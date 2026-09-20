import os
import uuid
from abc import ABC, abstractmethod
from typing import Set
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings

ALLOWED_EXTENSIONS: Set[str] = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}
MAX_FILE_SIZE_BYTES: int = 20 * 1024 * 1024  # 20 MB max


class ImageStorageBase(ABC):
    @abstractmethod
    def save_image(self, file: UploadFile, category: str, field_id: int) -> str:
        """Save image file and return the relative reference path."""
        pass


class LocalDiskImageStorage(ImageStorageBase):
    def __init__(self, base_path: str = settings.TEMP_IMAGE_STORAGE_PATH):
        self.base_path = os.path.abspath(base_path)

    def save_image(self, file: UploadFile, category: str, field_id: int) -> str:
        # 1. Validate file extension
        filename = file.filename or "image.jpg"
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # 2. Read content and validate file size
        content = file.file.read()
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum allowed limit ({MAX_FILE_SIZE_BYTES // (1024*1024)} MB)"
            )

        # 3. Create safe directory layout (protection against path traversal)
        # e.g., category = "fields" or "diagnoses"
        safe_category = "fields" if category == "fields" else "diagnoses"
        target_dir = os.path.join(self.base_path, safe_category, str(field_id))
        
        # Ensure target_dir is strictly under base_path
        abs_target_dir = os.path.abspath(target_dir)
        if not abs_target_dir.startswith(self.base_path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid target path"
            )

        os.makedirs(abs_target_dir, exist_ok=True)

        # 4. Generate safe unique filename
        safe_filename = f"{uuid.uuid4().hex}{ext}"
        full_filepath = os.path.join(abs_target_dir, safe_filename)

        with open(full_filepath, "wb") as f:
            f.write(content)

        # Return relative reference path for DB storage, e.g. "storage/images/diagnoses/123/a1b2c3.jpg"
        rel_path = os.path.relpath(full_filepath, start=os.getcwd()).replace("\\", "/")
        return rel_path


# Dependency provider
local_image_storage = LocalDiskImageStorage()

def get_local_image_storage() -> LocalDiskImageStorage:
    return local_image_storage
