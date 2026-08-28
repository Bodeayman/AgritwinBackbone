from datetime import datetime
from sqlalchemy import String, Text, DateTime, Float, ForeignKey, Index, JSON, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class Diagnosis(Base):
    """Replaces disease_detections table.
    Multiple diagnoses per field; historical records are never overwritten.
    Processing status: 'pending', 'processing', 'processed', 'failed', 'ready'.
    References AIModel and Imagery entities.
    """
    __tablename__ = "diagnoses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    model_id: Mapped[int | None] = mapped_column(ForeignKey("ai_models.id", ondelete="SET NULL"), nullable=True)
    imagery_id: Mapped[int | None] = mapped_column(ForeignKey("imagery.id", ondelete="SET NULL"), nullable=True)
    crop_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    disease_or_pest: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="processed")
    diagnosed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    leaf_boundary_box: Mapped[list[int] | None] = mapped_column(JSON, nullable=True)
    detected_diseases: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    disease_confidences: Mapped[list[float] | None] = mapped_column(JSON, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    treatment_suggestion: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    ai_model = relationship("AIModel", foreign_keys=[model_id])
    imagery = relationship("Imagery")

    __table_args__ = (
        Index("ix_diagnoses_field_diagnosed", "field_id", "diagnosed_at"),
    )

    def __repr__(self) -> str:
        return f"<Diagnosis(id={self.id}, field_id={self.field_id}, model_id={self.model_id}, status={self.status})>"
