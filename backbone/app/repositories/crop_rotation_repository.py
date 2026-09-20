from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.crop_rotation_matrix import CropRotationMatrix


class CropRotationRepository:
    def __init__(self, db: Session):
        self.db = db
        self.model = CropRotationMatrix

    def get(self, rotation_id: int) -> Optional[CropRotationMatrix]:
        return self.db.query(self.model).filter(self.model.id == rotation_id).first()

    def get_suitability(self, previous_crop: str, candidate_crop: str) -> Optional[int]:
        obj = self.db.query(self.model).filter(
            self.model.previous_crop_name == previous_crop,
            self.model.candidate_crop_name == candidate_crop
        ).first()
        return obj.suitability_score if obj else None

    def get_all(self, skip: int = 0, limit: int = 100) -> List[CropRotationMatrix]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def get_by_previous_crop(self, previous_crop: str) -> List[CropRotationMatrix]:
        return self.db.query(self.model).filter(self.model.previous_crop_name == previous_crop).all()

    def create(self, obj: CropRotationMatrix) -> CropRotationMatrix:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj: CropRotationMatrix, **kwargs) -> CropRotationMatrix:
        for key, value in kwargs.items():
            setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, rotation_id: int) -> bool:
        obj = self.get(rotation_id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True