from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.farm import Farm

class FarmRepository(BaseRepository[Farm]):
    def __init__(self, db: Session):
        super().__init__(Farm, db)

    def get_by_name(self, name: str) -> Optional[Farm]:
        stmt = select(Farm).where(Farm.name == name)
        return self.db.scalars(stmt).first()

    def list_farms(self, skip: int = 0, limit: int = 100) -> List[Farm]:
        stmt = select(Farm).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def list_by_owner(self, owner_id: int, skip: int = 0, limit: int = 100) -> List[Farm]:
        stmt = select(Farm).where(Farm.owner_id == owner_id).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())
