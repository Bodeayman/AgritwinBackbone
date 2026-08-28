from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class WeatherBase(BaseModel):
    field_id: int = Field(..., examples=[1])
    temperature: Optional[float] = Field(None, examples=[22.5])
    humidity: Optional[float] = Field(None, examples=[55.0])
    rainfall: Optional[float] = Field(None, examples=[0.0])
    forecast_rain: Optional[float] = Field(None, examples=[10.5])
    pressure: Optional[float] = Field(None, description="Atmospheric pressure in hPa", examples=[1013.2])
    recorded_at: Optional[datetime] = Field(None, examples=["2026-08-08T12:00:00Z"])

class WeatherCreate(WeatherBase):
    pass

class WeatherOut(WeatherBase):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., examples=[1])
