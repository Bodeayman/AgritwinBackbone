from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.farm import FarmCreate, FarmUpdate, FarmOut
from app.services.farm_service import FarmService
from app.api.deps import get_farm_service, get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=FarmOut, status_code=status.HTTP_201_CREATED,
             summary="Create a new farm")
def create_farm(
    farm_in: FarmCreate,
    svc: FarmService = Depends(get_farm_service),
    current_user: User = Depends(get_current_user),
):
    """Create a farm. The owner is automatically set to the authenticated farmer from the JWT token.

    **Request body:**
    ```json
    {
        "name": "Green Valley Farm",
        "location": "Nairobi County, Kenya"
    }
    ```
    """
    return svc.create_farm(farm_in, owner_id=current_user.id)


@router.get("/", response_model=list[FarmOut], summary="List my farms")
def list_my_farms(
    skip: int = 0,
    limit: int = 100,
    svc: FarmService = Depends(get_farm_service),
    current_user: User = Depends(get_current_user),
):
    """Return only the farms that belong to the currently authenticated farmer."""
    return svc.list_farms_by_owner(current_user.id, skip=skip, limit=limit)


@router.get("/{farm_id}", response_model=FarmOut, summary="Get farm by ID")
def get_farm(
    farm_id: int,
    svc: FarmService = Depends(get_farm_service),
    current_user: User = Depends(get_current_user),
):
    obj = svc.get_farm(farm_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Farm not found")
    if obj.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorised to access this farm")
    return obj


@router.put("/{farm_id}", response_model=FarmOut, summary="Update farm")
def update_farm(
    farm_id: int,
    farm_in: FarmUpdate,
    svc: FarmService = Depends(get_farm_service),
    current_user: User = Depends(get_current_user),
):
    obj = svc.get_farm(farm_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Farm not found")
    if obj.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorised to modify this farm")
    updated = svc.update_farm(farm_id, farm_in)
    return updated


@router.delete("/{farm_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete farm")
def delete_farm(
    farm_id: int,
    svc: FarmService = Depends(get_farm_service),
    current_user: User = Depends(get_current_user),
):
    obj = svc.get_farm(farm_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Farm not found")
    if obj.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorised to delete this farm")
    svc.delete_farm(farm_id)
    return None
