from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class CropCatalogBase(BaseModel):
    name_en: str = Field(..., examples=["Wheat"])
    name_ar: str = Field(..., examples=["قمح"])
    category: str = Field("General", examples=["Cereal"])
    expected_yield_tons_per_feddan: float = Field(..., gt=0, examples=[2.5])
    price_egp_per_ton: float = Field(..., ge=0, examples=[12500.0])
    production_cost_egp_per_feddan: float = Field(..., ge=0, examples=[8500.0])
    water_requirement_m3_per_feddan: float = Field(..., ge=0, examples=[1890.95])
    labor_requirement_hours_per_feddan: float = Field(0.0, ge=0, examples=[20.0])
    fertilizer_requirement_kg_per_feddan: float = Field(0.0, ge=0, examples=[100.0])
    min_ph: float = Field(4.5, ge=0, le=14, examples=[4.5])
    max_ph: float = Field(8.5, ge=0, le=14, examples=[8.5])
    max_ec_ds_m: float = Field(3.5, ge=0, examples=[3.5])
    suitable_textures: List[str] = Field(default=["Loam", "Clay", "Silt", "Sandy", "Sandy Loam"], examples=[["Loam", "Clay"]])
    is_perennial: bool = Field(False, examples=[False])


class CropCatalogCreate(CropCatalogBase):
    farm_id: Optional[int] = Field(None, examples=[1])


class CropCatalogOut(CropCatalogBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., examples=[1])
    farm_id: Optional[int] = Field(None, examples=[1])
    created_at: Optional[datetime] = Field(None, examples=["2024-09-07T10:00:00Z"])