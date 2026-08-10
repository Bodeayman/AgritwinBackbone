from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class CropMixAllocation(Base):
    """A single crop entry within a CropMixRecommendation optimization run.

    Example:
        CropMixRecommendation id=456
            → CropMixAllocation: Tomato, 40 ha
            → CropMixAllocation: Wheat,  20 ha
            → CropMixAllocation: Corn,   10 ha
    """
    __tablename__ = "crop_mix_allocations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recommendation_id: Mapped[int] = mapped_column(
        ForeignKey("crop_mix_recommendations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    crop_type: Mapped[str] = mapped_column(String(100), nullable=False)
    allocated_area: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False, default="ha")

    # Back-reference to parent recommendation
    recommendation = relationship("CropMixRecommendation", back_populates="allocations")

    def __repr__(self) -> str:
        return (
            f"<CropMixAllocation(id={self.id}, recommendation_id={self.recommendation_id}, "
            f"crop_type={self.crop_type}, allocated_area={self.allocated_area} {self.unit})>"
        )
