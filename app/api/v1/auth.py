from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.auth_service import AuthService
from app.api.deps import get_auth_service
from app.schemas.auth import UserCreate, UserLogin, Token
from pydantic import BaseModel, EmailStr, Field

router = APIRouter()

class UserResponse(BaseModel):
    id: int = Field(..., examples=[1])
    email: EmailStr = Field(..., examples=["user@example.com"])
    role: str = Field(..., examples=["user"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, auth_svc: AuthService = Depends(get_auth_service)):
    # Check if email already exists
    from app.models.user import User
    existing = auth_svc.db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    user = auth_svc.register_user(email=user_in.email, password=user_in.password)
    return UserResponse(id=user.id, email=user.email, role=user.role)

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, auth_svc: AuthService = Depends(get_auth_service)):
    user = auth_svc.authenticate_user(email=user_in.email, password=user_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth_svc.create_access_token(user)
    return Token(access_token=token, token_type="bearer")
