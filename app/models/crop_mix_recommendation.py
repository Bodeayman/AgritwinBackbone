from datetime import datetime
from sqlalchemy import String, DateTime, Float, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class CropMixRecommendation(Base):
    """One optimization run result for a field.
    Contains expected profit and binding constraint; the individual crop allocations
    live in the CropMixAllocation child table.
    Processing status: 'pending', 'processing', 'processed', 'failed', 'ready'.
    References AIModel metadata via model_id.
    """
    __tablename__ = "crop_mix_recommendations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    model_id: Mapped[int | None] = mapped_column(ForeignKey("ai_models.id", ondelete="SET NULL"), nullable=True)
    expected_profit: Mapped[float | None] = mapped_column(Float, nullable=True)
    binding_constraint: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="processed")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    ai_model = relationship("AIModel", foreign_keys=[model_id])

    # One recommendation → many allocations
    allocations = relationship(
        "CropMixAllocation",
        back_populates="recommendation",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_crop_mix_recs_field", "field_id"),
    )

    def __repr__(self) -> str:
        return f"<CropMixRecommendation(id={self.id}, field_id={self.field_id}, model_id={self.model_id}, status={self.status})>"
