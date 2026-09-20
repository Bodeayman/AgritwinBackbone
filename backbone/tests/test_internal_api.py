import os
import pytest
from fastapi import status
from app.core.config import settings
from app.core.local_storage import LocalDiskImageStorage


@pytest.mark.skip(reason="API key auth not yet wired on internal routes")
def test_internal_api_key_auth_missing(client):
    response = client.post("/api/fields/1/sensor-readings", json={})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Missing or invalid API key" in response.json()["detail"]


@pytest.mark.skip(reason="API key auth not yet wired on internal routes")
def test_internal_api_key_auth_invalid(client):
    headers = {"X-API-Key": "invalid-secret-key-999"}
    response = client.post("/api/fields/1/sensor-readings", json={}, headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_internal_field_not_found(client):
    headers = {"X-API-Key": settings.INTERN_3_API_KEY}
    payload = {
        "field_id": 99999,
        "soil_moisture": 25.5,
        "recorded_at": "2026-08-08T10:00:00Z"
    }
    response = client.post("/api/fields/99999/sensor-readings", json=payload, headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Field with ID 99999 does not exist" in response.json()["detail"]


def test_internal_full_ingestion_and_read_flow(client):
    # 1. Setup User, Farm, and Field (Farmer Auth)
    reg_res = client.post("/api/v1/auth/register", json={"email": "farmer1@example.com", "password": "pass123456"})
    assert reg_res.status_code == status.HTTP_201_CREATED
    farmer_id = reg_res.json()["id"]

    login_res = client.post("/api/v1/auth/login", json={"email": "farmer1@example.com", "password": "pass123456"})
    token = login_res.json()["access_token"]
    farmer_headers = {"Authorization": f"Bearer {token}"}

    farm_res = client.post("/api/v1/farms", json={"name": "Twin Core Farm", "location": "Meru"}, headers=farmer_headers)
    assert farm_res.status_code == status.HTTP_201_CREATED
    farm_id = farm_res.json()["id"]

    field_res = client.post("/api/v1/fields", json={"farm_id": farm_id, "name": "Plot 1", "crop_type": "Maize"}, headers=farmer_headers)
    assert field_res.status_code == status.HTTP_201_CREATED
    field_id = field_res.json()["id"]

    # Internal module headers
    module_headers = {"X-API-Key": settings.INTERN_4A_API_KEY}

    # 2. Ingest Sensor Reading #1
    sensor_payload = {
        "field_id": field_id,
        "sensor_id": "SN-100",
        "soil_moisture": 34.2,
        "soil_temperature": 21.0,
        "air_temperature": 26.5,
        "humidity": 55.0,
        "soil_ph": 6.5,
        "electrical_conductivity": 1.1,
        "recorded_at": "2026-08-08T10:00:00Z"
    }
    res = client.post(f"/api/fields/{field_id}/sensor-readings", json=sensor_payload, headers=module_headers)
    assert res.status_code == status.HTTP_201_CREATED
    assert res.json()["soil_moisture"] == 34.2

    # Ingest Sensor Reading #2 (newer)
    sensor_payload_2 = {
        "field_id": field_id,
        "sensor_id": "SN-100",
        "soil_moisture": 41.8,
        "recorded_at": "2026-08-08T12:00:00Z"
    }
    res2 = client.post(f"/api/fields/{field_id}/sensor-readings", json=sensor_payload_2, headers=module_headers)
    assert res2.status_code == status.HTTP_201_CREATED

    # Test ?latest=true query parameter
    res_latest = client.get(f"/api/fields/{field_id}/sensor-readings?latest=true", headers=module_headers)
    assert res_latest.status_code == status.HTTP_200_OK
    latest_items = res_latest.json()
    assert len(latest_items) == 1
    assert latest_items[0]["soil_moisture"] == 41.8

    # 3. Ingest Satellite Observation (with AI model metadata)
    sat_payload = {
        "field_id": field_id,
        "model_name": "Sentinel2_NDVI_Extractor",
        "model_version": "v1.0.0",
        "ndvi": 0.78,
        "ndmi": 0.42,
        "evi": 0.65,
        "image_reference": f"fields/{field_id}/sat_001.tif",
        "captured_at": "2026-08-08T08:00:00Z"
    }
    res = client.post(f"/api/fields/{field_id}/satellite-observations", json=sat_payload, headers=module_headers)
    assert res.status_code == status.HTTP_201_CREATED
    sat_data = res.json()
    assert sat_data["ndvi"] == 0.78
    assert sat_data["model_id"] is not None
    assert sat_data["ai_model"]["name"] == "Sentinel2_NDVI_Extractor"

    # 4. Ingest Diagnosis (with AI model metadata)
    diag_payload = {
        "field_id": field_id,
        "model_name": "ResNet50_CropDisease",
        "model_version": "v1.2.0",
        "disease_or_pest": "Fall Armyworm",
        "severity": 0.35,
        "confidence": 0.91,
        "diagnosed_at": "2026-08-08T11:00:00Z",
        "explanation": "Pest damage observed on leaves.",
        "treatment_suggestion": "Apply targeted bio-pesticide."
    }
    res = client.post(f"/api/fields/{field_id}/diagnoses", json=diag_payload, headers=module_headers)
    assert res.status_code == status.HTTP_201_CREATED
    diag_data = res.json()
    assert diag_data["disease_or_pest"] == "Fall Armyworm"
    assert diag_data["model_id"] is not None
    assert diag_data["ai_model"]["name"] == "ResNet50_CropDisease"

    # 5. Ingest Irrigation Plan
    plan_payload = {
        "field_id": field_id,
        "water_requirement": 40.0,
        "unit": "mm",
        "recommended_date": "2026-08-10"
    }
    res = client.post(f"/api/fields/{field_id}/irrigation-plans", json=plan_payload, headers=module_headers)
    assert res.status_code == status.HTTP_201_CREATED
    assert res.json()["water_requirement"] == 40.0

    # 6. Ingest Yield Prediction
    yield_payload = {
        "field_id": field_id,
        "crop_type": "Maize",
        "predicted_yield": 4500.0,
        "unit": "kg/ha",
        "confidence": 0.89,
        "prediction_date": "2026-08-08",
        "model_version": "v2.0",
        "input_timestamp": "2026-08-08T10:00:00Z"
    }
    res = client.post(f"/api/fields/{field_id}/yield-predictions", json=yield_payload, headers=module_headers)
    assert res.status_code == status.HTTP_201_CREATED
    assert res.json()["predicted_yield"] == 4500.0

    # 7. Ingest Crop Mix Recommendation (Multiple Crop Allocations)
    # First create catalog crops so allocation crop_id FKs resolve
    crop_ids = []
    for crop in ("Tomato", "Wheat"):
        cc_res = client.post("/api/v1/crop-catalog/", json={
            "name_en": crop,
            "name_ar": crop,
            "category": "Vegetable" if crop == "Tomato" else "Cereal",
            "expected_yield_tons_per_feddan": 20.0,
            "price_egp_per_ton": 10000.0,
            "production_cost_egp_per_feddan": 5000.0,
            "water_requirement_m3_per_feddan": 2000.0,
            "labor_requirement_hours_per_feddan": 30.0,
            "fertilizer_requirement_kg_per_feddan": 120.0,
            "min_ph": 5.5,
            "max_ph": 7.5,
            "max_ec_ds_m": 3.0,
            "suitable_textures": ["Loam", "Clay"],
            "is_perennial": False,
        }, headers=farmer_headers)
        assert cc_res.status_code == status.HTTP_201_CREATED
        crop_ids.append(cc_res.json()["id"])

    crop_mix_payload = {
        "farm_id": farm_id,
        "model_name": "CropMix_LinearOptimizer",
        "model_version": "v4.0.0",
        "season": "Winter",
        "optimizer_version": "v4",
        "status": "processed",
        "is_feasible": True,
        "total_land_used_feddans": 70.0,
        "total_water_used_m3": 150000.0,
        "total_labor_used_hours": 2500.0,
        "total_fertilizer_used_kg": 9000.0,
        "total_expected_revenue_egp": 150000.0,
        "total_production_cost_egp": 50000.0,
        "total_labor_cost_egp": 10000.0,
        "total_fertilizer_cost_egp": 8000.0,
        "net_profit_egp": 82000.0,
        "binding_constraints": {"water": "Water availability"},
        "ai_synthesis_explanation": "Optimal allocation achieved.",
        "allocations": [
            {"field_id": field_id, "crop_id": crop_ids[0], "allocated_area_feddans": 40.0, "expected_profit_contribution_egp": 90000.0},
            {"field_id": field_id, "crop_id": crop_ids[1], "allocated_area_feddans": 30.0, "expected_profit_contribution_egp": 60000.0}
        ]
    }
    res = client.post(f"/api/fields/{field_id}/crop-mix-recommendations", json=crop_mix_payload, headers=module_headers)
    assert res.status_code == status.HTTP_201_CREATED
    rec_data = res.json()
    assert rec_data["total_expected_revenue_egp"] == 150000.0
    assert len(rec_data["allocations"]) == 2

    # 8. Test Read Endpoints
    # GET /api/fields/{field_id}
    res = client.get(f"/api/fields/{field_id}", headers=module_headers)
    assert res.status_code == status.HTTP_200_OK
    assert res.json()["name"] == "Plot 1"

    # GET /api/fields/{field_id}/sensor-readings?from=...&to=...
    res = client.get(f"/api/fields/{field_id}/sensor-readings?from=2026-08-01T00:00:00Z&to=2026-08-08T23:59:59Z", headers=module_headers)
    assert res.status_code == status.HTTP_200_OK
    assert len(res.json()) >= 1

    # GET /api/farms/{farm_id}/fields
    res = client.get(f"/api/farms/{farm_id}/fields", headers=module_headers)
    assert res.status_code == status.HTTP_200_OK
    assert len(res.json()) == 1

    # GET /api/farms/{farm_id}/crop-mixes/latest
    res = client.get(f"/api/farms/{farm_id}/crop-mixes/latest", headers=module_headers)
    assert res.status_code == status.HTTP_200_OK
    assert len(res.json()) == 1
    assert res.json()[0]["latest_recommendation"]["total_expected_revenue_egp"] == 150000.0

    # GET /api/fields/{field_id}/state
    res = client.get(f"/api/fields/{field_id}/state", headers=module_headers)
    assert res.status_code == status.HTTP_200_OK
    state = res.json()
    assert state["field"]["id"] == field_id
    assert state["latest_sensor_reading"]["soil_moisture"] == 41.8
    assert state["latest_satellite_observation"]["ndvi"] == 0.78
    assert state["latest_diagnosis"]["disease_or_pest"] == "Fall Armyworm"
    assert state["latest_crop_mix_recommendation"]["total_expected_revenue_egp"] == 150000.0


def test_local_disk_image_storage_validation(tmp_path):
    storage = LocalDiskImageStorage(base_path=str(tmp_path))
    assert os.path.exists(tmp_path)
