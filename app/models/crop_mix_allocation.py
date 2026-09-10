from sqlalchemy import String, Float, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class CropMixAllocation(Base):
    """A single crop field allocation within a CropMixRecommendation optimization plan.

    Example:
        CropMixRecommendation id=456
            → CropMixAllocation: Field "North Basin", Tomato, 40 feddans
            → CropMixAllocation: Field "East Basin", Wheat,  20 feddans
    """
    __tablename__ = "crop_mix_allocations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recommendation_id: Mapped[int] = mapped_column(
        ForeignKey("crop_mix_recommendations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    field_id: Mapped[int] = mapped_column(ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    crop_id: Mapped[int] = mapped_column(ForeignKey("crop_catalog.id", ondelete="CASCADE"), nullable=False)
    allocated_area_feddans: Mapped[float] = mapped_column(Float, nullable=False)
    expected_profit_contribution_egp: Mapped[float] = mapped_column(Float, nullable=False)

    # Back-reference to parent recommendation
    recommendation = relationship("CropMixRecommendation", back_populates="allocations")
    field = relationship("Field")
    crop = relationship("CropCatalog")

    __table_args__ = (
        CheckConstraint("allocated_area_feddans >= 0", name='check_allocation_area_non_negative'),
    )

    def __repr__(self) -> str:
        return (
            f"<CropMixAllocation(id={self.id}, recommendation_id={self.recommendation_id}, "
            f"field_id={self.field_id}, crop_id={self.crop_id}, allocated_area={self.allocated_area_feddans} feddans)>"
        )
