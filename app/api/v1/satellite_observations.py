from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.satellite_observation import SatelliteObservationCreate, SatelliteObservationOut
from app.services.satellite_observation_service import SatelliteObservationService
from app.services.ai_model_service import AIModelService
from app.services.satellite_service import SatelliteService
from app.api.deps import get_satellite_observation_service, get_ai_model_service, get_satellite_service

router = APIRouter()


@router.post("/", response_model=SatelliteObservationOut, status_code=status.HTTP_201_CREATED,
             summary="Record a satellite observation")
def create(
    obs_in: SatelliteObservationCreate,
    svc: SatelliteObservationService = Depends(get_satellite_observation_service),
    ai_model_svc: AIModelService = Depends(get_ai_model_service),
    satellite_svc: SatelliteService = Depends(get_satellite_service),
):
    """Store a new satellite observation. Historical records are never overwritten."""
    # Resolve model_id to ensure it exists in ai_models table
    obs_in.model_id = ai_model_svc.resolve_model_id(
        obs_in.model_id, obs_in.model_name, obs_in.model_version
    )
    
    # Resolve satellite_id to ensure it exists in satellites table
    if obs_in.satellite_name and not obs_in.satellite_id:
        satellite = satellite_svc.get_or_create(obs_in.satellite_name)
        obs_in.satellite_id = satellite.id
    
    return svc.create(obs_in)


@router.get("/{obs_id}", response_model=SatelliteObservationOut, summary="Get observation by ID")
def get(obs_id: int, svc: SatelliteObservationService = Depends(get_satellite_observation_service)):
    obj = svc.get(obs_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Satellite observation not found")
    return obj


@router.get("/field/{field_id}", response_model=list[SatelliteObservationOut],
            summary="List satellite observations for a field")
def list_by_field(
    field_id: int,
    from_dt: Optional[datetime] = Query(None, alias="from"),
    to_dt: Optional[datetime] = Query(None, alias="to"),
    latest: bool = Query(False, description="If true, returns only the latest record"),
    skip: int = 0,
    limit: int = 100,
    svc: SatelliteObservationService = Depends(get_satellite_observation_service),
):
    if latest:
        skip, limit = 0, 1
    return svc.list_by_field(field_id, from_dt, to_dt, skip=skip, limit=limit)


@router.delete("/{obs_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete observation")
def delete(obs_id: int, svc: SatelliteObservationService = Depends(get_satellite_observation_service)):
    if not svc.delete(obs_id):
        raise HTTPException(status_code=404, detail="Satellite observation not found")
    return None
