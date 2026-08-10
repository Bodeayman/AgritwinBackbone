from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from app.schemas.ai_model import AIModelOut


class SatelliteObservationBase(BaseModel):
    field_id: int = Field(..., examples=[1])
    model_id: Optional[int] = Field(None, description="FK ID to ai_models entity", examples=[1])
    model_name: Optional[str] = Field(None, description="Name of the satellite analysis model", examples=["Sentinel2_Vegetation_Extractor"])
    model_version: Optional[str] = Field(None, description="Version of the model", examples=["v1.0.0"])
    ndvi: Optional[float] = Field(None, description="Normalized Difference Vegetation Index", examples=[0.72])
    ndmi: Optional[float] = Field(None, description="Normalized Difference Moisture Index", examples=[0.45])
    evi: Optional[float] = Field(None, description="Enhanced Vegetation Index", examples=[0.58])
    status: str = Field("processed", description="Satellite processing status: 'pending', 'processing', 'processed', 'failed', 'ready'", examples=["processed"])
    image_reference: Optional[str] = Field(
        None,
        description="Relative path to the stored satellite image file",
        examples=["fields/1/sat_20260808_143012_a3f9.tif"],
    )
    captured_at: datetime = Field(..., examples=["2026-08-08T08:30:00Z"])


class SatelliteObservationCreate(SatelliteObservationBase):
    pass


class SatelliteObservationOut(SatelliteObservationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., examples=[1])
    ai_model: Optional[AIModelOut] = Field(None, description="Nested AIModel entity details")
    created_at: Optional[datetime] = Field(None, examples=["2026-08-08T08:30:01Z"])
