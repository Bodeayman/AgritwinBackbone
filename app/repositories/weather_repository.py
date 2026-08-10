from app.repositories.base import BaseRepository
from app.models.weather import Weather

class WeatherRepository(BaseRepository[Weather]):
    def __init__(self, db):
        super().__init__(Weather, db)
