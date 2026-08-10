from typing import List, Optional

from sqlalchemy.orm import Session

from app.repositories.crop_cycle_repository import CropCycleRepository
from app.models.crop_cycle import CropCycle
from app.schemas.crop_cycle import CropCycleCreate, CropCycleUpdate, CropCycleOut

class CropCycleService:
    """Service layer for CropCycle CRUD operations.

    It delegates persistence to :class:`CropCycleRepository` and returns
    Pydantic schema objects for FastAPI responses.
    """

    def __init__(self, db: Session):
        self.repo = CropCycleRepository(db)

    def create_crop_cycle(self, cc_in: CropCycleCreate) -> CropCycleOut:
        """Create a new crop cycle record.

        Args:
            cc_in: validated request payload.
        Returns:
            CropCycleOut schema representing the persisted record.
        """
        crop_cycle = CropCycle(
            field_id=cc_in.field_id,
            crop=cc_in.crop,
            planting_date=cc_in.planting_date,
            expected_harvest_date=cc_in.expected_harvest_date,
            actual_harvest_date=cc_in.actual_harvest_date,
            status=cc_in.status,
        )
        obj = self.repo.create(crop_cycle)
        return CropCycleOut.model_validate(obj)

    def get_crop_cycle(self, crop_cycle_id: int) -> Optional[CropCycleOut]:
        obj = self.repo.get(crop_cycle_id)
        return CropCycleOut.model_validate(obj) if obj else None

    def list_crop_cycles(self, skip: int = 0, limit: int = 100) -> List[CropCycleOut]:
        objs = self.repo.list_crop_cycles(skip=skip, limit=limit)
        return [CropCycleOut.model_validate(o) for o in objs]

    def update_crop_cycle(self, crop_cycle_id: int, cc_in: CropCycleUpdate) -> Optional[CropCycleOut]:
        obj = self.repo.get(crop_cycle_id)
        if not obj:
            return None
        data = cc_in.model_dump(exclude_unset=True)
        updated = self.repo.update(obj, data)
        return CropCycleOut.model_validate(updated)

    def delete_crop_cycle(self, crop_cycle_id: int) -> bool:
        return self.repo.delete(crop_cycle_id)
