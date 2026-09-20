from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, func, cast
from sqlalchemy.orm import Session
from geoalchemy2 import Geography
from app.repositories.base import BaseRepository
from app.models.field import Field


class FieldRepository(BaseRepository[Field]):
    def __init__(self, db: Session):
        super().__init__(Field, db)

    def get_by_name(self, name: str) -> Optional[Field]:
        stmt = select(Field).where(Field.name == name)
        return self.db.scalars(stmt).first()

    def list_fields(self, skip: int = 0, limit: int = 100) -> List[Field]:
        stmt = select(Field).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def get_fields_by_farm(self, farm_id: int, skip: int = 0, limit: int = 100) -> List[Field]:
        stmt = select(Field).where(Field.farm_id == farm_id).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())
