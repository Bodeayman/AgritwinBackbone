from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Float, DateTime, ForeignKey
from datetime import datetime
from app.models.base import Base

class DiseaseDetection(Base):
    __tablename__ = "disease_detections"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    image_url: Mapped[str] = mapped_column(String, nullable=False)
    disease_name: Mapped[str] = mapped_column(String, nullable=False)
    severity: Mapped[float] = mapped_column(Float, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
