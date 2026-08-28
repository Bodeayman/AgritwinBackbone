from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class Field(Base):
    """
    Field entity representing a specific agricultural area within a farm.

    Fields are the primary unit for crop management, monitoring, and analysis.
    Each field has associated data including satellite observations, sensor readings,
    weather data, diagnoses, irrigation plans, and yield predictions.

    Attributes:
        id: Primary key, auto-incrementing integer.
        farm_id: Foreign key to farms.id. Farm this field belongs to.
        name: Human-readable field name (max 100 characters).
        created_at: Timestamp when the field was created.
        updated_at: Timestamp when the field was last modified.

    Relationships:
        farm: Farm this field belongs to (CASCADE delete on farm deletion).
        boundary: FieldBoundary with polygon geometry (PostGIS).
        crop_cycles: Collection of CropCycle entities for this field.

    Cascade Behavior:
        Deleting a farm cascades to delete all associated fields.
        Deleting a field cascades to delete all related data:
        - sensor_readings, weather, diagnoses, irrigation_plans
        - yield_predictions, crop_cycles, crop_mix_recommendations
        - satellite_observations, imagery

    Indexes:
        farm_id: Indexed for efficient farm lookup.

    Properties:
        current_crop: Returns the crop from the active 'growing' cycle, if any.
    """

    __tablename__ = "fields"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    farm = relationship("Farm", backref="fields")
    boundary = relationship("FieldBoundary", back_populates="field", uselist=False, passive_deletes=True)
    crop_cycles = relationship("CropCycle", back_populates="field")

    @property
    def current_crop(self) -> str | None:
        """
        Get the current crop from the active crop cycle.

        Returns:
            The crop name from the cycle with status 'growing', or None if no active cycle.

        Example:
            >>> field.current_crop
            'Maize'
        """
        active_cycle = next(
            (cycle for cycle in self.crop_cycles if cycle.status == 'growing'),
            None
        )
        return active_cycle.crop if active_cycle else None

    def __repr__(self) -> str:
        return f"<Field(id={self.id}, name={self.name}, farm_id={self.farm_id})>"
