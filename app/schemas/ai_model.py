from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class AIModelBase(BaseModel):
    name: str = Field(..., max_length=100, examples=["ResNet50_CropDisease"])
    version: str = Field(..., max_length=50, examples=["v1.2.0"])
    description: Optional[str] = Field(None, examples=["ResNet50 model fine-tuned for corn/wheat leaf diseases."])


class AIModelCreate(AIModelBase):
    pass


class AIModelOut(AIModelBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., examples=[1])
    created_at: Optional[datetime] = Field(None, examples=["2026-08-09T10:00:00Z"])
