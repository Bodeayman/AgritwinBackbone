from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, date
from app.schemas.ai_model import AIModelOut


class YieldPredictionBase(BaseModel):
    field_id: int = Field(..., examples=[1])
    model_id: Optional[int] = Field(None, description="FK ID to ai_models entity", examples=[1])
    model_name: Optional[str] = Field(None, description="Name of the AI model used", examples=["MaizeYieldPredictor"])
    model_version: Optional[str] = Field(None, max_length=50, examples=["v2.1.0"])
    crop_type: str = Field(..., max_length=100, examples=["Maize"])
    predicted_yield: float = Field(..., gt=0, examples=[4200.0])
    unit: str = Field("kg/ha", max_length=50, examples=["kg/ha"])
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, examples=[0.87])
    status: str = Field("processed", description="ML processing status: 'pending', 'processing', 'processed', 'failed', 'ready'", examples=["processed"])
    prediction_date: date = Field(..., examples=["2026-08-08"])


class YieldPredictionCreate(YieldPredictionBase):
    pass


class YieldPredictionOut(YieldPredictionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., examples=[1])
    ai_model: Optional[AIModelOut] = Field(None, description="Nested AIModel entity details")
    created_at: Optional[datetime] = Field(None, examples=["2026-08-08T15:00:00Z"])
