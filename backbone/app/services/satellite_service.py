from typing import List, Optional
from sqlalchemy.orm import Session, selectinload
from app.repositories.satellite_repository import SatelliteRepository
from app.models.satellite import Satellite
from app.schemas.satellite import SatelliteCreate, SatelliteUpdate, SatelliteOut


class SatelliteService:
    def __init__(self, db: Session):
        self.repo = SatelliteRepository(db)

    def create(self, satellite_in: SatelliteCreate) -> SatelliteOut:
        obj = Satellite(
            name=satellite_in.name,
            operator=satellite_in.operator,
            launch_date=satellite_in.launch_date,
            sensor_type=satellite_in.sensor_type,
            resolution_m=satellite_in.resolution_m,
            revisit_period_days=satellite_in.revisit_period_days,
            status=satellite_in.status,
            description=satellite_in.description,
        )
        self.repo.db.add(obj)
        self.repo.db.commit()
        self.repo.db.refresh(obj)
        return SatelliteOut.model_validate(obj)

    def get(self, satellite_id: int) -> Optional[SatelliteOut]:
        obj = self.repo.get(satellite_id)
        return SatelliteOut.model_validate(obj) if obj else None

    def get_with_observations(self, satellite_id: int) -> Optional[SatelliteOut]:
        """Get satellite with its observations loaded."""
        from app.models.satellite_observation import SatelliteObservation
        obj = self.repo.db.query(Satellite).options(
            selectinload(Satellite.observations)
        ).filter(Satellite.id == satellite_id).first()
        return SatelliteOut.model_validate(obj) if obj else None

    def get_by_name(self, name: str) -> Optional[SatelliteOut]:
        obj = self.repo.get_by_name(name)
        return SatelliteOut.model_validate(obj) if obj else None

    def list(self, skip: int = 0, limit: int = 100) -> List[SatelliteOut]:
        objs = self.repo.get_multi(skip=skip, limit=limit)
        return [SatelliteOut.model_validate(o) for o in objs]

    def list_all(self, skip: int = 0, limit: int = 100) -> List[SatelliteOut]:
        objs = self.repo.get_multi(skip=skip, limit=limit)
        return [SatelliteOut.model_validate(o) for o in objs]

    def list_active(self, skip: int = 0, limit: int = 100) -> List[SatelliteOut]:
        objs = self.repo.get_active(skip=skip, limit=limit)
        return [SatelliteOut.model_validate(o) for o in objs]

    def get_or_create(self, name: str, **kwargs) -> SatelliteOut:
        obj = self.repo.get_or_create_by_name(name, **kwargs)
        return SatelliteOut.model_validate(obj)

    def update(self, satellite_id: int, satellite_in: SatelliteUpdate) -> Optional[SatelliteOut]:
        obj = self.repo.get(satellite_id)
        if not obj:
            return None
        
        update_data = satellite_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(obj, field, value)
        
        self.repo.db.commit()
        self.repo.db.refresh(obj)
        return SatelliteOut.model_validate(obj)

    def delete(self, satellite_id: int) -> bool:
        obj = self.repo.get(satellite_id)
        if not obj:
            return False
        self.repo.db.delete(obj)
        self.repo.db.commit()
        return True
