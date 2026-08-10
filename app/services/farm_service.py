from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.farm_repository import FarmRepository
from app.models.farm import Farm
from app.schemas.farm import FarmCreate, FarmUpdate, FarmOut


class FarmService:
    def __init__(self, db: Session):
        self.repo = FarmRepository(db)

    def create_farm(self, farm_in: FarmCreate, owner_id: int) -> FarmOut:
        """owner_id is passed explicitly from the JWT token, not from the request body."""
        farm = Farm(
            owner_id=owner_id,
            name=farm_in.name,
            location=farm_in.location,
        )
        obj = self.repo.create(farm)
        return FarmOut.model_validate(obj)

    def get_farm(self, farm_id: int) -> Optional[FarmOut]:
        obj = self.repo.get(farm_id)
        return FarmOut.model_validate(obj) if obj else None

    def list_farms(self, skip: int = 0, limit: int = 100) -> List[FarmOut]:
        objs = self.repo.list_farms(skip=skip, limit=limit)
        return [FarmOut.model_validate(o) for o in objs]

    def list_farms_by_owner(self, owner_id: int, skip: int = 0, limit: int = 100) -> List[FarmOut]:
        """Return only the farms that belong to the authenticated farmer."""
        objs = self.repo.list_by_owner(owner_id, skip=skip, limit=limit)
        return [FarmOut.model_validate(o) for o in objs]

    def update_farm(self, farm_id: int, farm_in: FarmUpdate) -> Optional[FarmOut]:
        obj = self.repo.get(farm_id)
        if not obj:
            return None
        data = farm_in.model_dump(exclude_unset=True)
        updated = self.repo.update(obj, data)
        return FarmOut.model_validate(updated)

    def delete_farm(self, farm_id: int) -> bool:
        obj = self.repo.get(farm_id)
        if not obj:
            return False
        self.repo.remove(farm_id)
        return True
