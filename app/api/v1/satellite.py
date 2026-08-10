from app.services.satellite_service import SatelliteService
from app.api.deps import get_satellite_service
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.satellite_data import SatelliteCreate, SatelliteOut

router = APIRouter()

@router.post('/', response_model=SatelliteOut, status_code=status.HTTP_201_CREATED)
def create_satellite(sat_in: SatelliteCreate, svc: SatelliteService = Depends(get_satellite_service)):
    return svc.create_satellite(sat_in)

@router.get('/{sat_id}', response_model=SatelliteOut)
def get_satellite(sat_id: int, svc: SatelliteService = Depends(get_satellite_service)):
    obj = svc.get_satellite(sat_id)
    if not obj:
        raise HTTPException(status_code=404, detail='Satellite entry not found')
    return obj

@router.get('/', response_model=list[SatelliteOut])
def list_satellite(field_id: int | None = None, skip: int = 0, limit: int = 100, svc: SatelliteService = Depends(get_satellite_service)):
    return svc.list_satellite(field_id=field_id, skip=skip, limit=limit)

@router.put('/{sat_id}', response_model=SatelliteOut)
def update_satellite(sat_id: int, sat_in: SatelliteCreate, svc: SatelliteService = Depends(get_satellite_service)):
    obj = svc.update_satellite(sat_id, sat_in)
    if not obj:
        raise HTTPException(status_code=404, detail='Satellite entry not found')
    return obj

@router.delete('/{sat_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_satellite(sat_id: int, svc: SatelliteService = Depends(get_satellite_service)):
    success = svc.delete_satellite(sat_id)
    if not success:
        raise HTTPException(status_code=404, detail='Satellite entry not found')
    return None
