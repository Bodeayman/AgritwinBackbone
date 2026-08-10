from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr = Field(..., examples=["user@example.com"])
    password: str = Field(..., min_length=6, examples=["securepassword123"])

class UserLogin(BaseModel):
    email: EmailStr = Field(..., examples=["user@example.com"])
    password: str = Field(..., examples=["securepassword123"])

class Token(BaseModel):
    access_token: str = Field(..., examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6InVzZXIiLCJleHAiOjE3ODk1NjU2MDB9..."])
    token_type: str = Field("bearer", examples=["bearer"])

class TokenData(BaseModel):
    user_id: int | None = Field(None, examples=[1])
    role: str | None = Field(None, examples=["user"])
    exp: datetime | None = Field(None, examples=["2026-08-08T13:00:00Z"])
