from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey, func, Float, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class Farm(Base):
    """
    Farm entity representing an agricultural organization or property.

    A farm is owned by a user and contains multiple fields for crop management,
    monitoring, and analysis. Farms serve as the top-level organizational unit
    in the AgriTwin system.

    Attributes:
        id: Primary key, auto-incrementing integer.
        owner_id: Foreign key to users.id. Owner of the farm.
        name: Human-readable farm name (max 100 characters).
        location: Optional geographic location description (address, region, etc.).
        created_at: Timestamp when the farm was created.
        updated_at: Timestamp when the farm was last modified.

    Relationships:
        owner: User who owns this farm (CASCADE delete on user deletion).
        fields: Collection of Field entities belonging to this farm.

    Cascade Behavior:
        Deleting a user cascades to delete all owned farms.
        Deleting a farm cascades to delete all associated fields.

    Indexes:
        owner_id: Indexed for efficient owner lookup.
    """

    __tablename__ = "farms"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # Crop Mix Business Planner fields
    zone: Mapped[str] = mapped_column(String(100), nullable=False, default="Delta")
    total_area_feddans: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    water_budget_m3: Mapped[float] = mapped_column(Float, nullable=False, default=500000.0)
    labor_budget_hours: Mapped[float] = mapped_column(Float, nullable=False, default=2500.0)
    fertilizer_budget_kg: Mapped[float] = mapped_column(Float, nullable=False, default=15000.0)
    labor_rate_egp_per_hour: Mapped[float] = mapped_column(Float, nullable=False, default=20.0)
    fertilizer_rate_egp_per_kg: Mapped[float] = mapped_column(Float, nullable=False, default=1.50)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    owner = relationship("User", backref="farms")

    __table_args__ = (
        CheckConstraint("zone IN ('Delta', 'Middle Egypt', 'Upper Egypt', 'Sinai / Reclaimed Lands')", name='check_farm_zone'),
        CheckConstraint("total_area_feddans > 0", name='check_farm_area_positive'),
        CheckConstraint("water_budget_m3 >= 0", name='check_water_budget_non_negative'),
        CheckConstraint("labor_budget_hours >= 0", name='check_labor_budget_non_negative'),
        CheckConstraint("fertilizer_budget_kg >= 0", name='check_fertilizer_budget_non_negative'),
    )

    def __repr__(self) -> str:
        return f"<Farm(id={self.id}, name={self.name}, owner_id={self.owner_id})>"
