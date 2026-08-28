from datetime import datetime
from sqlalchemy import String, Date, Float, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class Satellite(Base):
    """
    Satellite platform entity representing remote sensing data sources.

    Stores metadata about satellite platforms that provide imagery and
    observation data for agricultural monitoring. Enables tracking of
    data sources and platform-specific characteristics.

    Attributes:
        id: Primary key, auto-incrementing integer.
        name: Unique satellite name (e.g., "Sentinel-2", "Landsat-8").
        operator: Organization operating the satellite (ESA, NASA, etc.).
        launch_date: Date when the satellite was launched.
        sensor_type: Type of sensor (optical, SAR, multispectral, etc.).
        resolution_m: Spatial resolution in meters (ground sample distance).
        revisit_period_days: Number of days between revisits to same location.
        status: Satellite status (active, retired, decommissioned).
        description: Optional description of the satellite platform.
        created_at: Timestamp when satellite record was created.

    Relationships:
        observations: Collection of SatelliteObservation entities from this satellite.

    Constraints:
        Unique constraint on name to prevent duplicate satellite entries.

    Indexes:
        name: Unique indexed for efficient lookup.
        ix_satellites_name_status: Composite index for active satellite queries.

    Usage:
        Satellites are registered via internal API endpoints. Satellite observations
        reference satellites by ID. The service layer can resolve satellite IDs
        by name for ingestion endpoints.
    """

    __tablename__ = "satellites"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    operator: Mapped[str | None] = mapped_column(String(100), nullable=True)
    launch_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    sensor_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    resolution_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    revisit_period_days: Mapped[int | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(Date, nullable=False, default=datetime.utcnow)

    # Relationships
    observations = relationship("SatelliteObservation", back_populates="satellite")

    __table_args__ = (
        Index("ix_satellites_name_status", "name", "status"),
    )

    def __repr__(self) -> str:
        return f"<Satellite(id={self.id}, name='{self.name}', operator='{self.operator}', status='{self.status}')>"
