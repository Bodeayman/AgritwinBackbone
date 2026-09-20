from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.imagery import Imagery


class ImageryRepository(BaseRepository[Imagery]):
    def __init__(self, db: Session):
        super().__init__(Imagery, db)

    def get_by_field(self, field_id: int, skip: int = 0, limit: int = 100) -> List[Imagery]:
        return self.db.query(Imagery).filter(Imagery.field_id == field_id).offset(skip).limit(limit).all()

    def get_by_field_and_type(self, field_id: int, image_type: str, skip: int = 0, limit: int = 100) -> List[Imagery]:
        return self.db.query(Imagery).filter(
            Imagery.field_id == field_id,
            Imagery.image_type == image_type
        ).offset(skip).limit(limit).all()

    def get_by_storage_path(self, storage_path: str) -> Optional[Imagery]:
        return self.db.query(Imagery).filter(Imagery.storage_path == storage_path).first()
