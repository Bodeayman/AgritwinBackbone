from datetime import datetime, date
from sqlalchemy import String, DateTime, Date, Float, ForeignKey, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class YieldPrediction(Base):
    """ML-generated yield prediction for a field/crop.
    Multiple predictions are stored so historical comparisons are possible.
    Processing status: 'pending', 'processing', 'processed', 'failed', 'ready'.
    References AIModel metadata via model_id.
    """
    __tablename__ = "yield_predictions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    crop_cycle_id: Mapped[int | None] = mapped_column(ForeignKey("crop_cycles.id", ondelete="SET NULL"), nullable=True)
    model_id: Mapped[int | None] = mapped_column(ForeignKey("ai_models.id", ondelete="SET NULL"), nullable=True)
    crop_type: Mapped[str] = mapped_column(String(100), nullable=False)
    predicted_yield: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False, default="kg/ha")
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="processed")
    prediction_date: Mapped[date] = mapped_column(Date, nullable=False)
    input_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    input_data_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    ai_model = relationship("AIModel", foreign_keys=[model_id])
    crop_cycle = relationship("CropCycle", foreign_keys=[crop_cycle_id])

    __table_args__ = (
        Index("ix_yield_predictions_field_date", "field_id", "prediction_date"),
        Index("ix_yield_predictions_crop_cycle_date", "crop_cycle_id", "prediction_date"),
    )

    def __repr__(self) -> str:
        return (
            f"<YieldPrediction(id={self.id}, field_id={self.field_id}, "
            f"model_id={self.model_id}, status={self.status})>"
        )
