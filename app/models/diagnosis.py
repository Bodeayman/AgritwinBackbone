from datetime import datetime
from sqlalchemy import String, Text, DateTime, Float, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class Diagnosis(Base):
    """Replaces disease_detections table.
    Multiple diagnoses per field; historical records are never overwritten.
    Processing status: 'pending', 'processing', 'processed', 'failed', 'ready'.
    References AIModel metadata via model_id.
    """
    __tablename__ = "diagnoses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    model_id: Mapped[int | None] = mapped_column(ForeignKey("ai_models.id", ondelete="SET NULL"), nullable=True)
    image_reference: Mapped[str | None] = mapped_column(String(512), nullable=True)
    crop_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    disease_or_pest: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="processed")
    diagnosed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    treatment_suggestion: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    ai_model = relationship("AIModel", foreign_keys=[model_id])

    __table_args__ = (
        Index("ix_diagnoses_field_diagnosed", "field_id", "diagnosed_at"),
    )

    def __repr__(self) -> str:
        return f"<Diagnosis(id={self.id}, field_id={self.field_id}, model_id={self.model_id}, status={self.status})>"
