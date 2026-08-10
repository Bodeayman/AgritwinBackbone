from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.repositories.satellite_repository import SatelliteRepository
from app.schemas.satellite_data import SatelliteCreate, SatelliteOut


class SatelliteService:
    def __init__(self, db: Session):
        self.repo = SatelliteRepository(db)

    def create_satellite(self, sat_in: SatelliteCreate) -> SatelliteOut:
        from app.models.satellite_data import SatelliteData
        obj = SatelliteData(
            field_id=sat_in.field_id,
            ndvi=sat_in.ndvi,
            ndmi=sat_in.ndmi,
            captured_at=sat_in.captured_at or datetime.utcnow(),
        )
        obj = self.repo.create(obj)
        return SatelliteOut.model_validate(obj)

    def get_satellite(self, sat_id: int) -> Optional[SatelliteOut]:
        obj = self.repo.get(sat_id)
        return SatelliteOut.model_validate(obj) if obj else None

    def list_satellite(self, field_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[SatelliteOut]:
        if field_id:
            objs = self.repo.db.query(self.repo.model).filter(self.repo.model.field_id == field_id).offset(skip).limit(limit).all()
        else:
            objs = self.repo.get_multi(skip=skip, limit=limit)
        return [SatelliteOut.model_validate(o) for o in objs]

    def update_satellite(self, sat_id: int, sat_in: SatelliteCreate) -> Optional[SatelliteOut]:
        obj = self.repo.get(sat_id)
        if not obj:
            return None
        data = sat_in.model_dump(exclude_unset=True)
        updated = self.repo.update(obj, data)
        return SatelliteOut.model_validate(updated)

    def delete_satellite(self, sat_id: int) -> bool:
        obj = self.repo.get(sat_id)
        if not obj:
            return False
        self.repo.remove(sat_id)
        return True
