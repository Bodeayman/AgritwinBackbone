from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.sensor_reading import SensorReading


class SensorRepository(BaseRepository[SensorReading]):
    def __init__(self, db: Session):
        super().__init__(SensorReading, db)

    def get_by_id(self, reading_id: int) -> Optional[SensorReading]:
        return self.db.get(SensorReading, reading_id)

    def list_by_field(self, field_id: int, skip: int = 0, limit: int = 100) -> List[SensorReading]:
        return (
            self.db.query(SensorReading)
            .filter(SensorReading.field_id == field_id)
            .order_by(SensorReading.recorded_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_by_field_date_range(
        self,
        field_id: int,
        from_dt: Optional[datetime] = None,
        to_dt: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[SensorReading]:
        q = self.db.query(SensorReading).filter(SensorReading.field_id == field_id)
        if from_dt:
            q = q.filter(SensorReading.recorded_at >= from_dt)
        if to_dt:
            q = q.filter(SensorReading.recorded_at <= to_dt)
        return q.order_by(SensorReading.recorded_at.desc()).offset(skip).limit(limit).all()
