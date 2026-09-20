from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any
from datetime import datetime, date


class SatelliteObservationSummary(BaseModel):
    """Minimal satellite observation summary for Satellite schema."""
    id: int = Field(..., examples=[1])
    field_id: int = Field(..., examples=[1])
    ndvi: Optional[float] = Field(None, examples=[0.78])
    captured_at: datetime = Field(..., examples=["2026-08-08T08:30:00Z"])
    status: str = Field(..., examples=["processed"])


class SatelliteBase(BaseModel):
    name: str = Field(..., examples=["Sentinel-2A"])
    operator: Optional[str] = Field(None, examples=["ESA"])
    launch_date: Optional[date] = Field(None, examples=["2015-06-23"])
    sensor_type: Optional[str] = Field(None, examples=["Multispectral"])
    resolution_m: Optional[float] = Field(None, examples=[10.0])
    revisit_period_days: Optional[int] = Field(None, examples=[5])
    status: str = Field("active", examples=["active", "decommissioned"])
    description: Optional[str] = Field(None, examples=["Copernicus Sentinel-2 mission"])


class SatelliteCreate(SatelliteBase):
    pass


class SatelliteUpdate(BaseModel):
    name: Optional[str] = Field(None, examples=["Sentinel-2A"])
    operator: Optional[str] = Field(None, examples=["ESA"])
    launch_date: Optional[date] = Field(None, examples=["2015-06-23"])
    sensor_type: Optional[str] = Field(None, examples=["Multispectral"])
    resolution_m: Optional[float] = Field(None, examples=[10.0])
    revisit_period_days: Optional[int] = Field(None, examples=[5])
    status: Optional[str] = Field(None, examples=["active", "decommissioned"])
    description: Optional[str] = Field(None, examples=["Copernicus Sentinel-2 mission"])


class SatelliteOut(SatelliteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., examples=[1])
    created_at: Optional[datetime] = Field(None, examples=["2026-08-01T00:00:00Z"])
    # observations: List[Any] = Field(default_factory=list, description="List of satellite observations from this platform")
