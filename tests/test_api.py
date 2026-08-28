import pytest
from fastapi import status
from app.models.user import User
from datetime import datetime


def test_health_check_public(client):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "healthy"


def test_farms_endpoint_protected(client):
    response = client.get("/api/v1/farms")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_auth_and_protected_flow(client, db_session):
    # 1. Register a new user
    register_payload = {
        "email": "testuser@example.com",
        "password": "strongpassword123"
    }
    response = client.post("/api/v1/auth/register", json=register_payload)
    assert response.status_code == status.HTTP_201_CREATED
    user_data = response.json()
    assert user_data["email"] == "testuser@example.com"
    assert "id" in user_data
    user_id = user_data["id"]
    
    # 2. Login to get token
    login_payload = {
        "email": "testuser@example.com",
        "password": "strongpassword123"
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == status.HTTP_200_OK
    token_data = response.json()
    assert "access_token" in token_data
    token = token_data["access_token"]
    
    # 3. Request protected endpoint with token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/farms", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

    # 4. Create a farm (owner_id is inferred automatically from JWT Bearer Token)
    farm_payload = {
        "name": "Green Valley Farms",
        "location": "Nairobi, Kenya"
    }
    response = client.post("/api/v1/farms", json=farm_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    farm_data = response.json()
    assert farm_data["name"] == "Green Valley Farms"
    assert farm_data["owner_id"] == user_id
    assert isinstance(farm_data["id"], int)

    # 5. Create a field for that farm
    field_payload = {
        "farm_id": farm_data["id"],
        "name": "East Barley Field"
    }
    response = client.post("/api/v1/fields", json=field_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    field_data = response.json()
    assert field_data["name"] == "East Barley Field"
    assert isinstance(field_data["id"], int)
    assert field_data["farm_id"] == farm_data["id"]

    # 6. Set field boundary (using larger coordinates to meet minimum area requirement)
    boundary_payload = {
        "coordinates": [[[-122.084, 37.422], [-122.082, 37.422], [-122.082, 37.420], [-122.084, 37.420], [-122.084, 37.422]]]
    }
    response = client.post(f"/api/v1/fields/{field_data['id']}/boundary", json=boundary_payload, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    boundary_data = response.json()
    assert boundary_data["field_id"] == field_data["id"]
    assert "area_hectares" in boundary_data

    # 7. Test satellite observations with non-existent model_id (should auto-create via model_name/version)
    satellite_payload = {
        "field_id": field_data["id"],
        "model_id": 999,  # Non-existent model_id
        "model_name": "Sentinel2_NDVI_Extractor",
        "model_version": "v1.0.0",
        "satellite_name": "Sentinel-2A",
        "ndvi": 0.72,
        "ndmi": 0.45,
        "evi": 0.58,
        "status": "processed",
        "captured_at": "2026-08-08T08:30:00Z"
    }
    response = client.post("/api/v1/satellite-observations/", json=satellite_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    sat_data = response.json()
    assert sat_data["field_id"] == field_data["id"]
    assert sat_data["ndvi"] == 0.72
    # The AI model should be auto-created and linked
    assert sat_data["ai_model"] is not None
    assert sat_data["ai_model"]["name"] == "Sentinel2_NDVI_Extractor"
    assert sat_data["ai_model"]["version"] == "v1.0.0"
    # The satellite should be auto-created and linked
    assert sat_data["satellite"] is not None
    assert sat_data["satellite"]["name"] == "Sentinel-2A"
