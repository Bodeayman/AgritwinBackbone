from app.services.disease_detection_service import DiseaseDetectionService
from app.api.deps import get_disease_detection_service
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.disease_detection import DiseaseDetectionCreate, DiseaseDetectionOut

router = APIRouter()

@router.post('/', response_model=DiseaseDetectionOut, status_code=status.HTTP_201_CREATED)
def create_detection(detection_in: DiseaseDetectionCreate, svc: DiseaseDetectionService = Depends(get_disease_detection_service)):
    return svc.create_detection(detection_in)

@router.get('/{detection_id}', response_model=DiseaseDetectionOut)
def get_detection(detection_id: int, svc: DiseaseDetectionService = Depends(get_disease_detection_service)):
    obj = svc.get_detection(detection_id)
    if not obj:
        raise HTTPException(status_code=404, detail='Disease detection not found')
    return obj

@router.get('/', response_model=list[DiseaseDetectionOut])
def list_detections(field_id: int | None = None, skip: int = 0, limit: int = 100, svc: DiseaseDetectionService = Depends(get_disease_detection_service)):
    return svc.list_detections(field_id=field_id, skip=skip, limit=limit)

@router.put('/{detection_id}', response_model=DiseaseDetectionOut)
def update_detection(detection_id: int, detection_in: DiseaseDetectionCreate, svc: DiseaseDetectionService = Depends(get_disease_detection_service)):
    obj = svc.update_detection(detection_id, detection_in)
    if not obj:
        raise HTTPException(status_code=404, detail='Disease detection not found')
    return obj

@router.delete('/{detection_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_detection(detection_id: int, svc: DiseaseDetectionService = Depends(get_disease_detection_service)):
    success = svc.delete_detection(detection_id)
    if not success:
        raise HTTPException(status_code=404, detail='Disease detection not found')
    return None
