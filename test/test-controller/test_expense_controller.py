from fastapi import Depends
from fastapi.security import HTTPBearer
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from main import app


client = TestClient(app)

# Fixtures for mocking
@pytest.fixture
def mock_db(mocker):
    return mocker.Mock()

@pytest.fixture
def mock_add_expense(mocker):
    return mocker.patch('service.expense_service.add_expense')

@pytest.fixture
def mock_get_expense_by_id(mocker):
    return mocker.patch('service.expense_service.get_expense_by_id')

@pytest.fixture
def mock_get_user_expenses(mocker):
    return mocker.patch('service.expense_service.get_user_expenses')

@pytest.fixture
def mock_show_overall_expenses(mocker):
    return mocker.patch('service.expense_service.show_overall_expenses')

@pytest.fixture
def mock_get_current_user(mocker):
    return mocker.patch('security.get_current_user')

# Corrected patch paths
@patch("security.get_current_user", return_value={"user_id": 1})
@patch("service.expense_service.add_expense", return_value={"id": 1, "description": "Test expense", "total_amount": 100.0})
def test_add_expense_success(mock_add_expense, mock_get_current_user):
    expense_data = {
        "description": "Test expense",
        "total_amount": 100.0,
        "split_method": "equal",
        "split_details": [{"user_id": 1, "amount": 50.0}]
    }
    
    response = client.post("/operation/expense/add", json=expense_data, headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 422

def test_add_expense_unauthorized(mock_add_expense, mock_get_current_user):
    expense_data = {
        "description": "Test expense",
        "total_amount": 100.0,
        "split_method": "equal",
        "split_details": [{"user_id": 1, "amount": 50.0}]
    }
    # Simulate unauthorized by not passing the Authorization header
    response = client.post("/operation/expense/add", json=expense_data)
    assert response.status_code == 403

def test_add_expense_invalid_data(mock_add_expense, mock_get_current_user):
    mock_get_current_user.return_value = {"user_id": 1}
    expense_data = {
        "description": "",
        "total_amount": -100.0,  # Invalid total amount
        "split_method": "equal",
        "split_details": [{"user_id": 1, "amount": 50.0}]
    }

    response = client.post("/operation/expense/add", json=expense_data, headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 422
