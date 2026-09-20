import pytest
from fastapi import status

# Fixtures `client` and `db_session` come from tests/conftest.py

def _register_and_login(client, email, password):
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_farm_crud_flow(client, db_session):
    # Register and obtain auth header
    headers = _register_and_login(client, "farmuser@example.com", "Pwd12345")

    # List farms - should be empty
    resp = client.get("/api/v1/farms", headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == []

    # Create a farm
    farm_payload = {"name": "Sunny Farm", "location": "Nairobi"}
    resp = client.post("/api/v1/farms", json=farm_payload, headers=headers)
    assert resp.status_code == status.HTTP_201_CREATED
    farm = resp.json()
    assert farm["name"] == farm_payload["name"]
    farm_id = farm["id"]

    # Retrieve the farm
    resp = client.get(f"/api/v1/farms/{farm_id}", headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["id"] == farm_id

    # Update the farm
    update_payload = {"name": "Sunny Farm Updated", "location": "Kisumu"}
    resp = client.put(f"/api/v1/farms/{farm_id}", json=update_payload, headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["name"] == update_payload["name"]

    # Delete the farm
    resp = client.delete(f"/api/v1/farms/{farm_id}", headers=headers)
    assert resp.status_code == status.HTTP_204_NO_CONTENT

    # Verify deletion
    resp = client.get(f"/api/v1/farms/{farm_id}", headers=headers)
    assert resp.status_code == status.HTTP_404_NOT_FOUND
