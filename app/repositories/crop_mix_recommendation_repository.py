from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.repositories.base import BaseRepository
from app.models.crop_mix_recommendation import CropMixRecommendation


class CropMixRecommendationRepository(BaseRepository[CropMixRecommendation]):
    def __init__(self, db: Session):
        super().__init__(CropMixRecommendation, db)

    def get_with_allocations(self, rec_id: int) -> Optional[CropMixRecommendation]:
        """Fetch a recommendation with its allocations eagerly loaded."""
        return (
            self.db.query(CropMixRecommendation)
            .options(joinedload(CropMixRecommendation.allocations))
            .filter(CropMixRecommendation.id == rec_id)
            .first()
        )

    def list_by_field(
        self,
        field_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[CropMixRecommendation]:
        return (
            self.db.query(CropMixRecommendation)
            .options(joinedload(CropMixRecommendation.allocations))
            .filter(CropMixRecommendation.field_id == field_id)
            .order_by(CropMixRecommendation.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_latest_by_field(self, field_id: int) -> Optional[CropMixRecommendation]:
        """Return the most recent recommendation for a field."""
        return (
            self.db.query(CropMixRecommendation)
            .options(joinedload(CropMixRecommendation.allocations))
            .filter(CropMixRecommendation.field_id == field_id)
            .order_by(CropMixRecommendation.created_at.desc())
            .first()
        )
