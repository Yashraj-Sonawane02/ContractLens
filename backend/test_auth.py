from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_user_registration_and_login():
    email = "testuser_v2@example.com"
    password = "SecurePassword123!"
    
    # 1. Register User
    reg_response = client.post(
        "/api/v1/auth/register",
        json={"full_name": "Test User", "email": email, "password": password}
    )
    assert reg_response.status_code == 201
    reg_data = reg_response.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == email

    # 2. Duplicate Registration should fail
    dup_response = client.post(
        "/api/v1/auth/register",
        json={"full_name": "Test User", "email": email, "password": password}
    )
    assert dup_response.status_code == 400

    # 3. Login User
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # 4. Profile endpoint with Bearer token
    profile_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert profile_response.status_code == 200
    assert profile_response.json()["email"] == email

if __name__ == "__main__":
    test_health_check()
    test_user_registration_and_login()
    print("ALL AUTHENTICATION & DATABASE TESTS PASSED SUCCESSFULLY!")
