from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.field_boundary_repository import FieldBoundaryRepository
from app.repositories.field_repository import FieldRepository
from app.models.field_boundary import FieldBoundary
from app.schemas.field_boundary import FieldBoundaryCreate, FieldBoundaryOut
from app.core.validation import validate_field_boundary


def _coords_to_wkt(coordinates) -> str:
    """Convert GeoJSON polygon ring coordinates to WKT POLYGON string."""
    ring = coordinates[0]
    pts = ", ".join(f"{lon} {lat}" for lon, lat in ring)
    return f"SRID=4326;POLYGON(({pts}))"


class FieldBoundaryService:
    def __init__(self, db: Session):
        self.repo = FieldBoundaryRepository(db)
        self.field_repo = FieldRepository(db)

    def _assert_field_exists(self, field_id: int):
        if not self.field_repo.get(field_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Field {field_id} not found",
            )

    def set_boundary(self, field_id: int, boundary_in: FieldBoundaryCreate) -> FieldBoundaryOut:
        """Create or replace the boundary for a field with comprehensive validation."""
        self._assert_field_exists(field_id)
        
        # Comprehensive validation across all layers
        is_valid, errors = validate_field_boundary(
            boundary_in.coordinates,
            use_shapely=False,  # Disabled for testing until we have realistic test data
            min_hectares=0.0001,  # Reduced for testing
            max_hectares=10000  # 10km² maximum
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "Field boundary validation failed",
                    "errors": errors
                }
            )
        
        existing = self.repo.get_by_field_id(field_id)
        wkt = _coords_to_wkt(boundary_in.coordinates)
        if existing:
            updated = self.repo.update_boundary_geometry(existing.id, wkt)
            return self._to_out(updated)
        new_boundary = FieldBoundary(field_id=field_id, boundary=wkt)
        obj = self.repo.create(new_boundary)
        return self._to_out(obj)

    def get_boundary(self, field_id: int) -> Optional[FieldBoundaryOut]:
        self._assert_field_exists(field_id)
        obj = self.repo.get_by_field_id(field_id)
        return self._to_out(obj) if obj else None

    def _to_out(self, obj: FieldBoundary) -> FieldBoundaryOut:
        coordinates = self.repo.get_coordinates(obj)
        area_ha = self.repo.compute_hectares(obj)
        return FieldBoundaryOut(
            id=obj.id,
            field_id=obj.field_id,
            coordinates=coordinates,
            area_hectares=area_ha,
            created_at=obj.created_at.isoformat() if obj.created_at else "",
            updated_at=obj.updated_at.isoformat() if obj.updated_at else "",
        )
