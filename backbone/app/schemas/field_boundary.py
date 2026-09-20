from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


class FieldBoundaryCreate(BaseModel):
    """GeoJSON polygon coordinates to set/replace a field's boundary."""
    coordinates: List[List[List[float]]] = Field(
        ...,
        description="GeoJSON polygon ring(s): [[[lon, lat], ...]]",
        examples=[
            [[
                [36.821, -1.292],
                [36.822, -1.292],
                [36.822, -1.293],
                [36.821, -1.293],
                [36.821, -1.292],
            ]]
        ],
    )


class FieldBoundaryUpdate(FieldBoundaryCreate):
    pass


class FieldBoundaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., examples=[1])
    field_id: int = Field(..., examples=[1])
    coordinates: List[List[List[float]]] = Field(
        ...,
        description="GeoJSON polygon coordinates extracted from PostGIS geometry",
        examples=[
            [[
                [36.821, -1.292],
                [36.822, -1.292],
                [36.822, -1.293],
                [36.821, -1.293],
                [36.821, -1.292],
            ]]
        ],
    )
    area_hectares: Optional[float] = Field(None, description="Computed polygon area in hectares", examples=[15.3])
    created_at: Optional[datetime] = Field(None, examples=["2026-08-08T12:00:00Z"])
    updated_at: Optional[datetime] = Field(None, examples=["2026-08-08T12:05:00Z"])
