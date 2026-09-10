from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.crop_mix_recommendation_repository import CropMixRecommendationRepository
from app.models.crop_mix_recommendation import CropMixRecommendation
from app.models.crop_mix_allocation import CropMixAllocation
from app.models.field import Field
from app.schemas.crop_mix_recommendation import (
    CropMixRecommendationCreate,
    CropMixRecommendationOut,
)


class CropMixService:
    def __init__(self, db: Session):
        self.repo = CropMixRecommendationRepository(db)

    def create(self, rec_in: CropMixRecommendationCreate) -> CropMixRecommendationOut:
        """Create an optimization plan and all its field allocations in a single transaction."""
        rec = CropMixRecommendation(
            farm_id=rec_in.farm_id,
            model_id=rec_in.model_id,
            season=rec_in.season,
            optimizer_version=rec_in.optimizer_version,
            status=rec_in.status,
            is_feasible=rec_in.is_feasible,
            total_land_used_feddans=rec_in.total_land_used_feddans,
            total_water_used_m3=rec_in.total_water_used_m3,
            total_labor_used_hours=rec_in.total_labor_used_hours,
            total_fertilizer_used_kg=rec_in.total_fertilizer_used_kg,
            total_expected_revenue_egp=rec_in.total_expected_revenue_egp,
            total_production_cost_egp=rec_in.total_production_cost_egp,
            total_labor_cost_egp=rec_in.total_labor_cost_egp,
            total_fertilizer_cost_egp=rec_in.total_fertilizer_cost_egp,
            net_profit_egp=rec_in.net_profit_egp,
            binding_constraints=rec_in.binding_constraints,
            ai_synthesis_explanation=rec_in.ai_synthesis_explanation,
        )
        self.repo.db.add(rec)
        self.repo.db.flush()  # get rec.id before committing

        for alloc_in in rec_in.allocations:
            alloc = CropMixAllocation(
                recommendation_id=rec.id,
                field_id=alloc_in.field_id,
                crop_id=alloc_in.crop_id,
                allocated_area_feddans=alloc_in.allocated_area_feddans,
                expected_profit_contribution_egp=alloc_in.expected_profit_contribution_egp,
            )
            self.repo.db.add(alloc)

        self.repo.db.commit()
        self.repo.db.refresh(rec)
        return CropMixRecommendationOut.model_validate(rec)

    def get(self, rec_id: int) -> Optional[CropMixRecommendationOut]:
        obj = self.repo.get_with_allocations(rec_id)
        return CropMixRecommendationOut.model_validate(obj) if obj else None

    def list_by_farm(
        self, farm_id: int, skip: int = 0, limit: int = 100
    ) -> List[CropMixRecommendationOut]:
        objs = self.repo.list_by_farm(farm_id, skip=skip, limit=limit)
        return [CropMixRecommendationOut.model_validate(o) for o in objs]

    def get_latest_by_farm(self, farm_id: int) -> Optional[CropMixRecommendationOut]:
        obj = self.repo.get_latest_by_farm(farm_id)
        return CropMixRecommendationOut.model_validate(obj) if obj else None

    def _resolve_farm_id(self, field_id: int) -> Optional[int]:
        field = self.repo.db.query(Field).filter(Field.id == field_id).first()
        return field.farm_id if field else None

    def list_by_field(
        self, field_id: int, skip: int = 0, limit: int = 100
    ) -> List[CropMixRecommendationOut]:
        farm_id = self._resolve_farm_id(field_id)
        if farm_id is None:
            return []
        return self.list_by_farm(farm_id, skip=skip, limit=limit)

    def get_latest_by_field(self, field_id: int) -> Optional[CropMixRecommendationOut]:
        farm_id = self._resolve_farm_id(field_id)
        if farm_id is None:
            return None
        return self.get_latest_by_farm(farm_id)

    def delete(self, rec_id: int) -> bool:
        obj = self.repo.get(rec_id)
        if not obj:
            return False
        self.repo.db.delete(obj)
        self.repo.db.commit()
        return True
