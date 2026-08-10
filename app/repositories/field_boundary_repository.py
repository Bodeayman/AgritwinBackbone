from typing import Optional
from sqlalchemy import select, func, cast
from sqlalchemy.orm import Session
from geoalchemy2 import Geography
from geoalchemy2.shape import to_shape
from app.repositories.base import BaseRepository
from app.models.field_boundary import FieldBoundary


class FieldBoundaryRepository(BaseRepository[FieldBoundary]):
    def __init__(self, db: Session):
        super().__init__(FieldBoundary, db)

    def get_by_field_id(self, field_id: int) -> Optional[FieldBoundary]:
        """Return the boundary record for a given field, or None."""
        stmt = select(FieldBoundary).where(FieldBoundary.field_id == field_id)
        return self.db.scalars(stmt).first()

    def compute_hectares(self, boundary: FieldBoundary) -> float:
        """Compute area in hectares using PostGIS ST_Area on geography cast.
        1 hectare = 10 000 m².
        """
        stmt = select(
            func.ST_Area(cast(FieldBoundary.boundary, Geography))
        ).where(FieldBoundary.id == boundary.id)
        area_sqm = self.db.scalar(stmt)
        if area_sqm is None:
            return 0.0
        return float(area_sqm) / 10_000.0

    def get_coordinates(self, boundary: FieldBoundary):
        """Extract GeoJSON-style coordinates from the PostGIS geometry."""
        if boundary.boundary is None:
            return []
        try:
            shape = to_shape(boundary.boundary)
            return [[list(pt) for pt in shape.exterior.coords]]
        except Exception:
            return []
