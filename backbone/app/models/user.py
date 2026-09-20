from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class User(Base):
    """
    User account model for farmer authentication and authorization.

    Attributes:
        id: Primary key, auto-incrementing integer.
        email: Unique email address used for login and identification.
        hashed_password: Bcrypt-hashed password (never store plain text).
        is_active: Account status flag. Inactive accounts cannot authenticate.
        role: User role for authorization (e.g., "user", "admin").

    Relationships:
        Users are associated with farms and fields through foreign keys
        in those entities.

    Note:
        Passwords should be hashed using app.core.security.hash_password()
        and verified using app.core.security.verify_password().
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str] = mapped_column(String(50), default="user")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
