import pytest
from fastapi import status
from app.models.user import User


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
        "name": "East Barley Field",
        "crop_type": "Barley"
    }
    response = client.post("/api/v1/fields", json=field_payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    field_data = response.json()
    assert field_data["name"] == "East Barley Field"
    assert isinstance(field_data["id"], int)
    assert field_data["farm_id"] == farm_data["id"]

    # 6. Set field boundary
    boundary_payload = {
        "coordinates": [[[-122.084, 37.422], [-122.083, 37.422], [-122.083, 37.421], [-122.084, 37.421], [-122.084, 37.422]]]
    }
    response = client.post(f"/api/v1/fields/{field_data['id']}/boundary", json=boundary_payload, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    boundary_data = response.json()
    assert boundary_data["field_id"] == field_data["id"]
    assert "area_hectares" in boundary_data
