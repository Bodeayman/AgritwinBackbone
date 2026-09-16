from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.repositories.diagnosis_repository import DiagnosisRepository
from app.models.diagnosis import Diagnosis
from app.schemas.diagnosis import DiagnosisCreate, DiagnosisOut
from app.services.disease_service import DiseaseService


class DiagnosisService:
    def __init__(self, db: Session, disease_service: Optional[DiseaseService] = None):
        self.repo = DiagnosisRepository(db)
        self.disease_service = disease_service or DiseaseService(db)

    def create(self, diag_in: DiagnosisCreate) -> DiagnosisOut:
        # Find or create disease based on disease_name and crop_type
        disease = None
        if diag_in.disease_or_pest and diag_in.crop_type:
            disease = self.disease_service.find_or_create_disease(
                disease_name=diag_in.disease_or_pest,
                crop_type=diag_in.crop_type
            )
        
        obj = Diagnosis(
            field_id=diag_in.field_id,
            model_id=diag_in.model_id,
            imagery_id=diag_in.imagery_id,
            disease_id=disease.id if disease else None,
            status=diag_in.status,
            crop_type=diag_in.crop_type,
            disease_or_pest=diag_in.disease_or_pest,
            severity=diag_in.severity,
            confidence=diag_in.confidence,
            latitude=diag_in.latitude,
            longitude=diag_in.longitude,
            diagnosed_at=diag_in.diagnosed_at,
            explanation=diag_in.explanation,
            treatment_suggestion=diag_in.treatment_suggestion,
        )
        self.repo.db.add(obj)
        self.repo.db.commit()
        self.repo.db.refresh(obj)
        return DiagnosisOut.model_validate(obj)

    def get(self, diag_id: int) -> Optional[DiagnosisOut]:
        obj = self.repo.get(diag_id)
        return DiagnosisOut.model_validate(obj) if obj else None

    def list_by_field(
        self,
        field_id: int,
        from_dt: Optional[datetime] = None,
        to_dt: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[DiagnosisOut]:
        objs = self.repo.list_by_field(field_id, from_dt, to_dt, skip=skip, limit=limit)
        return [DiagnosisOut.model_validate(o) for o in objs]

    def delete(self, diag_id: int) -> bool:
        obj = self.repo.get(diag_id)
        if not obj:
            return False
        self.repo.db.delete(obj)
        self.repo.db.commit()
        return True
