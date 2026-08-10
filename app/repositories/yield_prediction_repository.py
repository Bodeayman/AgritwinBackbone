from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.yield_prediction import YieldPrediction


class YieldPredictionRepository(BaseRepository[YieldPrediction]):
    def __init__(self, db: Session):
        super().__init__(YieldPrediction, db)

    def list_by_field(
        self,
        field_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[YieldPrediction]:
        q = self.db.query(YieldPrediction).filter(YieldPrediction.field_id == field_id)
        if from_date:
            q = q.filter(YieldPrediction.prediction_date >= from_date)
        if to_date:
            q = q.filter(YieldPrediction.prediction_date <= to_date)
        return q.order_by(YieldPrediction.prediction_date.desc()).offset(skip).limit(limit).all()
