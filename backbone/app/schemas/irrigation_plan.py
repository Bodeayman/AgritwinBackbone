from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, date
from app.schemas.ai_model import AIModelOut


class IrrigationPlanBase(BaseModel):
    field_id: int = Field(..., examples=[1])
    model_id: Optional[int] = Field(None, description="FK ID to ai_models entity", examples=[1])
    model_name: Optional[str] = Field(None, description="Name of the irrigation AI model", examples=["IrrigationSmartPlanner"])
    model_version: Optional[str] = Field(None, description="Version of the model", examples=["v1.1.0"])
    water_requirement: float = Field(..., gt=0, examples=[35.0])
    unit: str = Field("mm", max_length=50, examples=["mm"])
    recommended_date: date = Field(..., examples=["2026-08-10"])


class IrrigationPlanCreate(IrrigationPlanBase):
    pass


class IrrigationPlanOut(IrrigationPlanBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., examples=[1])
    ai_model: Optional[AIModelOut] = Field(None, description="Nested AIModel entity details")
    created_at: Optional[datetime] = Field(None, examples=["2026-08-08T14:00:00Z"])
