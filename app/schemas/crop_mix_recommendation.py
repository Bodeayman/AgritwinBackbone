from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from app.schemas.ai_model import AIModelOut


# ── Allocation (child) ────────────────────────────────────────────────────────

class CropMixAllocationBase(BaseModel):
    crop_type: str = Field(..., max_length=100, examples=["Tomato"])
    allocated_area: float = Field(..., gt=0, examples=[40.0])
    unit: str = Field("ha", max_length=50, examples=["ha"])


class CropMixAllocationCreate(CropMixAllocationBase):
    pass


class CropMixAllocationOut(CropMixAllocationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., examples=[1])
    recommendation_id: int = Field(..., examples=[1])


# ── Recommendation (parent) ───────────────────────────────────────────────────

class CropMixRecommendationBase(BaseModel):
    field_id: int = Field(..., examples=[1])
    model_id: Optional[int] = Field(None, description="FK ID to ai_models entity", examples=[1])
    model_name: Optional[str] = Field(None, description="Name of the optimization AI model", examples=["CropMix_LinearOptimizer"])
    model_version: Optional[str] = Field(None, description="Version of the model", examples=["v3.0.0"])
    expected_profit: Optional[float] = Field(None, examples=[125000.0])
    binding_constraint: Optional[str] = Field(
        None, max_length=255, examples=["Water availability"]
    )
    status: str = Field("processed", description="Optimization processing status: 'pending', 'processing', 'processed', 'failed', 'ready'", examples=["processed"])


class CropMixRecommendationCreate(CropMixRecommendationBase):
    allocations: List[CropMixAllocationCreate] = Field(
        ...,
        min_length=1,
        description="At least one crop allocation must be provided",
        examples=[
            [
                {"crop_type": "Tomato", "allocated_area": 40.0, "unit": "ha"},
                {"crop_type": "Wheat",  "allocated_area": 20.0, "unit": "ha"},
                {"crop_type": "Corn",   "allocated_area": 10.0, "unit": "ha"},
            ]
        ],
    )


class CropMixRecommendationOut(CropMixRecommendationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., examples=[1])
    ai_model: Optional[AIModelOut] = Field(None, description="Nested AIModel entity details")
    allocations: List[CropMixAllocationOut] = Field(default_factory=list)
    created_at: Optional[datetime] = Field(None, examples=["2026-08-08T16:00:00Z"])
