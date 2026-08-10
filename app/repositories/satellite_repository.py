from app.repositories.base import BaseRepository
from app.models.satellite_data import SatelliteData

class SatelliteRepository(BaseRepository[SatelliteData]):
    def __init__(self, db):
        super().__init__(SatelliteData, db)
