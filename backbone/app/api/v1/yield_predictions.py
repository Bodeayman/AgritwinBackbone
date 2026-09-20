from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.yield_prediction import YieldPredictionCreate, YieldPredictionOut
from app.services.yield_prediction_service import YieldPredictionService
from app.services.ai_model_service import AIModelService
from app.api.deps import get_yield_prediction_service, get_ai_model_service

router = APIRouter()


@router.post("/", response_model=YieldPredictionOut, status_code=status.HTTP_201_CREATED,
             summary="Create a yield prediction")
def create(
    pred_in: YieldPredictionCreate,
    svc: YieldPredictionService = Depends(get_yield_prediction_service),
    ai_model_svc: AIModelService = Depends(get_ai_model_service),
):
    """Store a new yield prediction. Multiple predictions per field are preserved historically."""
    # Resolve model_id to ensure it exists in ai_models table
    pred_in.model_id = ai_model_svc.resolve_model_id(
        pred_in.model_id, pred_in.model_name, pred_in.model_version
    )
    return svc.create(pred_in)


@router.get("/{pred_id}", response_model=YieldPredictionOut, summary="Get prediction by ID")
def get(pred_id: int, svc: YieldPredictionService = Depends(get_yield_prediction_service)):
    obj = svc.get(pred_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Yield prediction not found")
    return obj


@router.get("/field/{field_id}", response_model=list[YieldPredictionOut],
            summary="List yield predictions for a field")
def list_by_field(
    field_id: int,
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
    latest: bool = Query(False, description="If true, returns only the latest record"),
    skip: int = 0,
    limit: int = 100,
    svc: YieldPredictionService = Depends(get_yield_prediction_service),
):
    if latest:
        skip, limit = 0, 1
    return svc.list_by_field(field_id, from_date, to_date, skip=skip, limit=limit)


@router.delete("/{pred_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete prediction")
def delete(pred_id: int, svc: YieldPredictionService = Depends(get_yield_prediction_service)):
    if not svc.delete(pred_id):
        raise HTTPException(status_code=404, detail="Yield prediction not found")
    return None
