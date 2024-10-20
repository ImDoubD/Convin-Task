import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from pydantic import EmailStr
from models import User
from service.user_service import validate_registration_data, register_user, authenticate_user, get_user_details
from security import hash_password

# Mock database session
class MockDB:
    def __init__(self):
        self.users = []

    def query(self, model):
        return self

    def filter(self, condition):
        return self

    def first(self):
        return self.users[0] if self.users else None

    def add(self, user):
        self.users.append(user)

    def commit(self):
        pass

    def refresh(self, user):
        pass

@pytest.fixture
def mock_db():
    return MockDB()

def test_validate_registration_data_success():
    valid_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "password123",
        "mobile": "1234567890"
    }
    validate_registration_data(valid_data)  # Should not raise an exception

def test_validate_registration_data_missing_fields():
    invalid_data = {
        "name": "John Doe",
        "email": "john@example.com"
    }
    with pytest.raises(HTTPException) as exc_info:
        validate_registration_data(invalid_data)
    assert exc_info.value.status_code == 400
    assert "required" in str(exc_info.value.detail)

def test_validate_registration_data_invalid_email():
    invalid_data = {
        "name": "John Doe",
        "email": "invalid-email",
        "password": "password123",
        "mobile": "1234567890"
    }
    with pytest.raises(HTTPException) as exc_info:
        validate_registration_data(invalid_data)
    assert exc_info.value.status_code == 400
    assert "Invalid email format" in str(exc_info.value.detail)

def test_validate_registration_data_short_password():
    invalid_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "12345",
        "mobile": "1234567890"
    }
    with pytest.raises(HTTPException) as exc_info:
        validate_registration_data(invalid_data)
    assert exc_info.value.status_code == 400
    assert "Password must be at least 6 characters long" in str(exc_info.value.detail)

def test_register_user_success(mock_db):
    data = {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "password123",
        "mobile": "1234567890"
    }
    new_user = register_user(data, mock_db)
    assert new_user.name == data["name"]
    assert new_user.email == data["email"]
    assert new_user.mobile == data["mobile"]
    assert new_user.hashed_password != data["password"]

def test_register_user_duplicate_email(mock_db):
    existing_user = User(email="john@example.com", mobile="1234567890")
    mock_db.users.append(existing_user)
    
    data = {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "password123",
        "mobile": "9876543210"
    }
    with pytest.raises(HTTPException) as exc_info:
        register_user(data, mock_db)
    assert exc_info.value.status_code == 400
    assert "Email or mobile number is already taken" in str(exc_info.value.detail)

def test_authenticate_user_success(mock_db):
    password = "password123"
    hashed_password = hash_password(password)
    user = User(email="john@example.com", hashed_password=hashed_password)
    mock_db.users.append(user)

    result = authenticate_user("john@example.com", password, mock_db)
    assert "access_token" in result

def test_authenticate_user_invalid_credentials(mock_db):
    user = User(email="john@example.com", hashed_password=hash_password("password123"))
    mock_db.users.append(user)

    with pytest.raises(HTTPException) as exc_info:
        authenticate_user("john@example.com", "wrong_password", mock_db)
    assert exc_info.value.status_code == 401
    assert "Invalid email or password" in str(exc_info.value.detail)

def test_get_user_details_success(mock_db):
    user = User(id=1, name="John Doe", email="john@example.com", mobile="1234567890")
    mock_db.users.append(user)

    details = get_user_details("john@example.com", mock_db)
    assert details["id"] == 1
    assert details["name"] == "John Doe"
    assert details["email"] == "john@example.com"
    assert details["mobile"] == "1234567890"

def test_get_user_details_not_found(mock_db):
    with pytest.raises(HTTPException) as exc_info:
        get_user_details("nonexistent@example.com", mock_db)
    assert exc_info.value.status_code == 404
    assert "User not found" in str(exc_info.value.detail)