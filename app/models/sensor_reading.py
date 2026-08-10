from datetime import datetime
from sqlalchemy import String, DateTime, Float, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    sensor_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    soil_moisture: Mapped[float | None] = mapped_column(Float, nullable=True)
    soil_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    air_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    humidity: Mapped[float | None] = mapped_column(Float, nullable=True)
    soil_ph: Mapped[float | None] = mapped_column(Float, nullable=True)
    electrical_conductivity: Mapped[float | None] = mapped_column(Float, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_sensor_readings_field_recorded", "field_id", "recorded_at"),
    )

    def __repr__(self) -> str:
        return f"<SensorReading(id={self.id}, field_id={self.field_id}, recorded_at={self.recorded_at})>"
