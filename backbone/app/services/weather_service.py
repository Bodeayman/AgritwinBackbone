from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.repositories.weather_repository import WeatherRepository
from app.schemas.weather import WeatherCreate, WeatherOut

class WeatherService:
    def __init__(self, db: Session):
        self.repo = WeatherRepository(db)

    def create_weather(self, weather_in: WeatherCreate) -> WeatherOut:
        from app.models.weather import Weather
        obj = Weather(
            field_id=weather_in.field_id,
            temperature=weather_in.temperature,
            humidity=weather_in.humidity,
            rainfall=weather_in.rainfall,
            forecast_rain=weather_in.forecast_rain,
            pressure=weather_in.pressure,
            recorded_at=weather_in.recorded_at or datetime.utcnow(),
        )
        obj = self.repo.create(obj)
        return WeatherOut.model_validate(obj)

    def get_weather(self, weather_id: int) -> Optional[WeatherOut]:
        obj = self.repo.get(weather_id)
        return WeatherOut.model_validate(obj) if obj else None

    def list_weather(self, field_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[WeatherOut]:
        if field_id:
            objs = self.repo.db.query(self.repo.model).filter(self.repo.model.field_id == field_id).offset(skip).limit(limit).all()
        else:
            objs = self.repo.get_multi(skip=skip, limit=limit)
        return [WeatherOut.model_validate(o) for o in objs]

    def list_by_field_date_range(
        self,
        field_id: int,
        from_dt: Optional[datetime] = None,
        to_dt: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[WeatherOut]:
        query = self.repo.db.query(self.repo.model).filter(self.repo.model.field_id == field_id)
        if from_dt:
            query = query.filter(self.repo.model.recorded_at >= from_dt)
        if to_dt:
            query = query.filter(self.repo.model.recorded_at <= to_dt)
        objs = query.offset(skip).limit(limit).all()
        return [WeatherOut.model_validate(o) for o in objs]

    def update_weather(self, weather_id: int, weather_in: WeatherCreate) -> Optional[WeatherOut]:
        obj = self.repo.get(weather_id)
        if not obj:
            return None
        data = weather_in.model_dump(exclude_unset=True)
        updated = self.repo.update(obj, data)
        return WeatherOut.model_validate(updated)

    def delete_weather(self, weather_id: int) -> bool:
        obj = self.repo.get(weather_id)
        if not obj:
            return False
        self.repo.remove(weather_id)
        return True
