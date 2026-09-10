from datetime import datetime
from sqlalchemy import String, DateTime, Integer, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class CropRotationMatrix(Base):
    """Crop rotation suitability matrix.
    
    Maps previous crop to candidate next crop suitability (0 or 1).
    This is the agronomic source of truth for allowable crop sequences.
    """
    __tablename__ = "crop_rotation_matrix"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    previous_crop_name: Mapped[str] = mapped_column(String(100), nullable=False)
    candidate_crop_name: Mapped[str] = mapped_column(String(100), nullable=False)
    suitability_score: Mapped[int] = mapped_column(Integer, nullable=False)
    agronomic_notes: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("suitability_score IN (0, 1)", name='check_rotation_score_binary'),
    )

    def __repr__(self) -> str:
        return f"<CropRotationMatrix(id={self.id}, previous={self.previous_crop_name}, candidate={self.candidate_crop_name}, score={self.suitability_score})>"