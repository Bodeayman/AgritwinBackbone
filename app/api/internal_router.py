from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Form
from pydantic import BaseModel, Field as PydanticField

from app.api.deps import (
    verify_api_key,
    get_field_service,
    get_field_boundary_service,
    get_farm_service,
    get_sensor_service,
    get_satellite_observation_service,
    get_diagnosis_service,
    get_irrigation_plan_service,
    get_yield_prediction_service,
    get_crop_mix_service,
    get_ai_model_service,
)
from app.core.local_storage import get_local_image_storage, LocalDiskImageStorage

from app.schemas.field import FieldOut
from app.schemas.field_boundary import FieldBoundaryOut
from app.schemas.sensor_reading import SensorCreate, SensorOut
from app.schemas.satellite_observation import SatelliteObservationCreate, SatelliteObservationOut
from app.schemas.diagnosis import DiagnosisCreate, DiagnosisOut
from app.schemas.irrigation_plan import IrrigationPlanCreate, IrrigationPlanOut
from app.schemas.yield_prediction import YieldPredictionCreate, YieldPredictionOut
from app.schemas.crop_mix_recommendation import CropMixRecommendationCreate, CropMixRecommendationOut
from app.schemas.ai_model import AIModelCreate, AIModelOut
from app.services.field_service import FieldService
from app.services.field_boundary_service import FieldBoundaryService
from app.services.farm_service import FarmService
from app.services.sensor_service import SensorService
from app.services.satellite_observation_service import SatelliteObservationService
from app.services.diagnosis_service import DiagnosisService
from app.services.irrigation_plan_service import IrrigationPlanService
from app.services.yield_prediction_service import YieldPredictionService
from app.services.crop_mix_service import CropMixService
from app.services.ai_model_service import AIModelService

internal_router = APIRouter(dependencies=[Depends(verify_api_key)])


def _assert_field_exists(field_id: int, field_svc: FieldService):
    field = field_svc.get_field(field_id)
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field with ID {field_id} does not exist",
        )
    return field


def _assert_farm_exists(farm_id: int, farm_svc: FarmService):
    farm = farm_svc.get_farm(farm_id)
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {farm_id} does not exist",
        )
    return farm


# ── AI MODEL ENTITY MANAGEMENT ───────────────────────────────────────────────

@internal_router.post(
    "/models",
    response_model=AIModelOut,
    status_code=status.HTTP_201_CREATED,
    summary="[Internal] Register/get an AI model entity",
    tags=["Internal AI Models"],
)
def create_or_get_ai_model(
    model_in: AIModelCreate,
    ai_model_svc: AIModelService = Depends(get_ai_model_service),
):
    """Register or fetch an AI/ML Model entity by name and version."""
    return ai_model_svc.create_model(model_in)


@internal_router.get(
    "/models",
    response_model=List[AIModelOut],
    summary="[Internal] List registered AI models",
    tags=["Internal AI Models"],
)
def list_ai_models(
    skip: int = 0,
    limit: int = 100,
    ai_model_svc: AIModelService = Depends(get_ai_model_service),
):
    return ai_model_svc.list_models(skip=skip, limit=limit)


# ── INGESTION ENDPOINTS ───────────────────────────────────────────────────────

@internal_router.post(
    "/fields/{field_id}/sensor-readings",
    response_model=SensorOut,
    status_code=status.HTTP_201_CREATED,
    summary="[Internal] Ingest sensor reading for field",
    tags=["Internal Ingestion"],
)
def ingest_sensor_reading(
    field_id: int,
    reading_in: SensorCreate,
    field_svc: FieldService = Depends(get_field_service),
    sensor_svc: SensorService = Depends(get_sensor_service),
):
    _assert_field_exists(field_id, field_svc)
    reading_in.field_id = field_id
    return sensor_svc.create_reading(reading_in)


@internal_router.post(
    "/fields/{field_id}/satellite-observations",
    response_model=SatelliteObservationOut,
    status_code=status.HTTP_201_CREATED,
    summary="[Internal] Ingest satellite observation for field",
    tags=["Internal Ingestion"],
)
def ingest_satellite_observation(
    field_id: int,
    obs_in: SatelliteObservationCreate,
    field_svc: FieldService = Depends(get_field_service),
    sat_svc: SatelliteObservationService = Depends(get_satellite_observation_service),
    ai_model_svc: AIModelService = Depends(get_ai_model_service),
):
    _assert_field_exists(field_id, field_svc)
    obs_in.field_id = field_id
    obs_in.model_id = ai_model_svc.resolve_model_id(obs_in.model_id, obs_in.model_name, obs_in.model_version)
    return sat_svc.create(obs_in)


@internal_router.post(
    "/fields/{field_id}/diagnoses",
    response_model=DiagnosisOut,
    status_code=status.HTTP_201_CREATED,
    summary="[Internal] Ingest disease/pest diagnosis for field",
    tags=["Internal Ingestion"],
)
def ingest_diagnosis(
    field_id: int,
    diag_in: DiagnosisCreate,
    field_svc: FieldService = Depends(get_field_service),
    diag_svc: DiagnosisService = Depends(get_diagnosis_service),
    ai_model_svc: AIModelService = Depends(get_ai_model_service),
):
    _assert_field_exists(field_id, field_svc)
    diag_in.field_id = field_id
    diag_in.model_id = ai_model_svc.resolve_model_id(diag_in.model_id, diag_in.model_name, diag_in.model_version)
    return diag_svc.create(diag_in)


@internal_router.post(
    "/fields/{field_id}/irrigation-plans",
    response_model=IrrigationPlanOut,
    status_code=status.HTTP_201_CREATED,
    summary="[Internal] Ingest irrigation plan for field",
    tags=["Internal Ingestion"],
)
def ingest_irrigation_plan(
    field_id: int,
    plan_in: IrrigationPlanCreate,
    field_svc: FieldService = Depends(get_field_service),
    plan_svc: IrrigationPlanService = Depends(get_irrigation_plan_service),
    ai_model_svc: AIModelService = Depends(get_ai_model_service),
):
    _assert_field_exists(field_id, field_svc)
    plan_in.field_id = field_id
    plan_in.model_id = ai_model_svc.resolve_model_id(plan_in.model_id, plan_in.model_name, plan_in.model_version)
    return plan_svc.create(plan_in)


@internal_router.post(
    "/fields/{field_id}/yield-predictions",
    response_model=YieldPredictionOut,
    status_code=status.HTTP_201_CREATED,
    summary="[Internal] Ingest yield prediction for field",
    tags=["Internal Ingestion"],
)
def ingest_yield_prediction(
    field_id: int,
    pred_in: YieldPredictionCreate,
    field_svc: FieldService = Depends(get_field_service),
    pred_svc: YieldPredictionService = Depends(get_yield_prediction_service),
    ai_model_svc: AIModelService = Depends(get_ai_model_service),
):
    _assert_field_exists(field_id, field_svc)
    pred_in.field_id = field_id
    pred_in.model_id = ai_model_svc.resolve_model_id(pred_in.model_id, pred_in.model_name, pred_in.model_version)
    return pred_svc.create(pred_in)


@internal_router.post(
    "/fields/{field_id}/crop-mix-recommendations",
    response_model=CropMixRecommendationOut,
    status_code=status.HTTP_201_CREATED,
    summary="[Internal] Ingest crop-mix recommendation for field",
    tags=["Internal Ingestion"],
)
def ingest_crop_mix_recommendation(
    field_id: int,
    rec_in: CropMixRecommendationCreate,
    field_svc: FieldService = Depends(get_field_service),
    crop_mix_svc: CropMixService = Depends(get_crop_mix_service),
    ai_model_svc: AIModelService = Depends(get_ai_model_service),
):
    _assert_field_exists(field_id, field_svc)
    rec_in.field_id = field_id
    rec_in.model_id = ai_model_svc.resolve_model_id(rec_in.model_id, rec_in.model_name, rec_in.model_version)
    return crop_mix_svc.create(rec_in)


# ── READ ENDPOINTS ────────────────────────────────────────────────────────────

@internal_router.get(
    "/fields/{field_id}",
    response_model=FieldOut,
    summary="[Internal] Get field details",
    tags=["Internal Read"],
)
def get_internal_field(
    field_id: int,
    field_svc: FieldService = Depends(get_field_service),
):
    return _assert_field_exists(field_id, field_svc)


@internal_router.get(
    "/fields/{field_id}/boundary",
    response_model=Optional[FieldBoundaryOut],
    summary="[Internal] Get field boundary polygon and area",
    tags=["Internal Read"],
)
def get_internal_field_boundary(
    field_id: int,
    field_svc: FieldService = Depends(get_field_service),
    boundary_svc: FieldBoundaryService = Depends(get_field_boundary_service),
):
    _assert_field_exists(field_id, field_svc)
    return boundary_svc.get_boundary(field_id)


@internal_router.get(
    "/fields/{field_id}/sensor-readings",
    response_model=List[SensorOut],
    summary="[Internal] Get field sensor readings (historical / date-range)",
    tags=["Internal Read"],
)
def get_internal_sensor_readings(
    field_id: int,
    from_dt: Optional[datetime] = Query(None, alias="from"),
    to_dt: Optional[datetime] = Query(None, alias="to"),
    latest: bool = Query(False, description="If true, returns only the latest record"),
    skip: int = 0,
    limit: int = 100,
    field_svc: FieldService = Depends(get_field_service),
    sensor_svc: SensorService = Depends(get_sensor_service),
):
    _assert_field_exists(field_id, field_svc)
    if latest:
        skip, limit = 0, 1
    if from_dt or to_dt:
        return sensor_svc.list_by_field_date_range(field_id, from_dt, to_dt, skip=skip, limit=limit)
    return sensor_svc.list_by_field(field_id, skip=skip, limit=limit)


@internal_router.get(
    "/fields/{field_id}/satellite-observations",
    response_model=List[SatelliteObservationOut],
    summary="[Internal] Get field satellite observations",
    tags=["Internal Read"],
)
def get_internal_satellite_observations(
    field_id: int,
    from_dt: Optional[datetime] = Query(None, alias="from"),
    to_dt: Optional[datetime] = Query(None, alias="to"),
    latest: bool = Query(False, description="If true, returns only the latest record"),
    skip: int = 0,
    limit: int = 100,
    field_svc: FieldService = Depends(get_field_service),
    sat_svc: SatelliteObservationService = Depends(get_satellite_observation_service),
):
    _assert_field_exists(field_id, field_svc)
    if latest:
        skip, limit = 0, 1
    return sat_svc.list_by_field(field_id, from_dt, to_dt, skip=skip, limit=limit)


@internal_router.get(
    "/fields/{field_id}/diagnoses",
    response_model=List[DiagnosisOut],
    summary="[Internal] Get field diagnoses",
    tags=["Internal Read"],
)
def get_internal_diagnoses(
    field_id: int,
    from_dt: Optional[datetime] = Query(None, alias="from"),
    to_dt: Optional[datetime] = Query(None, alias="to"),
    latest: bool = Query(False, description="If true, returns only the latest record"),
    skip: int = 0,
    limit: int = 100,
    field_svc: FieldService = Depends(get_field_service),
    diag_svc: DiagnosisService = Depends(get_diagnosis_service),
):
    _assert_field_exists(field_id, field_svc)
    if latest:
        skip, limit = 0, 1
    return diag_svc.list_by_field(field_id, from_dt, to_dt, skip=skip, limit=limit)


@internal_router.get(
    "/fields/{field_id}/irrigation-plans",
    response_model=List[IrrigationPlanOut],
    summary="[Internal] Get field irrigation plans",
    tags=["Internal Read"],
)
def get_internal_irrigation_plans(
    field_id: int,
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
    latest: bool = Query(False, description="If true, returns only the latest record"),
    skip: int = 0,
    limit: int = 100,
    field_svc: FieldService = Depends(get_field_service),
    plan_svc: IrrigationPlanService = Depends(get_irrigation_plan_service),
):
    _assert_field_exists(field_id, field_svc)
    if latest:
        skip, limit = 0, 1
    return plan_svc.list_by_field(field_id, from_date, to_date, skip=skip, limit=limit)


@internal_router.get(
    "/fields/{field_id}/yield-predictions",
    response_model=List[YieldPredictionOut],
    summary="[Internal] Get field yield predictions",
    tags=["Internal Read"],
)
def get_internal_yield_predictions(
    field_id: int,
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
    latest: bool = Query(False, description="If true, returns only the latest record"),
    skip: int = 0,
    limit: int = 100,
    field_svc: FieldService = Depends(get_field_service),
    pred_svc: YieldPredictionService = Depends(get_yield_prediction_service),
):
    _assert_field_exists(field_id, field_svc)
    if latest:
        skip, limit = 0, 1
    return pred_svc.list_by_field(field_id, from_date, to_date, skip=skip, limit=limit)


@internal_router.get(
    "/fields/{field_id}/crop-mix-recommendations",
    response_model=List[CropMixRecommendationOut],
    summary="[Internal] Get field crop-mix recommendations",
    tags=["Internal Read"],
)
def get_internal_crop_mix_recommendations(
    field_id: int,
    latest: bool = Query(False, description="If true, returns only the latest record"),
    skip: int = 0,
    limit: int = 100,
    field_svc: FieldService = Depends(get_field_service),
    crop_mix_svc: CropMixService = Depends(get_crop_mix_service),
):
    _assert_field_exists(field_id, field_svc)
    if latest:
        skip, limit = 0, 1
    return crop_mix_svc.list_by_field(field_id, skip=skip, limit=limit)


@internal_router.get(
    "/farms/{farm_id}/fields",
    response_model=List[FieldOut],
    summary="[Internal] List all fields for a farm",
    tags=["Internal Read"],
)
def get_internal_farm_fields(
    farm_id: int,
    skip: int = 0,
    limit: int = 100,
    farm_svc: FarmService = Depends(get_farm_service),
    field_svc: FieldService = Depends(get_field_service),
):
    _assert_farm_exists(farm_id, farm_svc)
    return field_svc.list_by_farm(farm_id, skip=skip, limit=limit)


@internal_router.get(
    "/farms/{farm_id}/crop-mixes/latest",
    summary="[Internal] Get latest crop-mix recommendation for each field in farm",
    tags=["Internal Read"],
)
def get_internal_farm_latest_crop_mixes(
    farm_id: int,
    farm_svc: FarmService = Depends(get_farm_service),
    field_svc: FieldService = Depends(get_field_service),
    crop_mix_svc: CropMixService = Depends(get_crop_mix_service),
):
    _assert_farm_exists(farm_id, farm_svc)
    fields = field_svc.list_by_farm(farm_id)
    results = []
    for f in fields:
        latest_rec = crop_mix_svc.get_latest_by_field(f.id)
        results.append({
            "field_id": f.id,
            "field_name": f.name,
            "latest_recommendation": latest_rec,
        })
    return results


class FieldStateOut(BaseModel):
    field: FieldOut
    boundary: Optional[FieldBoundaryOut] = None
    latest_sensor_reading: Optional[SensorOut] = None
    latest_satellite_observation: Optional[SatelliteObservationOut] = None
    latest_diagnosis: Optional[DiagnosisOut] = None
    latest_irrigation_plan: Optional[IrrigationPlanOut] = None
    latest_yield_prediction: Optional[YieldPredictionOut] = None
    latest_crop_mix_recommendation: Optional[CropMixRecommendationOut] = None


@internal_router.get(
    "/fields/{field_id}/state",
    response_model=FieldStateOut,
    summary="[Internal] Get current aggregate state of a field",
    tags=["Internal Read"],
)
def get_internal_field_state(
    field_id: int,
    field_svc: FieldService = Depends(get_field_service),
    boundary_svc: FieldBoundaryService = Depends(get_field_boundary_service),
    sensor_svc: SensorService = Depends(get_sensor_service),
    sat_svc: SatelliteObservationService = Depends(get_satellite_observation_service),
    diag_svc: DiagnosisService = Depends(get_diagnosis_service),
    plan_svc: IrrigationPlanService = Depends(get_irrigation_plan_service),
    pred_svc: YieldPredictionService = Depends(get_yield_prediction_service),
    crop_mix_svc: CropMixService = Depends(get_crop_mix_service),
):
    field = _assert_field_exists(field_id, field_svc)
    boundary = boundary_svc.get_boundary(field_id)

    sensor_readings = sensor_svc.list_by_field(field_id, limit=1)
    sat_obs = sat_svc.list_by_field(field_id, limit=1)
    diagnoses = diag_svc.list_by_field(field_id, limit=1)
    plans = plan_svc.list_by_field(field_id, limit=1)
    predictions = pred_svc.list_by_field(field_id, limit=1)
    latest_crop_mix = crop_mix_svc.get_latest_by_field(field_id)

    return FieldStateOut(
        field=field,
        boundary=boundary,
        latest_sensor_reading=sensor_readings[0] if sensor_readings else None,
        latest_satellite_observation=sat_obs[0] if sat_obs else None,
        latest_diagnosis=diagnoses[0] if diagnoses else None,
        latest_irrigation_plan=plans[0] if plans else None,
        latest_yield_prediction=predictions[0] if predictions else None,
        latest_crop_mix_recommendation=latest_crop_mix,
    )
