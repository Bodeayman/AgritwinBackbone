from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.crop_rotation_repository import CropRotationRepository
from app.models.crop_rotation_matrix import CropRotationMatrix
from app.schemas.crop_rotation_matrix import CropRotationMatrixCreate, CropRotationMatrixOut


class CropRotationService:
    def __init__(self, db: Session):
        self.repo = CropRotationRepository(db)

    def create_rotation_rule(self, rotation_in: CropRotationMatrixCreate) -> CropRotationMatrixOut:
        obj = CropRotationMatrix(
            previous_crop_name=rotation_in.previous_crop_name,
            candidate_crop_name=rotation_in.candidate_crop_name,
            suitability_score=rotation_in.suitability_score,
            agronomic_notes=rotation_in.agronomic_notes,
        )
        return CropRotationMatrixOut.model_validate(self.repo.create(obj))

    def get_rotation(self, rotation_id: int) -> Optional[CropRotationMatrixOut]:
        obj = self.repo.get(rotation_id)
        return CropRotationMatrixOut.model_validate(obj) if obj else None

    def get_suitability(self, previous_crop: str, candidate_crop: str) -> Optional[int]:
        return self.repo.get_suitability(previous_crop, candidate_crop)

    def list_rotation_matrix(self, skip: int = 0, limit: int = 100) -> List[CropRotationMatrixOut]:
        objs = self.repo.get_all(skip=skip, limit=limit)
        return [CropRotationMatrixOut.model_validate(o) for o in objs]

    def get_previous_crop_options(self, previous_crop: str) -> List[CropRotationMatrixOut]:
        objs = self.repo.get_by_previous_crop(previous_crop)
        return [CropRotationMatrixOut.model_validate(o) for o in objs]

    def delete_rotation(self, rotation_id: int) -> bool:
        return self.repo.delete(rotation_id)