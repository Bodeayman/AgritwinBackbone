from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.crop_mix_recommendation import CropMixRecommendationCreate, CropMixRecommendationOut
from app.services.crop_mix_service import CropMixService
from app.services.ai_model_service import AIModelService
from app.api.deps import get_crop_mix_service, get_ai_model_service

router = APIRouter()


@router.post("/", response_model=CropMixRecommendationOut, status_code=status.HTTP_201_CREATED,
             summary="Create optimization plan")
def create(
    rec_in: CropMixRecommendationCreate,
    svc: CropMixService = Depends(get_crop_mix_service),
    ai_model_svc: AIModelService = Depends(get_ai_model_service),
):
    """Store a new optimization plan with all field allocations in one request."""
    # Resolve model_id to ensure it exists in ai_models table
    rec_in.model_id = ai_model_svc.resolve_model_id(
        rec_in.model_id, rec_in.model_name, rec_in.model_version
    )
    return svc.create(rec_in)


@router.get("/{rec_id}", response_model=CropMixRecommendationOut,
            summary="Get optimization plan by ID")
def get(rec_id: int, svc: CropMixService = Depends(get_crop_mix_service)):
    obj = svc.get(rec_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Optimization plan not found")
    return obj


@router.get("/farm/{farm_id}", response_model=list[CropMixRecommendationOut],
            summary="List optimization plans for farm")
def list_by_farm(
    farm_id: int,
    latest: bool = Query(False, description="If true, returns only the latest record"),
    skip: int = 0,
    limit: int = 100,
    svc: CropMixService = Depends(get_crop_mix_service),
):
    if latest:
        skip, limit = 0, 1
    return svc.list_by_farm(farm_id, skip=skip, limit=limit)


@router.get("/farm/{farm_id}/latest", response_model=Optional[CropMixRecommendationOut],
            summary="Get latest optimization plan for farm")
def get_latest(farm_id: int, svc: CropMixService = Depends(get_crop_mix_service)):
    """Return the most recent optimization plan for a given farm."""
    return svc.get_latest_by_farm(farm_id)


@router.delete("/{rec_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete optimization plan")
def delete(rec_id: int, svc: CropMixService = Depends(get_crop_mix_service)):
    if not svc.delete(rec_id):
        raise HTTPException(status_code=404, detail="Optimization plan not found")
    return None
