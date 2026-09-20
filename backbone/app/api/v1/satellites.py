from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, get_satellite_service
from app.schemas.satellite import SatelliteCreate, SatelliteUpdate, SatelliteOut
from app.services.satellite_service import SatelliteService
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=SatelliteOut, status_code=status.HTTP_201_CREATED, summary="Create satellite record")
def create_satellite(
    satellite_in: SatelliteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    satellite_svc: SatelliteService = Depends(get_satellite_service),
):
    """Create a new satellite record."""
    return satellite_svc.create(satellite_in)


@router.get("/", response_model=List[SatelliteOut], summary="List all satellites")
def list_satellites(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    satellite_svc: SatelliteService = Depends(get_satellite_service),
):
    """List all satellite records."""
    return satellite_svc.list_all(skip=skip, limit=limit)


@router.get("/active", response_model=List[SatelliteOut], summary="List active satellites")
def list_active_satellites(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    satellite_svc: SatelliteService = Depends(get_satellite_service),
):
    """List only active satellite records."""
    return satellite_svc.list_active(skip=skip, limit=limit)


@router.get("/{satellite_id}", response_model=SatelliteOut, summary="Get satellite by ID")
def get_satellite(
    satellite_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    satellite_svc: SatelliteService = Depends(get_satellite_service),
):
    """Get a specific satellite record by ID."""
    satellite = satellite_svc.get(satellite_id)
    if not satellite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Satellite with ID {satellite_id} not found"
        )
    return satellite


@router.get("/name/{name}", response_model=SatelliteOut, summary="Get satellite by name")
def get_satellite_by_name(
    name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    satellite_svc: SatelliteService = Depends(get_satellite_service),
):
    """Get a specific satellite record by name."""
    satellite = satellite_svc.get_by_name(name)
    if not satellite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Satellite with name {name} not found"
        )
    return satellite


@router.get("/{satellite_id}/observations", response_model=SatelliteOut, summary="Get satellite with observations")
def get_satellite_with_observations(
    satellite_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    satellite_svc: SatelliteService = Depends(get_satellite_service),
):
    """Get a specific satellite record with its observations."""
    satellite = satellite_svc.get_with_observations(satellite_id)
    if not satellite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Satellite with ID {satellite_id} not found"
        )
    return satellite
def get_satellite_by_name(
    name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    satellite_svc: SatelliteService = Depends(get_satellite_service),
):
    """Get a specific satellite record by name."""
    satellite = satellite_svc.get_by_name(name)
    if not satellite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Satellite with name {name} not found"
        )
    return satellite


@router.put("/{satellite_id}", response_model=SatelliteOut, summary="Update satellite record")
def update_satellite(
    satellite_id: int,
    satellite_in: SatelliteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    satellite_svc: SatelliteService = Depends(get_satellite_service),
):
    """Update an existing satellite record."""
    satellite = satellite_svc.update(satellite_id, satellite_in)
    if not satellite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Satellite with ID {satellite_id} not found"
        )
    return satellite


@router.delete("/{satellite_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete satellite record")
def delete_satellite(
    satellite_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    satellite_svc: SatelliteService = Depends(get_satellite_service),
):
    """Delete a satellite record."""
    success = satellite_svc.delete(satellite_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Satellite with ID {satellite_id} not found"
        )
