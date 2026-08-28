from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.satellite import Satellite


class SatelliteRepository(BaseRepository[Satellite]):
    def __init__(self, db: Session):
        super().__init__(Satellite, db)

    def get_by_name(self, name: str) -> Optional[Satellite]:
        return self.db.query(Satellite).filter(Satellite.name == name).first()

    def get_active(self, skip: int = 0, limit: int = 100) -> List[Satellite]:
        return self.db.query(Satellite).filter(Satellite.status == "active").offset(skip).limit(limit).all()

    def get_or_create_by_name(self, name: str, **kwargs) -> Satellite:
        existing = self.get_by_name(name)
        if existing:
            return existing
        satellite = Satellite(name=name, **kwargs)
        return self.create(satellite)
