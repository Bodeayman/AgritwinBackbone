from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.imagery_repository import ImageryRepository
from app.models.imagery import Imagery
from app.schemas.imagery import ImageryCreate, ImageryUpdate, ImageryOut


class ImageryService:
    def __init__(self, db: Session):
        self.repo = ImageryRepository(db)

    def create(self, imagery_in: ImageryCreate) -> ImageryOut:
        obj = Imagery(
            field_id=imagery_in.field_id,
            storage_path=imagery_in.storage_path,
            storage_type=imagery_in.storage_type,
            storage_bucket=imagery_in.storage_bucket,
            file_name=imagery_in.file_name,
            file_extension=imagery_in.file_extension,
            file_size_bytes=imagery_in.file_size_bytes,
            mime_type=imagery_in.mime_type,
            image_type=imagery_in.image_type,
            capture_time=imagery_in.capture_time,
            resolution_m=imagery_in.resolution_m,
            spectral_bands=imagery_in.spectral_bands,
            width_pixels=imagery_in.width_pixels,
            height_pixels=imagery_in.height_pixels,
            source=imagery_in.source,
            additional_metadata=imagery_in.additional_metadata,
        )
        self.repo.db.add(obj)
        self.repo.db.commit()
        self.repo.db.refresh(obj)
        return ImageryOut.model_validate(obj)

    def get(self, imagery_id: int) -> Optional[ImageryOut]:
        obj = self.repo.get(imagery_id)
        return ImageryOut.model_validate(obj) if obj else None

    def get_by_field(self, field_id: int, skip: int = 0, limit: int = 100) -> List[ImageryOut]:
        objs = self.repo.get_by_field(field_id, skip=skip, limit=limit)
        return [ImageryOut.model_validate(o) for o in objs]

    def get_by_field_and_type(self, field_id: int, image_type: str, skip: int = 0, limit: int = 100) -> List[ImageryOut]:
        objs = self.repo.get_by_field_and_type(field_id, image_type, skip=skip, limit=limit)
        return [ImageryOut.model_validate(o) for o in objs]

    def list_all(self, skip: int = 0, limit: int = 100) -> List[ImageryOut]:
        objs = self.repo.list_all(skip=skip, limit=limit)
        return [ImageryOut.model_validate(o) for o in objs]

    def list_by_field(self, field_id: int, skip: int = 0, limit: int = 100) -> List[ImageryOut]:
        objs = self.repo.get_by_field(field_id, skip=skip, limit=limit)
        return [ImageryOut.model_validate(o) for o in objs]

    def update(self, imagery_id: int, imagery_in: ImageryUpdate) -> Optional[ImageryOut]:
        obj = self.repo.get(imagery_id)
        if not obj:
            return None
        
        update_data = imagery_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(obj, field, value)
        
        self.repo.db.commit()
        self.repo.db.refresh(obj)
        return ImageryOut.model_validate(obj)

    def delete(self, imagery_id: int) -> bool:
        obj = self.repo.get(imagery_id)
        if not obj:
            return False
        self.repo.db.delete(obj)
        self.repo.db.commit()
        return True
