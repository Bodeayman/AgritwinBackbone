from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.disease_detection_repository import DiseaseDetectionRepository
from app.schemas.disease_detection import DiseaseDetectionCreate, DiseaseDetectionOut
from datetime import datetime

class DiseaseDetectionService:
    def __init__(self, db: Session):
        self.repo = DiseaseDetectionRepository(db)

    def create_detection(self, detection_in: DiseaseDetectionCreate) -> DiseaseDetectionOut:
        from app.models.disease_detection import DiseaseDetection
        obj = DiseaseDetection(
            field_id=detection_in.field_id,
            image_url=detection_in.image_url,
            disease_name=detection_in.disease_name,
            severity=detection_in.severity,
            confidence=detection_in.confidence,
            created_at=detection_in.created_at or datetime.utcnow(),
        )
        obj = self.repo.create(obj)
        return DiseaseDetectionOut.model_validate(obj)

    def get_detection(self, detection_id: int) -> Optional[DiseaseDetectionOut]:
        obj = self.repo.get(detection_id)
        return DiseaseDetectionOut.model_validate(obj) if obj else None

    def list_detections(self, field_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[DiseaseDetectionOut]:
        if field_id:
            objs = self.repo.db.query(self.repo.model).filter(self.repo.model.field_id == field_id).offset(skip).limit(limit).all()
        else:
            objs = self.repo.get_multi(skip=skip, limit=limit)
        return [DiseaseDetectionOut.model_validate(o) for o in objs]

    def update_detection(self, detection_id: int, detection_in: DiseaseDetectionCreate) -> Optional[DiseaseDetectionOut]:
        obj = self.repo.get(detection_id)
        if not obj:
            return None
        data = detection_in.model_dump(exclude_unset=True)
        updated = self.repo.update(obj, data)
        return DiseaseDetectionOut.model_validate(updated)

    def delete_detection(self, detection_id: int) -> bool:
        obj = self.repo.get(detection_id)
        if not obj:
            return False
        self.repo.remove(detection_id)
        return True
