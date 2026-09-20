from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime, date
from app.schemas.ai_model import AIModelOut


class InputDataSnapshot(BaseModel):
    """Snapshot of input data used for yield prediction"""
    soil_moisture: Optional[float] = Field(None, description="Soil moisture percentage", examples=[45.5])
    temperature: Optional[float] = Field(None, description="Temperature in Celsius", examples=[22.3])
    rainfall: Optional[float] = Field(None, description="Rainfall in mm", examples=[120.5])
    ndvi: Optional[float] = Field(None, description="Normalized Difference Vegetation Index", examples=[0.75])
    gndvi: Optional[float] = Field(None, description="Green Normalized Difference Vegetation Index", examples=[0.72])
    ndwi: Optional[float] = Field(None, description="Normalized Difference Water Index", examples=[0.32])
    savi: Optional[float] = Field(None, description="Soil Adjusted Vegetation Index", examples=[0.58])
    satellite_image: Optional[str] = Field(None, description="Path to satellite image used", examples=["fields/1/imagery/satellite_image.tif"])
    additional_inputs: Optional[Dict[str, Any]] = Field(None, description="Additional input data")


class YieldPredictionBase(BaseModel):
    field_id: int = Field(..., examples=[1])
    crop_cycle_id: Optional[int] = Field(None, description="FK ID to crop_cycles entity for precise tracking", examples=[1])
    model_id: Optional[int] = Field(None, description="FK ID to ai_models entity", examples=[1])
    model_name: Optional[str] = Field(None, description="Name of the AI model used", examples=["MaizeYieldPredictor"])
    model_version: Optional[str] = Field(None, description="Version of the AI model used", examples=["v2.1.0"])
    crop_type: str = Field(..., max_length=100, examples=["Maize"])
    predicted_yield: float = Field(..., gt=0, examples=[4200.0])
    unit: str = Field("kg/ha", max_length=50, examples=["kg/ha"])
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, examples=[0.87])
    status: str = Field("processed", description="ML processing status: 'pending', 'processing', 'processed', 'failed', 'ready'", examples=["processed"])
    prediction_date: date = Field(..., examples=["2026-08-08"])
    input_timestamp: datetime = Field(..., description="Timestamp of the input data used for prediction", examples=["2026-08-08T10:30:00Z"])
    input_data_snapshot: Optional[InputDataSnapshot] = Field(None, description="Snapshot of input data used for this prediction")


class YieldPredictionCreate(YieldPredictionBase):
    pass


class YieldPredictionOut(YieldPredictionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., examples=[1])
    ai_model: Optional[AIModelOut] = Field(None, description="Nested AIModel entity details")
    created_at: Optional[datetime] = Field(None, examples=["2026-08-08T15:00:00Z"])
