from datetime import datetime
from sqlalchemy import String, DateTime, Float, ForeignKey, Boolean, ARRAY, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class CropCatalog(Base):
    """Crop catalog with EcoCrop rules and agronomic parameters.
    
    Contains crop information, market prices, cost structures, and soil tolerance bounds
    for use in crop mix optimization. Can be global (farm_id is NULL) or farm-specific.
    """
    __tablename__ = "crop_catalog"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    farm_id: Mapped[int | None] = mapped_column(ForeignKey("farms.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Crop identification
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    name_ar: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="General")
    
    # Agronomic parameters
    expected_yield_tons_per_feddan: Mapped[float] = mapped_column(Float, nullable=False)
    price_egp_per_ton: Mapped[float] = mapped_column(Float, nullable=False)
    production_cost_egp_per_feddan: Mapped[float] = mapped_column(Float, nullable=False)
    water_requirement_m3_per_feddan: Mapped[float] = mapped_column(Float, nullable=False)
    labor_requirement_hours_per_feddan: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    fertilizer_requirement_kg_per_feddan: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    
    # Soil tolerance bounds
    min_ph: Mapped[float] = mapped_column(Float, nullable=False, default=4.5)
    max_ph: Mapped[float] = mapped_column(Float, nullable=False, default=8.5)
    max_ec_ds_m: Mapped[float] = mapped_column(Float, nullable=False, default=3.5)
    suitable_textures: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=lambda: ["Loam", "Clay", "Silt", "Sandy", "Sandy Loam"])
    
    # Crop characteristics
    is_perennial: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    farm = relationship("Farm", backref="crop_catalog")

    __table_args__ = (
        CheckConstraint("expected_yield_tons_per_feddan > 0", name='check_crop_yield_positive'),
        CheckConstraint("price_egp_per_ton >= 0", name='check_crop_price_non_negative'),
        CheckConstraint("production_cost_egp_per_feddan >= 0", name='check_crop_cost_non_negative'),
        CheckConstraint("water_requirement_m3_per_feddan >= 0", name='check_crop_water_non_negative'),
        CheckConstraint("labor_requirement_hours_per_feddan >= 0", name='check_crop_labor_non_negative'),
        CheckConstraint("fertilizer_requirement_kg_per_feddan >= 0", name='check_crop_fertilizer_non_negative'),
        CheckConstraint("min_ph BETWEEN 0 AND 14", name='check_crop_min_ph_range'),
        CheckConstraint("max_ph BETWEEN 0 AND 14", name='check_crop_max_ph_range'),
        CheckConstraint("max_ec_ds_m >= 0", name='check_crop_max_ec_non_negative'),
        CheckConstraint("category IN ('Cereal', 'Vegetable', 'Legume', 'Fruit', 'Oilseed', 'Fiber', 'Forage', 'General')", name='check_crop_category'),
    )

    def __repr__(self) -> str:
        return f"<CropCatalog(id={self.id}, name_en={self.name_en}, name_ar={self.name_ar})>"