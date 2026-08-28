from typing import List, Optional
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.storage import StorageService, get_storage
from app.core.config import settings

from app.services.image_processing_service import ImageProcessingService
from app.services.event_service import EventService
from app.services.location_service import LocationService
from app.services.farm_service import FarmService
from app.services.field_service import FieldService
from app.services.field_boundary_service import FieldBoundaryService
from app.services.crop_cycle_service import CropCycleService
from app.services.auth_service import AuthService
from app.services.sensor_service import SensorService
from app.services.satellite_observation_service import SatelliteObservationService
from app.services.diagnosis_service import DiagnosisService
from app.services.irrigation_plan_service import IrrigationPlanService
from app.services.yield_prediction_service import YieldPredictionService
from app.services.crop_mix_service import CropMixService
from app.services.weather_service import WeatherService
from app.services.ai_model_service import AIModelService
from app.services.imagery_service import ImageryService
from app.services.satellite_service import SatelliteService
from app.core.security import decode_access_token
from app.models.user import User


# ── Service providers ─────────────────────────────────────────────────────────

def get_image_service() -> ImageProcessingService:
    return ImageProcessingService()

def get_event_service() -> EventService:
    return EventService()

def get_location_service(
    db: Session = Depends(get_db),
    storage: StorageService = Depends(get_storage)
) -> LocationService:
    return LocationService(db, storage)

def get_farm_service(db: Session = Depends(get_db)) -> FarmService:
    return FarmService(db)

def get_field_service(db: Session = Depends(get_db)) -> FieldService:
    return FieldService(db)

def get_field_boundary_service(db: Session = Depends(get_db)) -> FieldBoundaryService:
    return FieldBoundaryService(db)

def get_crop_cycle_service(db: Session = Depends(get_db)) -> CropCycleService:
    return CropCycleService(db)

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

def get_sensor_service(db: Session = Depends(get_db)) -> SensorService:
    return SensorService(db)

def get_satellite_observation_service(db: Session = Depends(get_db)) -> SatelliteObservationService:
    return SatelliteObservationService(db)

def get_diagnosis_service(db: Session = Depends(get_db)) -> DiagnosisService:
    return DiagnosisService(db)

def get_irrigation_plan_service(db: Session = Depends(get_db)) -> IrrigationPlanService:
    return IrrigationPlanService(db)

def get_yield_prediction_service(db: Session = Depends(get_db)) -> YieldPredictionService:
    return YieldPredictionService(db)

def get_crop_mix_service(db: Session = Depends(get_db)) -> CropMixService:
    return CropMixService(db)

def get_weather_service(db: Session = Depends(get_db)) -> WeatherService:
    return WeatherService(db)

def get_ai_model_service(db: Session = Depends(get_db)) -> AIModelService:
    return AIModelService(db)


def get_imagery_service(db: Session = Depends(get_db)) -> ImageryService:
    return ImageryService(db)


def get_satellite_service(db: Session = Depends(get_db)) -> SatelliteService:
    return SatelliteService(db)


# ── Internal Module API-Key authentication ────────────────────────────────────

def verify_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> str:
    """Validate internal module API key from X-API-Key header.
    Returns calling module identifier if valid, raises 401 if invalid/missing.
    Never logs or exposes API keys.
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key",
        )
    valid_keys = {
        settings.INTERN_2_API_KEY: "intern_2",
        settings.INTERN_3_API_KEY: "intern_3",
        settings.INTERN_4A_API_KEY: "intern_4a",
        settings.INTERN_4B_API_KEY: "intern_4b",
        settings.INTERN_5_API_KEY: "intern_5",
        settings.INTERN_7_API_KEY: "intern_7",
        settings.INTERN_8_API_KEY: "intern_8",
    }
    module = valid_keys.get(x_api_key)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key",
        )
    return module


# ── JWT authentication (farmer-facing routes) ─────────────────────────────────

security_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Extract and validate JWT Bearer token; return the authenticated User.
    Expected header: Authorization: Bearer <JWT>
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid token",
        )
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
