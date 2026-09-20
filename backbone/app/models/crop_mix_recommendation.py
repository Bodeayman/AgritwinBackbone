from datetime import datetime
from sqlalchemy import String, DateTime, Float, ForeignKey, Index, Boolean, JSON, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class CropMixRecommendation(Base):
    """Optimization plan result for a farm.
    
    Contains overall financial performance, constraint information, and binding constraints.
    The individual field-by-field crop allocations live in the CropMixAllocation child table.
    Processing status: 'pending', 'processing', 'processed', 'failed', 'ready'.
    """
    __tablename__ = "crop_mix_recommendations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    model_id: Mapped[int | None] = mapped_column(ForeignKey("ai_models.id", ondelete="SET NULL"), nullable=True)
    
    # Optimization metadata
    season: Mapped[str] = mapped_column(String(50), nullable=False, default="Winter")
    optimizer_version: Mapped[str] = mapped_column(String(20), nullable=False, default="v4")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="processed")
    is_feasible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # Resource usage
    total_land_used_feddans: Mapped[float] = mapped_column(Float, nullable=False)
    total_water_used_m3: Mapped[float] = mapped_column(Float, nullable=False)
    total_labor_used_hours: Mapped[float] = mapped_column(Float, nullable=False)
    total_fertilizer_used_kg: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Financial calculations
    total_expected_revenue_egp: Mapped[float] = mapped_column(Float, nullable=False)
    total_production_cost_egp: Mapped[float] = mapped_column(Float, nullable=False)
    total_labor_cost_egp: Mapped[float] = mapped_column(Float, nullable=False)
    total_fertilizer_cost_egp: Mapped[float] = mapped_column(Float, nullable=False)
    net_profit_egp: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Constraint information
    binding_constraints: Mapped[dict] = mapped_column(JSON, nullable=True)
    ai_synthesis_explanation: Mapped[str] = mapped_column(String(1000), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    ai_model = relationship("AIModel", foreign_keys=[model_id])
    farm = relationship("Farm", backref="crop_mix_recommendations")

    # One recommendation → many allocations
    allocations = relationship(
        "CropMixAllocation",
        back_populates="recommendation",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_crop_mix_recs_farm", "farm_id"),
        Index("ix_crop_mix_recs_season", "season"),
        CheckConstraint("season IN ('Winter', 'Summer', 'Nili', 'Perennial')", name='check_rec_season'),
        CheckConstraint("total_land_used_feddans >= 0", name='check_rec_land_non_negative'),
        CheckConstraint("total_water_used_m3 >= 0", name='check_rec_water_non_negative'),
        CheckConstraint("total_labor_used_hours >= 0", name='check_rec_labor_non_negative'),
        CheckConstraint("total_fertilizer_used_kg >= 0", name='check_rec_fertilizer_non_negative'),
    )

    def __repr__(self) -> str:
        return f"<CropMixRecommendation(id={self.id}, farm_id={self.farm_id}, season={self.season}, status={self.status})>"
