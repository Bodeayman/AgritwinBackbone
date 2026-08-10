from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from app.repositories.yield_prediction_repository import YieldPredictionRepository
from app.models.yield_prediction import YieldPrediction
from app.schemas.yield_prediction import YieldPredictionCreate, YieldPredictionOut


class YieldPredictionService:
    def __init__(self, db: Session):
        self.repo = YieldPredictionRepository(db)

    def create(self, pred_in: YieldPredictionCreate) -> YieldPredictionOut:
        obj = YieldPrediction(
            field_id=pred_in.field_id,
            model_id=pred_in.model_id,
            status=pred_in.status,
            crop_type=pred_in.crop_type,
            predicted_yield=pred_in.predicted_yield,
            unit=pred_in.unit,
            confidence=pred_in.confidence,
            prediction_date=pred_in.prediction_date,
            model_version=pred_in.model_version,
        )
        self.repo.db.add(obj)
        self.repo.db.commit()
        self.repo.db.refresh(obj)
        return YieldPredictionOut.model_validate(obj)

    def get(self, pred_id: int) -> Optional[YieldPredictionOut]:
        obj = self.repo.get(pred_id)
        return YieldPredictionOut.model_validate(obj) if obj else None

    def list_by_field(
        self,
        field_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[YieldPredictionOut]:
        objs = self.repo.list_by_field(field_id, from_date, to_date, skip=skip, limit=limit)
        return [YieldPredictionOut.model_validate(o) for o in objs]

    def delete(self, pred_id: int) -> bool:
        obj = self.repo.get(pred_id)
        if not obj:
            return False
        self.repo.db.delete(obj)
        self.repo.db.commit()
        return True
