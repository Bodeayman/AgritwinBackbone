import pytest
from fastapi import status

# Fixtures `client` and `db_session` are defined in tests/conftest.py

def test_register_success(client, db_session):
    payload = {"email": "alice@example.com", "password": "StrongPass!123"}
    resp = client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert data["email"] == payload["email"]
    assert "id" in data

def test_register_duplicate_email(client, db_session):
    payload = {"email": "bob@example.com", "password": "Secret123"}
    # First registration
    resp1 = client.post("/api/v1/auth/register", json=payload)
    assert resp1.status_code == status.HTTP_201_CREATED
    # Duplicate attempt
    resp2 = client.post("/api/v1/auth/register", json=payload)
    assert resp2.status_code == status.HTTP_409_CONFLICT
    assert resp2.json()["detail"] == "Email already registered"

def test_login_success_and_failure(client, db_session):
    # Register a user
    reg_payload = {"email": "carol@example.com", "password": "Pwd12345"}
    client.post("/api/v1/auth/register", json=reg_payload)

    # Correct credentials
    login_payload = {"email": "carol@example.com", "password": "Pwd12345"}
    resp_ok = client.post("/api/v1/auth/login", json=login_payload)
    assert resp_ok.status_code == status.HTTP_200_OK
    token_data = resp_ok.json()
    assert "access_token" in token_data

    # Incorrect password
    bad_payload = {"email": "carol@example.com", "password": "WrongPwd"}
    resp_bad = client.post("/api/v1/auth/login", json=bad_payload)
    assert resp_bad.status_code == status.HTTP_401_UNAUTHORIZED
    assert resp_bad.json()["detail"] == "Incorrect email or password"

def test_protected_endpoint_requires_auth(client, db_session):
    # Access a protected endpoint without a token should be denied
    resp = client.get("/api/v1/farms")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
