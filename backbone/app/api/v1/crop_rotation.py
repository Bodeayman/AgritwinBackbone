from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.crop_rotation_matrix import CropRotationMatrixCreate, CropRotationMatrixOut
from app.services.crop_rotation_service import CropRotationService
from app.api.deps import get_crop_rotation_service

router = APIRouter()


@router.post("/", response_model=CropRotationMatrixOut, status_code=status.HTTP_201_CREATED,
             summary="Create crop rotation rule")
def create_rotation_rule(
    rotation_in: CropRotationMatrixCreate,
    svc: CropRotationService = Depends(get_crop_rotation_service),
):
    """Add a new crop rotation suitability rule."""
    return svc.create_rotation_rule(rotation_in)


@router.get("/", response_model=list[CropRotationMatrixOut],
            summary="List crop rotation matrix")
def list_rotation_matrix(
    skip: int = 0,
    limit: int = 100,
    svc: CropRotationService = Depends(get_crop_rotation_service),
):
    """Get the complete crop rotation matrix."""
    return svc.list_rotation_matrix(skip=skip, limit=limit)


@router.get("/{rotation_id}", response_model=CropRotationMatrixOut,
            summary="Get rotation rule by ID")
def get_rotation(
    rotation_id: int,
    svc: CropRotationService = Depends(get_crop_rotation_service),
):
    """Get a specific rotation rule."""
    rotation = svc.get_rotation(rotation_id)
    if not rotation:
        raise HTTPException(status_code=404, detail="Rotation rule not found")
    return rotation


@router.get("/suitability/{previous_crop}/{candidate_crop}",
            summary="Check crop rotation suitability")
def get_suitability(
    previous_crop: str,
    candidate_crop: str,
    svc: CropRotationService = Depends(get_crop_rotation_service),
):
    """Check if a crop rotation is suitable (returns 0 or 1)."""
    suitability = svc.get_suitability(previous_crop, candidate_crop)
    if suitability is None:
        raise HTTPException(status_code=404, detail="Rotation rule not found")
    return {"suitability": suitability}


@router.get("/previous/{previous_crop}", response_model=list[CropRotationMatrixOut],
            summary="Get suitable next crops")
def get_previous_crop_options(
    previous_crop: str,
    svc: CropRotationService = Depends(get_crop_rotation_service),
):
    """Get all suitable next crops for a given previous crop."""
    return svc.get_previous_crop_options(previous_crop)


@router.delete("/{rotation_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete rotation rule")
def delete_rotation(
    rotation_id: int,
    svc: CropRotationService = Depends(get_crop_rotation_service),
):
    """Remove a rotation rule."""
    if not svc.delete_rotation(rotation_id):
        raise HTTPException(status_code=404, detail="Rotation rule not found")
    return None