from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.satellite_observation import SatelliteObservation


class SatelliteObservationRepository(BaseRepository[SatelliteObservation]):
    def __init__(self, db: Session):
        super().__init__(SatelliteObservation, db)

    def list_by_field(
        self,
        field_id: int,
        from_dt: Optional[datetime] = None,
        to_dt: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[SatelliteObservation]:
        q = self.db.query(SatelliteObservation).filter(SatelliteObservation.field_id == field_id)
        if from_dt:
            q = q.filter(SatelliteObservation.captured_at >= from_dt)
        if to_dt:
            q = q.filter(SatelliteObservation.captured_at <= to_dt)
        return q.order_by(SatelliteObservation.captured_at.desc()).offset(skip).limit(limit).all()
