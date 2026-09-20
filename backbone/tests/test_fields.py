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
    field_payload = {"farm_id": farm_id, "name": "Barley Field"}
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
    update_payload = {"name": "Barley Field Updated"}
    resp = client.put(f"/api/v1/fields/{field_id}", json=update_payload, headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    updated = resp.json()
    assert updated["name"] == update_payload["name"]

    # Add a boundary to the field (using larger coordinates to meet validation requirements)
    boundary_payload = {
        "coordinates": [[[-122.084, 37.422], [-122.082, 37.422], [-122.082, 37.420], [-122.084, 37.420], [-122.084, 37.422]]]
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
