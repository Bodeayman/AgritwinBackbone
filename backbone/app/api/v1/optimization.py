from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from app.services.optimization_service import OptimizationService
from app.api.deps import get_optimization_service, get_farm_service

router = APIRouter()


class OptimizationRequest(BaseModel):
    farm_id: int = Field(..., examples=[1])
    season: str = Field("Winter", examples=["Winter"])
    zone: str = Field("Delta", examples=["Delta"])
    optimizer_version: str = Field("v4", examples=["v4"])


class OptimizationResponse(BaseModel):
    is_feasible: bool
    status: str
    total_land_used_feddans: float
    total_water_used_m3: float
    total_labor_used_hours: float
    total_fertilizer_used_kg: float
    total_expected_revenue_egp: float
    total_production_cost_egp: float
    total_labor_cost_egp: float
    total_fertilizer_cost_egp: float
    net_profit_egp: float
    allocations: list
    binding_constraints: list
    solver_status: str


@router.post("/run", response_model=OptimizationResponse,
            summary="Run crop mix optimizer")
def run_optimization(
    request: OptimizationRequest,
    opt_svc: OptimizationService = Depends(get_optimization_service),
    farm_svc = Depends(get_farm_service),
):
    """Execute Pyomo + HiGHS LP optimization for crop mix planning."""
    # Verify farm exists
    farm = farm_svc.get_farm(request.farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    try:
        result = opt_svc.run_optimization(
            farm_id=request.farm_id,
            season=request.season,
            zone=request.zone,
            optimizer_version=request.optimizer_version
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")