from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class DiseaseDetectionBase(BaseModel):
    field_id: int = Field(..., examples=[1])
    image_url: str = Field(..., examples=["https://storage.agritwin.local/disease-images/field_1_leaf.jpg"])
    disease_name: str = Field(..., examples=["Rust Disease"])
    severity: Optional[float] = Field(None, examples=[0.45])
    confidence: Optional[float] = Field(None, examples=[0.92])
    created_at: Optional[datetime] = Field(None, examples=["2026-08-08T12:00:00Z"])

class DiseaseDetectionCreate(DiseaseDetectionBase):
    pass

class DiseaseDetectionOut(DiseaseDetectionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., examples=[1])
