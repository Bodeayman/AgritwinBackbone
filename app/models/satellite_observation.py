from datetime import datetime
from sqlalchemy import String, DateTime, Float, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class SatelliteObservation(Base):
    """Replaces the old satellite_data table.
    Each row is one satellite capture — never overwritten, historical records preserved.
    Processing status: 'pending', 'processing', 'processed', 'failed', 'ready'.
    References AIModel metadata via model_id.
    """
    __tablename__ = "satellite_observations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    model_id: Mapped[int | None] = mapped_column(ForeignKey("ai_models.id", ondelete="SET NULL"), nullable=True)
    ndvi: Mapped[float | None] = mapped_column(Float, nullable=True)
    ndmi: Mapped[float | None] = mapped_column(Float, nullable=True)
    evi: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="processed")
    image_reference: Mapped[str | None] = mapped_column(String(512), nullable=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    ai_model = relationship("AIModel", foreign_keys=[model_id])

    __table_args__ = (
        Index("ix_satellite_obs_field_captured", "field_id", "captured_at"),
    )

    def __repr__(self) -> str:
        return f"<SatelliteObservation(id={self.id}, field_id={self.field_id}, model_id={self.model_id}, status={self.status})>"
