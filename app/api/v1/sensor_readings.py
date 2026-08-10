from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.sensor_reading import SensorCreate, SensorOut
from app.services.sensor_service import SensorService
from app.api.deps import get_sensor_service

router = APIRouter()


@router.post("/", response_model=SensorOut, status_code=status.HTTP_201_CREATED,
             summary="Record a sensor reading")
def create_reading(reading_in: SensorCreate, svc: SensorService = Depends(get_sensor_service)):
    """Store a new sensor reading. Each call creates a new historical record."""
    return svc.create_reading(reading_in)


@router.get("/{reading_id}", response_model=SensorOut, summary="Get reading by ID")
def get_reading(reading_id: int, svc: SensorService = Depends(get_sensor_service)):
    obj = svc.get_reading(reading_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Reading not found")
    return obj


@router.get("/field/{field_id}", response_model=list[SensorOut],
            summary="List sensor readings for a field")
def list_by_field(
    field_id: int,
    from_dt: Optional[datetime] = Query(None, alias="from", description="Filter from (ISO datetime)"),
    to_dt: Optional[datetime] = Query(None, alias="to", description="Filter to (ISO datetime)"),
    latest: bool = Query(False, description="If true, returns only the latest record"),
    skip: int = 0,
    limit: int = 100,
    svc: SensorService = Depends(get_sensor_service),
):
    """Return historical sensor readings for a field, newest first.
    Optionally filter with `?from=2026-08-01T00:00:00&to=2026-08-08T23:59:59` or `?latest=true`.
    """
    if latest:
        skip, limit = 0, 1
    if from_dt or to_dt:
        return svc.list_by_field_date_range(field_id, from_dt, to_dt, skip=skip, limit=limit)
    return svc.list_by_field(field_id, skip=skip, limit=limit)


@router.delete("/{reading_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete a reading")
def delete_reading(reading_id: int, svc: SensorService = Depends(get_sensor_service)):
    if not svc.delete_reading(reading_id):
        raise HTTPException(status_code=404, detail="Reading not found")
    return None
