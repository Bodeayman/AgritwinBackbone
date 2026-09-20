from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.irrigation_plan import IrrigationPlanCreate, IrrigationPlanOut
from app.services.irrigation_plan_service import IrrigationPlanService
from app.services.ai_model_service import AIModelService
from app.api.deps import get_irrigation_plan_service, get_ai_model_service

router = APIRouter()


@router.post("/", response_model=IrrigationPlanOut, status_code=status.HTTP_201_CREATED,
             summary="Create an irrigation plan")
def create(
    plan_in: IrrigationPlanCreate,
    svc: IrrigationPlanService = Depends(get_irrigation_plan_service),
    ai_model_svc: AIModelService = Depends(get_ai_model_service),
):
    """Store a new irrigation recommendation. Historical plans are preserved."""
    # Resolve model_id to ensure it exists in ai_models table
    plan_in.model_id = ai_model_svc.resolve_model_id(
        plan_in.model_id, plan_in.model_name, plan_in.model_version
    )
    return svc.create(plan_in)


@router.get("/{plan_id}", response_model=IrrigationPlanOut, summary="Get irrigation plan by ID")
def get(plan_id: int, svc: IrrigationPlanService = Depends(get_irrigation_plan_service)):
    obj = svc.get(plan_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Irrigation plan not found")
    return obj


@router.get("/field/{field_id}", response_model=list[IrrigationPlanOut],
            summary="List irrigation plans for a field")
def list_by_field(
    field_id: int,
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
    latest: bool = Query(False, description="If true, returns only the latest record"),
    skip: int = 0,
    limit: int = 100,
    svc: IrrigationPlanService = Depends(get_irrigation_plan_service),
):
    if latest:
        skip, limit = 0, 1
    return svc.list_by_field(field_id, from_date, to_date, skip=skip, limit=limit)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete plan")
def delete(plan_id: int, svc: IrrigationPlanService = Depends(get_irrigation_plan_service)):
    if not svc.delete(plan_id):
        raise HTTPException(status_code=404, detail="Irrigation plan not found")
    return None
