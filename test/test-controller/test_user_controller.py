from fastapi import HTTPException
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def mock_db(mocker):
    return mocker.Mock()

@pytest.fixture
def mock_register_user(mocker):
    return mocker.patch('service.user_service.register_user')

@pytest.fixture
def mock_authenticate_user(mocker):
    return mocker.patch('service.user_service.authenticate_user')

def test_login_success(mock_authenticate_user):
    login_data = {
        "email": "john@example.com",
        "password": "password123"
    }
    mock_authenticate_user.return_value = {"access_token": "mock_token"}
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_credentials(mock_authenticate_user):
    login_data = {
        "email": "john@example.com",
        "password": "wrong_password"
    }
    mock_authenticate_user.side_effect = HTTPException(status_code=401, detail="Invalid credentials")
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 401

def test_get_user_details_invalid_token():
    response = client.get("/auth/user/details", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401

def test_get_user_details_missing_token():
    response = client.get("/auth/user/details")
    assert response.status_code == 403