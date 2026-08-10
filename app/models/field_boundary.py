from datetime import datetime
from sqlalchemy import Integer, DateTime, ForeignKey, func, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry
from app.models.base import Base


class FieldBoundary(Base):
    __tablename__ = "field_boundaries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("fields.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    # PostGIS polygon stored in EPSG:4326
    boundary: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326, spatial_index=True), nullable=False
    )
    # Use client-side default so INSERT always sends a value (works in test
    # nested-savepoint sessions where server_default returns NULL on RETURNING).
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

    # Relationships
    field = relationship("Field", back_populates="boundary", passive_deletes=True)

    def __repr__(self) -> str:
        return f"<FieldBoundary(id={self.id}, field_id={self.field_id})>"
