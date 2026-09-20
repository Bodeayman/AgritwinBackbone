from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.ai_model import AIModel


class AIModelRepository(BaseRepository[AIModel]):
    def __init__(self, db: Session):
        super().__init__(AIModel, db)

    def get_by_name_and_version(self, name: str, version: str) -> Optional[AIModel]:
        stmt = select(AIModel).where(AIModel.name == name, AIModel.version == version)
        return self.db.scalars(stmt).first()

    def get_or_create(self, name: str, version: str, description: Optional[str] = None) -> AIModel:
        existing = self.get_by_name_and_version(name, version)
        if existing:
            return existing
        model = AIModel(name=name, version=version, description=description)
        return self.create(model)
