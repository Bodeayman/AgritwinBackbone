from datetime import datetime
from sqlalchemy import String, DateTime, Float, ForeignKey, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class SatelliteObservation(Base):
    """Replaces the old satellite_data table.
    Each row is one satellite capture — never overwritten, historical records preserved.
    Processing status: 'pending', 'processing', 'processed', 'failed', 'ready'.
    References AIModel, Satellite, and Imagery entities.
    """
    __tablename__ = "satellite_observations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    satellite_id: Mapped[int | None] = mapped_column(ForeignKey("satellites.id", ondelete="SET NULL"), nullable=True)
    model_id: Mapped[int | None] = mapped_column(ForeignKey("ai_models.id", ondelete="SET NULL"), nullable=True)
    imagery_id: Mapped[int | None] = mapped_column(ForeignKey("imagery.id", ondelete="SET NULL"), nullable=True)
    observation_type: Mapped[str] = mapped_column(String(50), nullable=False, default="processed")
    cloud_cover_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    ndvi: Mapped[float | None] = mapped_column(Float, nullable=True)
    ndmi: Mapped[float | None] = mapped_column(Float, nullable=True)
    evi: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="processed")
    captured_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    additional_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    ai_model = relationship("AIModel", foreign_keys=[model_id])
    satellite = relationship("Satellite", back_populates="observations")
    imagery = relationship("Imagery")

    __table_args__ = (
        Index("ix_satellite_obs_field_captured", "field_id", "captured_at"),
        Index("ix_satellite_obs_satellite_captured", "satellite_id", "captured_at"),
    )

    def __repr__(self) -> str:
        return f"<SatelliteObservation(id={self.id}, field_id={self.field_id}, satellite_id={self.satellite_id}, status={self.status})>"
