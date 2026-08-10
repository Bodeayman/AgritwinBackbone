from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.diagnosis import Diagnosis


class DiagnosisRepository(BaseRepository[Diagnosis]):
    def __init__(self, db: Session):
        super().__init__(Diagnosis, db)

    def list_by_field(
        self,
        field_id: int,
        from_dt: Optional[datetime] = None,
        to_dt: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Diagnosis]:
        q = self.db.query(Diagnosis).filter(Diagnosis.field_id == field_id)
        if from_dt:
            q = q.filter(Diagnosis.diagnosed_at >= from_dt)
        if to_dt:
            q = q.filter(Diagnosis.diagnosed_at <= to_dt)
        return q.order_by(Diagnosis.diagnosed_at.desc()).offset(skip).limit(limit).all()
