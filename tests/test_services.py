from datetime import datetime, date
import pytest
from fastapi import HTTPException
from app.models.user import User
from app.models.farm import Farm
from app.models.field import Field

from app.schemas.farm import FarmCreate, FarmUpdate
from app.schemas.field import FieldCreate
from app.schemas.field_boundary import FieldBoundaryCreate
from app.schemas.sensor_reading import SensorCreate
from app.schemas.satellite_observation import SatelliteObservationCreate
from app.schemas.diagnosis import DiagnosisCreate
from app.schemas.irrigation_plan import IrrigationPlanCreate
from app.schemas.yield_prediction import YieldPredictionCreate
from app.schemas.crop_mix_recommendation import CropMixRecommendationCreate, CropMixAllocationCreate

from app.services.farm_service import FarmService
from app.services.field_service import FieldService
from app.services.field_boundary_service import FieldBoundaryService
from app.services.sensor_service import SensorService
from app.services.satellite_observation_service import SatelliteObservationService
from app.services.diagnosis_service import DiagnosisService
from app.services.irrigation_plan_service import IrrigationPlanService
from app.services.yield_prediction_service import YieldPredictionService
from app.services.crop_mix_service import CropMixService


def test_farm_and_field_service(db_session):
    user = User(email="svc_user@example.com", hashed_password="hashed_pass")
    db_session.add(user)
    db_session.commit()

    farm_svc = FarmService(db_session)
    farm_out = farm_svc.create_farm(FarmCreate(name="Service Farm", location="Nakuru"), owner_id=user.id)
    assert farm_out.id is not None
    assert farm_out.name == "Service Farm"

    field_svc = FieldService(db_session)
    field_out = field_svc.create_field(FieldCreate(farm_id=farm_out.id, name="Field 1"))
    assert field_out.id is not None

    fields = field_svc.list_by_farm(farm_out.id)
    assert len(fields) == 1


def test_field_boundary_service(db_session):
    user = User(email="b_svc_user@example.com", hashed_password="hashed_pass")
    db_session.add(user)
    db_session.commit()

    farm = Farm(owner_id=user.id, name="Boundary Service Farm")
    db_session.add(farm)
    db_session.commit()

    field = Field(farm_id=farm.id, name="Field With Boundary")
    db_session.add(field)
    db_session.commit()

    boundary_svc = FieldBoundaryService(db_session)

    # 1. Non-existent field throws HTTP 404
    with pytest.raises(HTTPException) as exc_info:
        boundary_svc.set_boundary(99999, FieldBoundaryCreate(coordinates=[[[36.8, -1.2], [36.9, -1.2], [36.9, -1.3], [36.8, -1.3], [36.8, -1.2]]]))
    assert exc_info.value.status_code == 404

    # 2. Set boundary for valid field (using larger coordinates to meet validation requirements)
    res = boundary_svc.set_boundary(
        field.id,
        FieldBoundaryCreate(coordinates=[[[36.8, -1.2], [36.9, -1.2], [36.9, -1.4], [36.8, -1.4], [36.8, -1.2]]])
    )
    assert res.field_id == field.id
    assert res.area_hectares is not None
    assert res.area_hectares > 0.0


def test_satellite_and_diagnosis_services(db_session):
    user = User(email="obs_user@example.com", hashed_password="hashed_pass")
    db_session.add(user)
    db_session.commit()

    farm = Farm(owner_id=user.id, name="Obs Farm")
    db_session.add(farm)
    db_session.commit()

    field = Field(farm_id=farm.id, name="Obs Field")
    db_session.add(field)
    db_session.commit()

    # Satellite service
    sat_svc = SatelliteObservationService(db_session)
    sat_out = sat_svc.create(SatelliteObservationCreate(
        field_id=field.id,
        ndvi=0.82,
        ndmi=0.51,
        evi=0.70,
        captured_at=datetime.utcnow(),
        observation_type="processed"
    ))
    assert sat_out.id is not None
    assert sat_out.ndvi == 0.82

    # Diagnosis service
    diag_svc = DiagnosisService(db_session)
    diag_out = diag_svc.create(DiagnosisCreate(
        field_id=field.id,
        disease_or_pest="Aphids",
        severity=0.20,
        confidence=0.95,
        diagnosed_at=datetime.utcnow(),
        treatment_suggestion="Neem oil spray"
    ))
    assert diag_out.id is not None
    assert diag_out.disease_or_pest == "Aphids"


def test_irrigation_yield_and_crop_mix_services(db_session):
    user = User(email="plans_user@example.com", hashed_password="hashed_pass")
    db_session.add(user)
    db_session.commit()

    farm = Farm(owner_id=user.id, name="Plans Farm")
    db_session.add(farm)
    db_session.commit()

    field = Field(farm_id=farm.id, name="Plans Field")
    db_session.add(field)
    db_session.commit()

    # Irrigation
    plan_svc = IrrigationPlanService(db_session)
    plan_out = plan_svc.create(IrrigationPlanCreate(
        field_id=field.id,
        water_requirement=25.5,
        unit="mm",
        recommended_date=date(2026, 8, 15)
    ))
    assert plan_out.water_requirement == 25.5

    # Yield prediction
    pred_svc = YieldPredictionService(db_session)
    pred_out = pred_svc.create(YieldPredictionCreate(
        field_id=field.id,
        crop_type="Beans",
        predicted_yield=2100.0,
        unit="kg/ha",
        prediction_date=date(2026, 8, 8)
    ))
    assert pred_out.predicted_yield == 2100.0

    # Crop mix recommendation with allocations
    crop_mix_svc = CropMixService(db_session)
    mix_out = crop_mix_svc.create(CropMixRecommendationCreate(
        field_id=field.id,
        expected_profit=85000.0,
        binding_constraint="Soil nitrogen",
        allocations=[
            CropMixAllocationCreate(crop_type="Beans", allocated_area=5.0, unit="ha"),
            CropMixAllocationCreate(crop_type="Sorghum", allocated_area=10.0, unit="ha")
        ]
    ))
    assert mix_out.id is not None
    assert len(mix_out.allocations) == 2

    latest_mix = crop_mix_svc.get_latest_by_field(field.id)
    assert latest_mix is not None
    assert latest_mix.expected_profit == 85000.0
