from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class SensorReadingBase(BaseModel):
    field_id: int = Field(..., examples=[1])
    sensor_id: Optional[str] = Field(None, max_length=100, examples=["SENSOR-N-001"])
    soil_moisture: Optional[float] = Field(None, examples=[32.4])
    soil_temperature: Optional[float] = Field(None, examples=[18.5])
    air_temperature: Optional[float] = Field(None, examples=[24.2])
    humidity: Optional[float] = Field(None, examples=[60.0])
    soil_ph: Optional[float] = Field(None, examples=[6.8])
    electrical_conductivity: Optional[float] = Field(None, examples=[1.2])
    recorded_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow, examples=["2026-08-08T10:00:00Z"]
    )


class SensorCreate(SensorReadingBase):
    pass


class SensorOut(SensorReadingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., examples=[1])
    created_at: Optional[datetime] = Field(None, examples=["2026-08-08T10:00:01Z"])
