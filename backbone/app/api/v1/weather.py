from app.services.weather_service import WeatherService
from app.api.deps import get_weather_service
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.weather import WeatherCreate, WeatherOut

router = APIRouter()

@router.post('/', response_model=WeatherOut, status_code=status.HTTP_201_CREATED)
def create_weather(weather_in: WeatherCreate, svc: WeatherService = Depends(get_weather_service)):
    return svc.create_weather(weather_in)

@router.get('/{weather_id}', response_model=WeatherOut)
def get_weather(weather_id: int, svc: WeatherService = Depends(get_weather_service)):
    obj = svc.get_weather(weather_id)
    if not obj:
        raise HTTPException(status_code=404, detail='Weather entry not found')
    return obj

@router.get('/', response_model=list[WeatherOut])
def list_weather(field_id: int | None = None, skip: int = 0, limit: int = 100, svc: WeatherService = Depends(get_weather_service)):
    return svc.list_weather(field_id=field_id, skip=skip, limit=limit)

@router.put('/{weather_id}', response_model=WeatherOut)
def update_weather(weather_id: int, weather_in: WeatherCreate, svc: WeatherService = Depends(get_weather_service)):
    obj = svc.update_weather(weather_id, weather_in)
    if not obj:
        raise HTTPException(status_code=404, detail='Weather entry not found')
    return obj

@router.delete('/{weather_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_weather(weather_id: int, svc: WeatherService = Depends(get_weather_service)):
    success = svc.delete_weather(weather_id)
    if not success:
        raise HTTPException(status_code=404, detail='Weather entry not found')
    return None
