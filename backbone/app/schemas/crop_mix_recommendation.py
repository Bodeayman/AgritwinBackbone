from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.schemas.ai_model import AIModelOut


# ── Allocation (child) ────────────────────────────────────────────────────────

class CropMixAllocationBase(BaseModel):
    field_id: int = Field(..., examples=[1])
    crop_id: int = Field(..., examples=[1])
    allocated_area_feddans: float = Field(..., ge=0, examples=[100.0])
    expected_profit_contribution_egp: float = Field(..., examples=[9985000.0])


class CropMixAllocationCreate(CropMixAllocationBase):
    pass


class CropMixAllocationOut(CropMixAllocationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., examples=[1])
    recommendation_id: int = Field(..., examples=[1])


# ── Recommendation (parent) ───────────────────────────────────────────────────

class CropMixRecommendationBase(BaseModel):
    farm_id: int = Field(..., examples=[1])
    model_id: Optional[int] = Field(None, description="FK ID to ai_models entity", examples=[1])
    model_name: Optional[str] = Field(None, description="Name of the optimization AI model", examples=["CropMix_LinearOptimizer"])
    model_version: Optional[str] = Field(None, description="Version of the model", examples=["v4.0.0"])
    season: str = Field("Winter", examples=["Winter"])
    optimizer_version: str = Field("v4", examples=["v4"])
    status: str = Field("processed", description="Optimization processing status: 'pending', 'processing', 'processed', 'failed', 'ready'", examples=["processed"])
    is_feasible: bool = Field(True, examples=[True])
    total_land_used_feddans: float = Field(..., examples=[160.0])
    total_water_used_m3: float = Field(..., examples=[500000.0])
    total_labor_used_hours: float = Field(..., examples=[2500.0])
    total_fertilizer_used_kg: float = Field(..., examples=[18000.0])
    total_expected_revenue_egp: float = Field(..., examples=[125000000.0])
    total_production_cost_egp: float = Field(..., examples=[6231500.0])
    total_labor_cost_egp: float = Field(..., examples=[50000.0])
    total_fertilizer_cost_egp: float = Field(..., examples=[27000.0])
    net_profit_egp: float = Field(..., examples=[118691500.0])
    binding_constraints: Optional[Dict[str, Any]] = Field(None, examples=[{"water": "Water budget binding"}])
    ai_synthesis_explanation: Optional[str] = Field(None, examples=["Optimal allocation achieved with 95% land utilization"])


class CropMixRecommendationCreate(CropMixRecommendationBase):
    allocations: List[CropMixAllocationCreate] = Field(
        ...,
        min_length=1,
        description="At least one crop allocation must be provided",
        examples=[
            [
                {"field_id": 1, "crop_id": 1, "allocated_area_feddans": 100.0, "expected_profit_contribution_egp": 9985000.0},
                {"field_id": 2, "crop_id": 2, "allocated_area_feddans": 60.0, "expected_profit_contribution_egp": 118768500.0},
            ]
        ],
    )


class CropMixRecommendationOut(CropMixRecommendationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., examples=[1])
    ai_model: Optional[AIModelOut] = Field(None, description="Nested AIModel entity details")
    allocations: List[CropMixAllocationOut] = Field(default_factory=list)
    created_at: Optional[datetime] = Field(None, examples=["2024-09-07T10:00:00Z"])
