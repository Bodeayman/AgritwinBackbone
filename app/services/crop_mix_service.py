from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.crop_mix_recommendation_repository import CropMixRecommendationRepository
from app.models.crop_mix_recommendation import CropMixRecommendation
from app.models.crop_mix_allocation import CropMixAllocation
from app.schemas.crop_mix_recommendation import (
    CropMixRecommendationCreate,
    CropMixRecommendationOut,
)


class CropMixService:
    def __init__(self, db: Session):
        self.repo = CropMixRecommendationRepository(db)

    def create(self, rec_in: CropMixRecommendationCreate) -> CropMixRecommendationOut:
        """Create a recommendation and all its allocations in a single transaction."""
        rec = CropMixRecommendation(
            field_id=rec_in.field_id,
            model_id=rec_in.model_id,
            status=rec_in.status,
            expected_profit=rec_in.expected_profit,
            binding_constraint=rec_in.binding_constraint,
        )
        self.repo.db.add(rec)
        self.repo.db.flush()  # get rec.id before committing

        for alloc_in in rec_in.allocations:
            alloc = CropMixAllocation(
                recommendation_id=rec.id,
                crop_type=alloc_in.crop_type,
                allocated_area=alloc_in.allocated_area,
                unit=alloc_in.unit,
            )
            self.repo.db.add(alloc)

        self.repo.db.commit()
        self.repo.db.refresh(rec)
        return CropMixRecommendationOut.model_validate(rec)

    def get(self, rec_id: int) -> Optional[CropMixRecommendationOut]:
        obj = self.repo.get_with_allocations(rec_id)
        return CropMixRecommendationOut.model_validate(obj) if obj else None

    def list_by_field(
        self, field_id: int, skip: int = 0, limit: int = 100
    ) -> List[CropMixRecommendationOut]:
        objs = self.repo.list_by_field(field_id, skip=skip, limit=limit)
        return [CropMixRecommendationOut.model_validate(o) for o in objs]

    def get_latest_by_field(self, field_id: int) -> Optional[CropMixRecommendationOut]:
        obj = self.repo.get_latest_by_field(field_id)
        return CropMixRecommendationOut.model_validate(obj) if obj else None

    def delete(self, rec_id: int) -> bool:
        obj = self.repo.get(rec_id)
        if not obj:
            return False
        self.repo.db.delete(obj)
        self.repo.db.commit()
        return True
