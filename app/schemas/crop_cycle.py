from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime

class CropCycleBase(BaseModel):
    field_id: int = Field(..., examples=[1])
    crop: str = Field(..., max_length=100, examples=["Corn (Sweet)"])
    planting_date: date = Field(..., description="Date of planting", examples=["2026-04-15"])
    expected_harvest_date: date = Field(..., description="Projected harvest date", examples=["2026-09-15"])
    actual_harvest_date: date | None = Field(None, description="Actual harvest date when known", examples=["2026-09-12"])
    status: str = Field("growing", max_length=20, description="Current cycle status", examples=["growing"])

class CropCycleCreate(CropCycleBase):
    pass

class CropCycleUpdate(BaseModel):
    crop: str | None = Field(None, examples=["Wheat (Durum)"])
    planting_date: date | None = Field(None, examples=["2026-05-01"])
    expected_harvest_date: date | None = Field(None, examples=["2026-10-01"])
    actual_harvest_date: date | None = Field(None, examples=["2026-09-28"])
    status: str | None = Field(None, examples=["harvested"])

class CropCycleOut(CropCycleBase):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., examples=[1])
    created_at: datetime = Field(..., examples=["2026-08-08T12:00:00Z"])
    updated_at: datetime = Field(..., examples=["2026-08-08T12:05:00Z"])
