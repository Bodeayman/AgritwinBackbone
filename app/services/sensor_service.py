from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.repositories.sensor_repository import SensorRepository
from app.schemas.sensor_reading import SensorCreate, SensorOut


class SensorService:
    def __init__(self, db: Session):
        self.repo = SensorRepository(db)

    def create_reading(self, reading_in: SensorCreate) -> SensorOut:
        from app.models.sensor_reading import SensorReading
        obj = SensorReading(
            field_id=reading_in.field_id,
            sensor_id=reading_in.sensor_id,
            recorded_at=reading_in.recorded_at or datetime.utcnow(),
            soil_moisture=reading_in.soil_moisture,
            soil_temperature=reading_in.soil_temperature,
            air_temperature=reading_in.air_temperature,
            humidity=reading_in.humidity,
            soil_ph=reading_in.soil_ph,
            electrical_conductivity=reading_in.electrical_conductivity,
        )
        self.repo.db.add(obj)
        self.repo.db.commit()
        self.repo.db.refresh(obj)
        return SensorOut.model_validate(obj)

    def get_reading(self, reading_id: int) -> Optional[SensorOut]:
        obj = self.repo.get_by_id(reading_id)
        return SensorOut.model_validate(obj) if obj else None

    def list_by_field(self, field_id: int, skip: int = 0, limit: int = 100) -> List[SensorOut]:
        objs = self.repo.list_by_field(field_id, skip=skip, limit=limit)
        return [SensorOut.model_validate(o) for o in objs]

    def list_by_field_date_range(
        self,
        field_id: int,
        from_dt: Optional[datetime] = None,
        to_dt: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[SensorOut]:
        objs = self.repo.list_by_field_date_range(field_id, from_dt, to_dt, skip=skip, limit=limit)
        return [SensorOut.model_validate(o) for o in objs]

    def delete_reading(self, reading_id: int) -> bool:
        obj = self.repo.get_by_id(reading_id)
        if not obj:
            return False
        self.repo.db.delete(obj)
        self.repo.db.commit()
        return True
