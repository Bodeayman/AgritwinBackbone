from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.crop_mix_recommendation import CropMixRecommendationCreate, CropMixRecommendationOut
from app.services.crop_mix_service import CropMixService
from app.api.deps import get_crop_mix_service

router = APIRouter()


@router.post("/", response_model=CropMixRecommendationOut, status_code=status.HTTP_201_CREATED,
             summary="Create a crop-mix recommendation")
def create(rec_in: CropMixRecommendationCreate, svc: CropMixService = Depends(get_crop_mix_service)):
    """Store a new optimization result with all crop allocations in one request.
    Each call creates a new historical recommendation record.
    """
    return svc.create(rec_in)


@router.get("/{rec_id}", response_model=CropMixRecommendationOut,
            summary="Get recommendation by ID")
def get(rec_id: int, svc: CropMixService = Depends(get_crop_mix_service)):
    obj = svc.get(rec_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Crop-mix recommendation not found")
    return obj


@router.get("/field/{field_id}", response_model=list[CropMixRecommendationOut],
            summary="List all crop-mix recommendations for a field")
def list_by_field(
    field_id: int,
    latest: bool = Query(False, description="If true, returns only the latest record"),
    skip: int = 0,
    limit: int = 100,
    svc: CropMixService = Depends(get_crop_mix_service),
):
    if latest:
        skip, limit = 0, 1
    return svc.list_by_field(field_id, skip=skip, limit=limit)


@router.get("/field/{field_id}/latest", response_model=Optional[CropMixRecommendationOut],
            summary="Get latest crop-mix recommendation for a field")
def get_latest(field_id: int, svc: CropMixService = Depends(get_crop_mix_service)):
    """Return the most recent optimization result for a given field."""
    return svc.get_latest_by_field(field_id)


@router.delete("/{rec_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete a recommendation")
def delete(rec_id: int, svc: CropMixService = Depends(get_crop_mix_service)):
    if not svc.delete(rec_id):
        raise HTTPException(status_code=404, detail="Crop-mix recommendation not found")
    return None
