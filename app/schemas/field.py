from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class FieldBase(BaseModel):
    farm_id: int = Field(..., examples=[1])
    name: str = Field(..., max_length=100, examples=["North Barley Field"])
    crop_type: Optional[str] = Field(None, max_length=100, examples=["Barley"])


class FieldCreate(FieldBase):
    pass


class FieldUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100, examples=["East Wheat Field"])
    crop_type: Optional[str] = Field(None, max_length=100, examples=["Wheat"])


class FieldOut(FieldBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., examples=[1])
    created_at: datetime = Field(..., examples=["2026-08-08T12:00:00Z"])
    updated_at: datetime = Field(..., examples=["2026-08-08T12:05:00Z"])
