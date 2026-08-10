from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.repositories.satellite_observation_repository import SatelliteObservationRepository
from app.models.satellite_observation import SatelliteObservation
from app.schemas.satellite_observation import SatelliteObservationCreate, SatelliteObservationOut


class SatelliteObservationService:
    def __init__(self, db: Session):
        self.repo = SatelliteObservationRepository(db)

    def create(self, obs_in: SatelliteObservationCreate) -> SatelliteObservationOut:
        obj = SatelliteObservation(
            field_id=obs_in.field_id,
            model_id=obs_in.model_id,
            status=obs_in.status,
            ndvi=obs_in.ndvi,
            ndmi=obs_in.ndmi,
            evi=obs_in.evi,
            image_reference=obs_in.image_reference,
            captured_at=obs_in.captured_at,
        )
        self.repo.db.add(obj)
        self.repo.db.commit()
        self.repo.db.refresh(obj)
        return SatelliteObservationOut.model_validate(obj)

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
