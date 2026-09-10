from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.crop_catalog import CropCatalogCreate, CropCatalogOut
from app.services.crop_catalog_service import CropCatalogService
from app.api.deps import get_crop_catalog_service

router = APIRouter()


@router.post("/", response_model=CropCatalogOut, status_code=status.HTTP_201_CREATED,
             summary="Create crop in catalog")
def create_crop(
    crop_in: CropCatalogCreate,
    svc: CropCatalogService = Depends(get_crop_catalog_service),
):
    """Add a new crop to the catalog with EcoCrop parameters."""
    return svc.create_crop(crop_in)


@router.get("/", response_model=list[CropCatalogOut],
            summary="List crop catalog")
def list_crops(
    farm_id: Optional[int] = Query(None, description="Filter by farm (NULL for global crops)"),
    skip: int = 0,
    limit: int = 100,
    svc: CropCatalogService = Depends(get_crop_catalog_service),
):
    """Get all crops in the catalog. Use farm_id to get farm-specific crops."""
    if farm_id is None:
        return svc.list_global_crops(skip=skip, limit=limit)
    return svc.list_crops(skip=skip, limit=limit, farm_id=farm_id)


@router.get("/global", response_model=list[CropCatalogOut],
            summary="List global crop catalog")
def list_global_crops(
    skip: int = 0,
    limit: int = 100,
    svc: CropCatalogService = Depends(get_crop_catalog_service),
):
    """Get global crops (not farm-specific)."""
    return svc.list_global_crops(skip=skip, limit=limit)


@router.get("/{crop_id}", response_model=CropCatalogOut,
            summary="Get crop by ID")
def get_crop(
    crop_id: int,
    svc: CropCatalogService = Depends(get_crop_catalog_service),
):
    """Get a specific crop from the catalog."""
    crop = svc.get_crop(crop_id)
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    return crop


@router.get("/name/{name_en}", response_model=CropCatalogOut,
            summary="Get crop by name")
def get_crop_by_name(
    name_en: str,
    farm_id: Optional[int] = Query(None),
    svc: CropCatalogService = Depends(get_crop_catalog_service),
):
    """Get a crop by its English name."""
    crop = svc.get_by_name(name_en, farm_id)
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    return crop


@router.delete("/{crop_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete crop from catalog")
def delete_crop(
    crop_id: int,
    svc: CropCatalogService = Depends(get_crop_catalog_service),
):
    """Remove a crop from the catalog."""
    if not svc.delete_crop(crop_id):
        raise HTTPException(status_code=404, detail="Crop not found")
    return None