import pytest

def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Advocate Ramesh Kumar",
            "email": "ramesh@legaltech.in",
            "password": "SecurePassword123!"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "ramesh@legaltech.in"

def test_register_duplicate_email(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Advocate Ramesh Kumar",
            "email": "ramesh@legaltech.in",
            "password": "AnotherPassword123!"
        }
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_login_success(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "ramesh@legaltech.in",
            "password": "SecurePassword123!"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_login_invalid_credentials(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "ramesh@legaltech.in",
            "password": "WrongPassword!"
        }
    )
    assert response.status_code == 401

def test_get_user_profile(client):
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "email": "ramesh@legaltech.in",
            "password": "SecurePassword123!"
        }
    )
    token = login_res.json()["access_token"]
    
    profile_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert profile_res.status_code == 200
    assert profile_res.json()["email"] == "ramesh@legaltech.in"
