from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.irrigation_plan import IrrigationPlan


class IrrigationPlanRepository(BaseRepository[IrrigationPlan]):
    def __init__(self, db: Session):
        super().__init__(IrrigationPlan, db)

    def list_by_field(
        self,
        field_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[IrrigationPlan]:
        q = self.db.query(IrrigationPlan).filter(IrrigationPlan.field_id == field_id)
        if from_date:
            q = q.filter(IrrigationPlan.recommended_date >= from_date)
        if to_date:
            q = q.filter(IrrigationPlan.recommended_date <= to_date)
        return q.order_by(IrrigationPlan.recommended_date.desc()).offset(skip).limit(limit).all()
