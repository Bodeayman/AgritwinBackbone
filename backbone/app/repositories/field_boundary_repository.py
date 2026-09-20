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

    def update_boundary_geometry(self, boundary_id: int, wkt: str) -> FieldBoundary:
        """Update only the geometry column via a direct SQL UPDATE.

        We expunge any cached ORM instance first so that SQLAlchemy does not
        flush stale attribute values (e.g. a None field_id) alongside the
        targeted UPDATE statement.
        """
        from sqlalchemy import update as sa_update

        # Expunge the stale instance from the identity map if present
        existing = self.db.get(FieldBoundary, boundary_id)
        if existing is not None:
            self.db.expunge(existing)

        stmt = (
            sa_update(FieldBoundary)
            .where(FieldBoundary.id == boundary_id)
            .values(boundary=wkt)
        )
        self.db.execute(stmt)
        self.db.commit()
        return self.db.get(FieldBoundary, boundary_id)
