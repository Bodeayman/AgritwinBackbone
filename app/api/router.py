from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.api.v1 import (
    auth,
    farms,
    fields,
    crop_cycles,
    images,
    events,
    weather,
    satellite_observations,
    diagnoses,
    sensor_readings,
    irrigation_plans,
    yield_predictions,
    crop_mix_recommendations,
    imagery,
    satellites,
    crop_catalog,
    crop_rotation,
    optimization,
)

api_router = APIRouter()

# Public Auth routes
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])

# Protected routes (require user authentication)
api_router.include_router(farms.router, prefix="/farms", tags=["Farms"], dependencies=[Depends(get_current_user)])
api_router.include_router(fields.router, prefix="/fields", tags=["Fields"], dependencies=[Depends(get_current_user)])
api_router.include_router(crop_cycles.router, prefix="/crop-cycles", tags=["CropCycles"], dependencies=[Depends(get_current_user)])
api_router.include_router(images.router, prefix="/images", tags=["Images"], dependencies=[Depends(get_current_user)])
api_router.include_router(events.router, prefix="/events", tags=["Events"], dependencies=[Depends(get_current_user)])
api_router.include_router(weather.router, prefix="/weather", tags=["Weather"], dependencies=[Depends(get_current_user)])
api_router.include_router(sensor_readings.router, prefix="/sensor-readings", tags=["SensorReadings"], dependencies=[Depends(get_current_user)])
api_router.include_router(satellite_observations.router, prefix="/satellite-observations", tags=["SatelliteObservations"], dependencies=[Depends(get_current_user)])
api_router.include_router(diagnoses.router, prefix="/diagnoses", tags=["Diagnoses"], dependencies=[Depends(get_current_user)])
api_router.include_router(irrigation_plans.router, prefix="/irrigation-plans", tags=["IrrigationPlans"], dependencies=[Depends(get_current_user)])
api_router.include_router(yield_predictions.router, prefix="/yield-predictions", tags=["YieldPredictions"], dependencies=[Depends(get_current_user)])
api_router.include_router(crop_mix_recommendations.router, prefix="/crop-mix-recommendations", tags=["CropMixRecommendations"], dependencies=[Depends(get_current_user)])
api_router.include_router(crop_catalog.router, prefix="/crop-catalog", tags=["CropCatalog"], dependencies=[Depends(get_current_user)])
api_router.include_router(crop_rotation.router, prefix="/crop-rotation", tags=["CropRotation"], dependencies=[Depends(get_current_user)])
api_router.include_router(optimization.router, prefix="/optimization", tags=["Optimization"], dependencies=[Depends(get_current_user)])
api_router.include_router(imagery.router, prefix="/imagery", tags=["Imagery"], dependencies=[Depends(get_current_user)])
api_router.include_router(satellites.router, prefix="/satellites", tags=["Satellites"], dependencies=[Depends(get_current_user)])
