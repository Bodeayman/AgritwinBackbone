import pytest
from fastapi import status

# Helper to register a user and obtain auth headers
def _auth_headers(client, email, password):
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_field_crud_and_boundary(client, db_session):
    # Authenticate
    headers = _auth_headers(client, "fielduser@example.com", "Pwd12345")

    # Create a farm first (owner inferred from token)
    farm_payload = {"name": "Test Farm", "location": "Nairobi"}
    resp = client.post("/api/v1/farms", json=farm_payload, headers=headers)
    assert resp.status_code == status.HTTP_201_CREATED
    farm_id = resp.json()["id"]

    # Create a field linked to the farm
    field_payload = {"farm_id": farm_id, "name": "Barley Field", "crop_type": "Barley"}
    resp = client.post("/api/v1/fields", json=field_payload, headers=headers)
    assert resp.status_code == status.HTTP_201_CREATED
    field = resp.json()
    field_id = field["id"]
    assert field["farm_id"] == farm_id

    # Retrieve the field
    resp = client.get(f"/api/v1/fields/{field_id}", headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["id"] == field_id

    # Update the field
    update_payload = {"name": "Barley Field Updated", "crop_type": "Wheat"}
    resp = client.put(f"/api/v1/fields/{field_id}", json=update_payload, headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    updated = resp.json()
    assert updated["name"] == update_payload["name"]
    assert updated["crop_type"] == update_payload["crop_type"]

    # Add a boundary to the field
    boundary_payload = {
        "coordinates": [[[-122.084, 37.422], [-122.083, 37.422], [-122.083, 37.421], [-122.084, 37.421], [-122.084, 37.422]]]
    }
    resp = client.post(f"/api/v1/fields/{field_id}/boundary", json=boundary_payload, headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    boundary = resp.json()
    assert boundary["field_id"] == field_id
    assert "area_hectares" in boundary

    # Delete the field
    resp = client.delete(f"/api/v1/fields/{field_id}", headers=headers)
    assert resp.status_code == status.HTTP_204_NO_CONTENT

    # Verify field deletion
    resp = client.get(f"/api/v1/fields/{field_id}", headers=headers)
    assert resp.status_code == status.HTTP_404_NOT_FOUND
