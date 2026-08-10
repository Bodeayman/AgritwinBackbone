from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.field import FieldCreate, FieldUpdate, FieldOut
from app.schemas.field_boundary import FieldBoundaryCreate, FieldBoundaryOut
from app.services.field_service import FieldService
from app.services.field_boundary_service import FieldBoundaryService
from app.api.deps import get_field_service, get_field_boundary_service

router = APIRouter()


# ── Field CRUD ────────────────────────────────────────────────────────────────

@router.post("/", response_model=FieldOut, status_code=status.HTTP_201_CREATED,
             summary="Create a field")
def create_field(field_in: FieldCreate, svc: FieldService = Depends(get_field_service)):
    """Create a field. Set the boundary separately via POST /{field_id}/boundary."""
    return svc.create_field(field_in)


@router.get("/{field_id}", response_model=FieldOut, summary="Get field by ID")
def get_field(field_id: int, svc: FieldService = Depends(get_field_service)):
    obj = svc.get_field(field_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Field not found")
    return obj


@router.get("/", response_model=list[FieldOut], summary="List all fields")
def list_fields(skip: int = 0, limit: int = 100, svc: FieldService = Depends(get_field_service)):
    return svc.list_fields(skip=skip, limit=limit)


@router.put("/{field_id}", response_model=FieldOut, summary="Update field")
def update_field(
    field_id: int, field_in: FieldUpdate, svc: FieldService = Depends(get_field_service)
):
    obj = svc.update_field(field_id, field_in)
    if not obj:
        raise HTTPException(status_code=404, detail="Field not found")
    return obj


@router.delete("/{field_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete field")
def delete_field(field_id: int, svc: FieldService = Depends(get_field_service)):
    if not svc.delete_field(field_id):
        raise HTTPException(status_code=404, detail="Field not found")
    return None


# ── Boundary sub-resource ─────────────────────────────────────────────────────

@router.post(
    "/{field_id}/boundary",
    response_model=FieldBoundaryOut,
    status_code=status.HTTP_200_OK,
    summary="Set or replace field boundary",
)
def set_boundary(
    field_id: int,
    boundary_in: FieldBoundaryCreate,
    svc: FieldBoundaryService = Depends(get_field_boundary_service),
):
    """Store a PostGIS polygon as the geographic boundary of the field.
    If a boundary already exists for this field it will be replaced.
    """
    return svc.set_boundary(field_id, boundary_in)


@router.get(
    "/{field_id}/boundary",
    response_model=Optional[FieldBoundaryOut],
    summary="Get field boundary",
)
def get_boundary(
    field_id: int,
    svc: FieldBoundaryService = Depends(get_field_boundary_service),
):
    """Return the geographic boundary polygon and area (hectares) for a field."""
    return svc.get_boundary(field_id)
