from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.diagnosis import DiagnosisCreate, DiagnosisOut
from app.services.diagnosis_service import DiagnosisService
from app.api.deps import get_diagnosis_service

router = APIRouter()


@router.post("/", response_model=DiagnosisOut, status_code=status.HTTP_201_CREATED,
             summary="Create a diagnosis")
def create(diag_in: DiagnosisCreate, svc: DiagnosisService = Depends(get_diagnosis_service)):
    """Store a disease/pest diagnosis. Multiple diagnoses per field are supported."""
    return svc.create(diag_in)


@router.get("/{diag_id}", response_model=DiagnosisOut, summary="Get diagnosis by ID")
def get(diag_id: int, svc: DiagnosisService = Depends(get_diagnosis_service)):
    obj = svc.get(diag_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Diagnosis not found")
    return obj


@router.get("/field/{field_id}", response_model=list[DiagnosisOut],
            summary="List diagnoses for a field")
def list_by_field(
    field_id: int,
    from_dt: Optional[datetime] = Query(None, alias="from"),
    to_dt: Optional[datetime] = Query(None, alias="to"),
    latest: bool = Query(False, description="If true, returns only the latest record"),
    skip: int = 0,
    limit: int = 100,
    svc: DiagnosisService = Depends(get_diagnosis_service),
):
    if latest:
        skip, limit = 0, 1
    return svc.list_by_field(field_id, from_dt, to_dt, skip=skip, limit=limit)


@router.delete("/{diag_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete diagnosis")
def delete(diag_id: int, svc: DiagnosisService = Depends(get_diagnosis_service)):
    if not svc.delete(diag_id):
        raise HTTPException(status_code=404, detail="Diagnosis not found")
    return None
