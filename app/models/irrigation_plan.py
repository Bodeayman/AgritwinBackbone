from datetime import datetime, date
from sqlalchemy import String, DateTime, Date, Float, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class IrrigationPlan(Base):
    """Irrigation recommendation for a field.
    Historical plans are preserved; never overwritten.
    References AIModel metadata via model_id.
    """
    __tablename__ = "irrigation_plans"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    model_id: Mapped[int | None] = mapped_column(ForeignKey("ai_models.id", ondelete="SET NULL"), nullable=True)
    water_requirement: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False, default="mm")
    recommended_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    ai_model = relationship("AIModel", foreign_keys=[model_id])

    __table_args__ = (
        Index("ix_irrigation_plans_field_date", "field_id", "recommended_date"),
    )

    def __repr__(self) -> str:
        return f"<IrrigationPlan(id={self.id}, field_id={self.field_id}, model_id={self.model_id})>"
