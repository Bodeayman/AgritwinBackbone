from datetime import datetime, date, timedelta
import pytest
from app.models.user import User
from app.models.farm import Farm
from app.models.field import Field
from app.models.field_boundary import FieldBoundary
from app.models.sensor_reading import SensorReading
from app.models.satellite_observation import SatelliteObservation
from app.models.diagnosis import Diagnosis
from app.models.irrigation_plan import IrrigationPlan
from app.models.yield_prediction import YieldPrediction
from app.models.crop_mix_recommendation import CropMixRecommendation
from app.models.crop_mix_allocation import CropMixAllocation

from app.repositories.farm_repository import FarmRepository
from app.repositories.field_repository import FieldRepository
from app.repositories.field_boundary_repository import FieldBoundaryRepository
from app.repositories.sensor_repository import SensorRepository
from app.repositories.satellite_observation_repository import SatelliteObservationRepository
from app.repositories.diagnosis_repository import DiagnosisRepository
from app.repositories.irrigation_plan_repository import IrrigationPlanRepository
from app.repositories.yield_prediction_repository import YieldPredictionRepository
from app.repositories.crop_mix_recommendation_repository import CropMixRecommendationRepository


def test_farm_and_field_repository_crud(db_session):
    # 1. Create User
    user = User(email="test_repo_owner@example.com", hashed_password="hashed_secret_pass")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 2. Create Farm
    farm_repo = FarmRepository(db_session)
    farm = Farm(owner_id=user.id, name="Highland Agro", location="Rift Valley")
    farm_repo.create(farm)
    assert farm.id is not None

    # 3. Create Field
    field_repo = FieldRepository(db_session)
    field = Field(farm_id=farm.id, name="Block A")
    field_repo.create(field)
    assert field.id is not None

    # 4. List fields by farm
    fields = field_repo.get_fields_by_farm(farm.id)
    assert len(fields) == 1
    assert fields[0].name == "Block A"


def test_field_boundary_repository_and_area(db_session):
    user = User(email="boundary_user@example.com", hashed_password="pass")
    db_session.add(user)
    db_session.commit()

    farm = Farm(owner_id=user.id, name="Boundary Farm")
    db_session.add(farm)
    db_session.commit()

    field = Field(farm_id=farm.id, name="Boundary Field")
    db_session.add(field)
    db_session.commit()

    boundary_repo = FieldBoundaryRepository(db_session)
    wkt = "SRID=4326;POLYGON((36.821 -1.292, 36.822 -1.292, 36.822 -1.293, 36.821 -1.293, 36.821 -1.292))"
    boundary = FieldBoundary(field_id=field.id, boundary=wkt)
    boundary_repo.create(boundary)

    assert boundary.id is not None
    fetched = boundary_repo.get_by_field_id(field.id)
    assert fetched is not None
    assert fetched.field_id == field.id

    coords = boundary_repo.get_coordinates(fetched)
    assert len(coords) == 1
    assert len(coords[0]) == 5

    area_ha = boundary_repo.compute_hectares(fetched)
    assert area_ha > 0.0


def test_sensor_repository_historical_and_date_range(db_session):
    user = User(email="sensor_user@example.com", hashed_password="pass")
    db_session.add(user)
    db_session.commit()

    farm = Farm(owner_id=user.id, name="Sensor Farm")
    db_session.add(farm)
    db_session.commit()

    field = Field(farm_id=farm.id, name="Sensor Field")
    db_session.add(field)
    db_session.commit()

    sensor_repo = SensorRepository(db_session)

    # Insert 3 historical readings at different times
    t1 = datetime(2026, 8, 1, 10, 0, 0)
    t2 = datetime(2026, 8, 5, 10, 0, 0)
    t3 = datetime(2026, 8, 8, 10, 0, 0)

    sensor_repo.create(SensorReading(field_id=field.id, sensor_id="S1", soil_moisture=20.0, recorded_at=t1))
    sensor_repo.create(SensorReading(field_id=field.id, sensor_id="S1", soil_moisture=30.0, recorded_at=t2))
    sensor_repo.create(SensorReading(field_id=field.id, sensor_id="S1", soil_moisture=40.0, recorded_at=t3))

    # All records preserved (historical requirement)
    readings = sensor_repo.list_by_field(field.id)
    assert len(readings) == 3
    # Ordered newest first
    assert readings[0].soil_moisture == 40.0

    # Date range filter
    range_readings = sensor_repo.list_by_field_date_range(
        field_id=field.id,
        from_dt=datetime(2026, 8, 4, 0, 0, 0),
        to_dt=datetime(2026, 8, 6, 23, 59, 59)
    )
    assert len(range_readings) == 1
    assert range_readings[0].soil_moisture == 30.0


def test_crop_mix_recommendation_allocations(db_session):
    user = User(email="cropmix_user@example.com", hashed_password="pass")
    db_session.add(user)
    db_session.commit()

    farm = Farm(owner_id=user.id, name="CropMix Farm")
    db_session.add(farm)
    db_session.commit()

    field = Field(farm_id=farm.id, name="CropMix Field")
    db_session.add(field)
    db_session.commit()

    rec_repo = CropMixRecommendationRepository(db_session)
    rec = CropMixRecommendation(
        field_id=field.id,
        expected_profit=200000.0,
        binding_constraint="Water and Labor",
    )
    db_session.add(rec)
    db_session.flush()

    alloc1 = CropMixAllocation(recommendation_id=rec.id, crop_type="Tomato", allocated_area=15.0, unit="ha")
    alloc2 = CropMixAllocation(recommendation_id=rec.id, crop_type="Onion", allocated_area=10.0, unit="ha")
    db_session.add(alloc1)
    db_session.add(alloc2)
    db_session.commit()

    fetched = rec_repo.get_with_allocations(rec.id)
    assert fetched is not None
    assert len(fetched.allocations) == 2
    crops = {a.crop_type for a in fetched.allocations}
    assert crops == {"Tomato", "Onion"}
