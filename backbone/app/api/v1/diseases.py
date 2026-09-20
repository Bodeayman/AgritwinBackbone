from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.disease import DiseaseCreate, DiseaseUpdate, DiseaseOut, DiseaseReferenceOut
from app.services.disease_service import DiseaseService
from app.api.deps import get_disease_service

router = APIRouter()


@router.get("/", response_model=list[DiseaseOut],
            summary="List diseases")
def list_diseases(
    crop_type: Optional[str] = Query(None, description="Filter by crop type"),
    is_active: bool = Query(True, description="Filter by active status"),
    skip: int = 0,
    limit: int = 100,
    svc: DiseaseService = Depends(get_disease_service),
):
    """List all diseases in the database, optionally filtered by crop type"""
    return svc.list_diseases(crop_type=crop_type, is_active=is_active, skip=skip, limit=limit)


@router.get("/sync/status", summary="Get sync status")
def get_sync_status(
    external_url: Optional[str] = Query(None, description="External knowledge base module URL"),
    svc: DiseaseService = Depends(get_disease_service),
):
    """Get sync status and statistics"""
    status_data = {
        "total_diseases": svc.get_total_disease_count(),
        "diseases_by_crop": svc.get_disease_count_by_crop(),
    }
    
    if external_url:
        status_data["external_kb_reachable"] = svc.check_external_kb_reachable(external_url)
    
    return status_data


@router.get("/search/external", summary="Search external knowledge base")
def search_external(
    name: str = Query(..., description="Disease name to search"),
    crop: str = Query(..., description="Crop type"),
    external_url: str = Query(..., description="External knowledge base module URL"),
    svc: DiseaseService = Depends(get_disease_service),
):
    """
    Search external knowledge base by name and crop.
    Does not sync, just returns search results.
    """
    result = svc.search_external(external_url, name, crop)
    if not result:
        raise HTTPException(status_code=404, detail="Disease not found in external knowledge base")
    return result


@router.get("/{disease_id}", response_model=DiseaseOut,
            summary="Get disease by ID")
def get_disease(
    disease_id: int,
    svc: DiseaseService = Depends(get_disease_service),
):
    """Get a specific disease by local ID"""
    disease = svc.get_disease(disease_id)
    if not disease:
        raise HTTPException(status_code=404, detail="Disease not found")
    return disease


@router.get("/external-id/{external_id}", response_model=DiseaseOut,
            summary="Get disease by external ID")
def get_disease_by_external_id(
    external_id: str,
    svc: DiseaseService = Depends(get_disease_service),
):
    """Get disease by external knowledge base ID (e.g., MAIZE_001)"""
    disease = svc.get_by_external_id(external_id)
    if not disease:
        raise HTTPException(status_code=404, detail="Disease not found")
    return disease


@router.post("/", response_model=DiseaseOut, status_code=status.HTTP_201_CREATED,
             summary="Create disease")
def create_disease(
    disease_in: DiseaseCreate,
    svc: DiseaseService = Depends(get_disease_service),
):
    """Create a new disease record (manual entry)"""
    return svc.create_disease(disease_in)


@router.put("/{disease_id}", response_model=DiseaseOut,
            summary="Update disease")
def update_disease(
    disease_id: int,
    disease_in: DiseaseUpdate,
    svc: DiseaseService = Depends(get_disease_service),
):
    """Update an existing disease record"""
    disease = svc.update_disease(disease_id, disease_in)
    if not disease:
        raise HTTPException(status_code=404, detail="Disease not found")
    return disease


@router.delete("/{disease_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete disease")
def delete_disease(
    disease_id: int,
    svc: DiseaseService = Depends(get_disease_service),
):
    """Soft delete disease (set is_active=False)"""
    if not svc.delete_disease(disease_id):
        raise HTTPException(status_code=404, detail="Disease not found")
    return None


@router.post("/sync", summary="Sync diseases from external module")
def sync_diseases(
    external_url: str = Query(..., description="External knowledge base module URL"),
    svc: DiseaseService = Depends(get_disease_service),
):
    """
    Sync diseases from external knowledge base module.
    Creates new diseases and updates existing ones.
    """
    try:
        stats = svc.sync_from_external(external_url)
        return {
            "message": "Diseases synced successfully",
            "created": stats["created"],
            "updated": stats["updated"],
            "total": stats["total"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to sync from external knowledge base: {str(e)}"
        )