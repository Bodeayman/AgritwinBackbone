from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.ai_model_repository import AIModelRepository
from app.schemas.ai_model import AIModelCreate, AIModelOut


class AIModelService:
    def __init__(self, db: Session):
        self.repo = AIModelRepository(db)

    def create_model(self, model_in: AIModelCreate) -> AIModelOut:
        obj = self.repo.get_or_create(model_in.name, model_in.version, model_in.description)
        return AIModelOut.model_validate(obj)

    def get_model(self, model_id: int) -> Optional[AIModelOut]:
        obj = self.repo.get(model_id)
        return AIModelOut.model_validate(obj) if obj else None

    def list_models(self, skip: int = 0, limit: int = 100) -> List[AIModelOut]:
        objs = self.repo.get_multi(skip=skip, limit=limit)
        return [AIModelOut.model_validate(o) for o in objs]

    def resolve_model_id(
        self,
        model_id: Optional[int] = None,
        model_name: Optional[str] = None,
        model_version: Optional[str] = None,
    ) -> Optional[int]:
        """Helper to resolve or auto-register AIModel and return its model_id."""
        if model_id:
            return model_id
        if model_name and model_version:
            obj = self.repo.get_or_create(model_name, model_version)
            return obj.id
        return None
