from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey, func
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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    owner = relationship("User", backref="farms")

    def __repr__(self) -> str:
        return f"<Farm(id={self.id}, name={self.name}, owner_id={self.owner_id})>"
