from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, get_imagery_service
from app.schemas.imagery import ImageryCreate, ImageryUpdate, ImageryOut
from app.services.imagery_service import ImageryService
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=ImageryOut, status_code=status.HTTP_201_CREATED, summary="Create imagery record")
def create_imagery(
    imagery_in: ImageryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    imagery_svc: ImageryService = Depends(get_imagery_service),
):
    """Create a new imagery record."""
    return imagery_svc.create(imagery_in)


@router.get("/{imagery_id}", response_model=ImageryOut, summary="Get imagery by ID")
def get_imagery(
    imagery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    imagery_svc: ImageryService = Depends(get_imagery_service),
):
    """Get a specific imagery record by ID."""
    imagery = imagery_svc.get(imagery_id)
    if not imagery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Imagery with ID {imagery_id} not found"
        )
    return imagery


@router.get("/field/{field_id}", response_model=List[ImageryOut], summary="List imagery for field")
def list_imagery_by_field(
    field_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    imagery_svc: ImageryService = Depends(get_imagery_service),
):
    """List all imagery records for a specific field."""
    return imagery_svc.list_by_field(field_id, skip=skip, limit=limit)


@router.put("/{imagery_id}", response_model=ImageryOut, summary="Update imagery record")
def update_imagery(
    imagery_id: int,
    imagery_in: ImageryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    imagery_svc: ImageryService = Depends(get_imagery_service),
):
    """Update an existing imagery record."""
    imagery = imagery_svc.update(imagery_id, imagery_in)
    if not imagery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Imagery with ID {imagery_id} not found"
        )
    return imagery


@router.delete("/{imagery_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete imagery record")
def delete_imagery(
    imagery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    imagery_svc: ImageryService = Depends(get_imagery_service),
):
    """Delete an imagery record."""
    success = imagery_svc.delete(imagery_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Imagery with ID {imagery_id} not found"
        )
