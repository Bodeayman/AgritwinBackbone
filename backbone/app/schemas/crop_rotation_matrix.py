from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class CropRotationMatrixBase(BaseModel):
    previous_crop_name: str = Field(..., examples=["Wheat"])
    candidate_crop_name: str = Field(..., examples=["Tomato"])
    suitability_score: int = Field(..., ge=0, le=1, examples=[1])
    agronomic_notes: Optional[str] = Field(None, examples=["Good rotation - different pest cycles"])


class CropRotationMatrixCreate(CropRotationMatrixBase):
    pass


class CropRotationMatrixOut(CropRotationMatrixBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., examples=[1])
    created_at: Optional[datetime] = Field(None, examples=["2024-09-07T10:00:00Z"])