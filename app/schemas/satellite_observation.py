from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from app.schemas.ai_model import AIModelOut
from app.schemas.satellite import SatelliteOut
from app.schemas.imagery import ImageryOut


class SatelliteObservationBase(BaseModel):
    field_id: int = Field(..., examples=[1])
    satellite_id: Optional[int] = Field(None, description="FK ID to satellites entity", examples=[1])
    satellite_name: Optional[str] = Field(None, description="Name of the satellite platform (auto-creates if doesn't exist)", examples=["Sentinel-2A"])
    model_id: Optional[int] = Field(None, description="FK ID to ai_models entity", examples=[1])
    model_name: Optional[str] = Field(None, description="Name of the satellite analysis model", examples=["Sentinel2_Vegetation_Extractor"])
    model_version: Optional[str] = Field(None, description="Version of the model", examples=["v1.0.0"])
    imagery_id: Optional[int] = Field(None, description="FK ID to imagery entity", examples=[1])
    observation_type: str = Field("processed", description="Type of observation: 'raw', 'processed', 'analyzed'", examples=["processed"])
    cloud_cover_pct: Optional[float] = Field(None, description="Cloud coverage percentage", examples=[15.5])
    ndvi: Optional[float] = Field(None, description="Normalized Difference Vegetation Index", examples=[0.72])
    ndmi: Optional[float] = Field(None, description="Normalized Difference Moisture Index", examples=[0.45])
    evi: Optional[float] = Field(None, description="Enhanced Vegetation Index", examples=[0.58])
    status: str = Field("processed", description="Satellite processing status: 'pending', 'processing', 'processed', 'failed', 'ready'", examples=["processed"])
    captured_at: datetime = Field(..., examples=["2026-08-08T08:30:00Z"])
    additional_metadata: Optional[Dict[str, Any]] = Field(None, description="Platform-specific metadata", examples=[{"sun_azimuth": 45.3, "sun_elevation": 30.1}])


class SatelliteObservationCreate(SatelliteObservationBase):
    pass


class SatelliteObservationOut(SatelliteObservationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., examples=[1])
    ai_model: Optional[AIModelOut] = Field(None, description="Nested AIModel entity details")
    satellite: Optional[SatelliteOut] = Field(None, description="Nested Satellite entity details")
    imagery: Optional[ImageryOut] = Field(None, description="Nested Imagery entity details")
    created_at: Optional[datetime] = Field(None, examples=["2026-08-08T08:30:01Z"])
