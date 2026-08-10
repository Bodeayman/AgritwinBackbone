from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from app.repositories.irrigation_plan_repository import IrrigationPlanRepository
from app.models.irrigation_plan import IrrigationPlan
from app.schemas.irrigation_plan import IrrigationPlanCreate, IrrigationPlanOut


class IrrigationPlanService:
    def __init__(self, db: Session):
        self.repo = IrrigationPlanRepository(db)

    def create(self, plan_in: IrrigationPlanCreate) -> IrrigationPlanOut:
        obj = IrrigationPlan(
            field_id=plan_in.field_id,
            model_id=plan_in.model_id,
            water_requirement=plan_in.water_requirement,
            unit=plan_in.unit,
            recommended_date=plan_in.recommended_date,
        )
        self.repo.db.add(obj)
        self.repo.db.commit()
        self.repo.db.refresh(obj)
        return IrrigationPlanOut.model_validate(obj)

    def get(self, plan_id: int) -> Optional[IrrigationPlanOut]:
        obj = self.repo.get(plan_id)
        return IrrigationPlanOut.model_validate(obj) if obj else None

    def list_by_field(
        self,
        field_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[IrrigationPlanOut]:
        objs = self.repo.list_by_field(field_id, from_date, to_date, skip=skip, limit=limit)
        return [IrrigationPlanOut.model_validate(o) for o in objs]

    def delete(self, plan_id: int) -> bool:
        obj = self.repo.get(plan_id)
        if not obj:
            return False
        self.repo.db.delete(obj)
        self.repo.db.commit()
        return True
