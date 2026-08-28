from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.field_repository import FieldRepository
from app.models.field import Field
from app.schemas.field import FieldCreate, FieldUpdate, FieldOut
from app.services.event_service import EventService


class FieldService:
    def __init__(self, db: Session):
        self.repo = FieldRepository(db)
        self.event_service = EventService()

    def create_field(self, field_in: FieldCreate) -> FieldOut:
        field = Field(
            farm_id=field_in.farm_id,
            name=field_in.name,
        )
        obj = self.repo.create(field)
        self.event_service.publish_event("field_created", {"id": obj.id})
        return FieldOut.model_validate(obj)

    def get_field(self, field_id: int) -> Optional[FieldOut]:
        obj = self.repo.get(field_id)
        return FieldOut.model_validate(obj) if obj else None

    def list_fields(self, skip: int = 0, limit: int = 100) -> List[FieldOut]:
        objs = self.repo.list_fields(skip=skip, limit=limit)
        return [FieldOut.model_validate(o) for o in objs]

    def list_by_farm(self, farm_id: int, skip: int = 0, limit: int = 100) -> List[FieldOut]:
        objs = self.repo.get_fields_by_farm(farm_id, skip=skip, limit=limit)
        return [FieldOut.model_validate(o) for o in objs]

    def update_field(self, field_id: int, field_in: FieldUpdate) -> Optional[FieldOut]:
        obj = self.repo.get(field_id)
        if not obj:
            return None
        data = field_in.model_dump(exclude_unset=True)
        updated = self.repo.update(obj, data)
        return FieldOut.model_validate(updated)

    def delete_field(self, field_id: int) -> bool:
        obj = self.repo.get(field_id)
        if not obj:
            return False
        self.repo.remove(field_id)
        self.event_service.publish_event("field_deleted", {"id": field_id})
        return True
