from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class FarmBase(BaseModel):
    name: str = Field(..., max_length=100, examples=["Green Valley Farm"])
    location: Optional[str] = Field(None, max_length=255, examples=["Nairobi County, Kenya"])


class FarmCreate(FarmBase):
    """owner_id is NOT required in the request body — it is inferred from the JWT token."""
    pass


class FarmUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100, examples=["Sunset Ridge Farm"])
    location: Optional[str] = Field(None, max_length=255, examples=["Meru County, Kenya"])


class FarmOut(FarmBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., examples=[1])
    owner_id: int = Field(..., examples=[1])
    created_at: datetime = Field(..., examples=["2026-08-08T12:00:00Z"])
    updated_at: datetime = Field(..., examples=["2026-08-08T12:05:00Z"])
