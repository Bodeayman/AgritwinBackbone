from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.crop_cycle import CropCycle

class CropCycleRepository(BaseRepository[CropCycle]):
    def __init__(self, db: Session):
        super().__init__(CropCycle, db)

    def get_by_field(self, field_id: int) -> List[CropCycle]:
        stmt = select(CropCycle).where(CropCycle.field_id == field_id)
        return list(self.db.scalars(stmt).all())

    def list_crop_cycles(self, skip: int = 0, limit: int = 100) -> List[CropCycle]:
        stmt = select(CropCycle).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def delete(self, crop_cycle_id: int) -> bool:
        obj = self.get(crop_cycle_id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True
