from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session, selectinload
from app.repositories.satellite_observation_repository import SatelliteObservationRepository
from app.models.satellite_observation import SatelliteObservation
from app.schemas.satellite_observation import SatelliteObservationCreate, SatelliteObservationOut


class SatelliteObservationService:
    def __init__(self, db: Session):
        self.repo = SatelliteObservationRepository(db)

    def create(self, obs_in: SatelliteObservationCreate) -> SatelliteObservationOut:
        obj = SatelliteObservation(
            field_id=obs_in.field_id,
            satellite_id=obs_in.satellite_id,
            model_id=obs_in.model_id,
            imagery_id=obs_in.imagery_id,
            observation_type=obs_in.observation_type,
            cloud_cover_pct=obs_in.cloud_cover_pct,
            status=obs_in.status,
            ndvi=obs_in.ndvi,
            ndmi=obs_in.ndmi,
            evi=obs_in.evi,
            captured_at=obs_in.captured_at,
            additional_metadata=obs_in.additional_metadata,
        )
        self.repo.db.add(obj)
        self.repo.db.commit()
        self.repo.db.refresh(obj)
        # Populate relationships for the response
        obj_with_relations = self.repo.db.query(SatelliteObservation).options(
            selectinload(SatelliteObservation.ai_model),
            selectinload(SatelliteObservation.satellite),
            selectinload(SatelliteObservation.imagery)
        ).filter(SatelliteObservation.id == obj.id).first()
        return SatelliteObservationOut.model_validate(obj_with_relations)

    def get(self, obs_id: int) -> Optional[SatelliteObservationOut]:
        obj = self.repo.get(obs_id)
        return SatelliteObservationOut.model_validate(obj) if obj else None

    def list_by_field(
        self,
        field_id: int,
        from_dt: Optional[datetime] = None,
        to_dt: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[SatelliteObservationOut]:
        objs = self.repo.list_by_field(field_id, from_dt, to_dt, skip=skip, limit=limit)
        return [SatelliteObservationOut.model_validate(o) for o in objs]

    def delete(self, obs_id: int) -> bool:
        obj = self.repo.get(obs_id)
        if not obj:
            return False
        self.repo.db.delete(obj)
        self.repo.db.commit()
        return True
