from typing import List, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.repositories.crop_cycle_repository import CropCycleRepository
from app.models.crop_cycle import CropCycle
from app.schemas.crop_cycle import CropCycleCreate, CropCycleUpdate, CropCycleOut


class CropCycleService:
    """Service layer for CropCycle CRUD operations.

    It delegates persistence to :class:`CropCycleRepository` and returns
    Pydantic schema objects for FastAPI responses.

    The ``planted_at`` timestamp is set automatically on creation (using the
    caller-supplied value if provided, otherwise the current UTC time).  When
    the ``crop`` field is changed via an update, ``planted_at`` is refreshed to
    *now* unless the caller explicitly passes a new value.
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
            # Use the caller-supplied timestamp or fall back to now.
            planted_at=cc_in.planted_at or datetime.utcnow(),
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

        # If the crop type changed and no explicit planted_at was supplied,
        # automatically refresh the timestamp to now.
        if "crop" in data and data["crop"] != obj.crop and "planted_at" not in data:
            data["planted_at"] = datetime.utcnow()

        updated = self.repo.update(obj, data)
        return CropCycleOut.model_validate(updated)

    def delete_crop_cycle(self, crop_cycle_id: int) -> bool:
        return self.repo.delete(crop_cycle_id)
