from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from uuid import uuid4
from app.services.image_processing_service import ImageProcessingService
from app.api.deps import get_image_service

router = APIRouter()

@router.post("/process", status_code=status.HTTP_200_OK)
async def upload_image(file: UploadFile = File(...), svc: ImageProcessingService = Depends(get_image_service)):
    # In a real implementation, we would store the file in MinIO and get a URL.
    # Here we simulate by using a dummy URL.
    dummy_url = f"https://example.com/{file.filename}"
    await svc.enqueue_image(dummy_url)
    return {"job_id": uuid4().hex, "status": "queued"}
