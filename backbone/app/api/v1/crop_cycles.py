from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.crop_cycle import CropCycleCreate, CropCycleUpdate, CropCycleOut
from app.services.crop_cycle_service import CropCycleService
from app.api.deps import get_crop_cycle_service

router = APIRouter()

@router.post("/", response_model=CropCycleOut, status_code=status.HTTP_201_CREATED)
def create_crop_cycle(cc_in: CropCycleCreate, svc: CropCycleService = Depends(get_crop_cycle_service)):
    return svc.create_crop_cycle(cc_in)

@router.get("/{crop_cycle_id}", response_model=CropCycleOut)
def get_crop_cycle(crop_cycle_id: int, svc: CropCycleService = Depends(get_crop_cycle_service)):
    obj = svc.get_crop_cycle(crop_cycle_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Crop cycle not found")
    return obj

@router.get("/", response_model=list[CropCycleOut])
def list_crop_cycles(skip: int = 0, limit: int = 100, svc: CropCycleService = Depends(get_crop_cycle_service)):
    return svc.list_crop_cycles(skip=skip, limit=limit)

@router.put("/{crop_cycle_id}", response_model=CropCycleOut)
def update_crop_cycle(crop_cycle_id: int, cc_in: CropCycleUpdate, svc: CropCycleService = Depends(get_crop_cycle_service)):
    obj = svc.update_crop_cycle(crop_cycle_id, cc_in)
    if not obj:
        raise HTTPException(status_code=404, detail="Crop cycle not found")
    return obj

@router.delete("/{crop_cycle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_crop_cycle(crop_cycle_id: int, svc: CropCycleService = Depends(get_crop_cycle_service)):
    success = svc.delete_crop_cycle(crop_cycle_id)
    if not success:
        raise HTTPException(status_code=404, detail="Crop cycle not found")
    return None
