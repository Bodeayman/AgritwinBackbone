from passlib.context import CryptContext
from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.database import get_db
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.config import Settings, get_settings

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")

    def register_user(self, email: str, password: str) -> User:
        hashed = get_password_hash(password)
        user = User(email=email, hashed_password=hashed)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate_user(self, email: str, password: str) -> User | None:
        user: User = self.db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token(self, user: User, expires_delta: timedelta | None = None) -> str:
        data = {"sub": str(user.id), "role": user.role}
        return create_access_token(data, expires_delta)
