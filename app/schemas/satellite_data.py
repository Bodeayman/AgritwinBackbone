from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class SatelliteBase(BaseModel):
    field_id: int = Field(..., examples=[1])
    ndvi: Optional[float] = Field(None, examples=[0.72])
    ndmi: Optional[float] = Field(None, examples=[0.45])
    captured_at: Optional[datetime] = Field(None, examples=["2026-08-08T12:00:00Z"])

class SatelliteCreate(SatelliteBase):
    pass

class SatelliteOut(SatelliteBase):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., examples=[1])
