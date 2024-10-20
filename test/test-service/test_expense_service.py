import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import Expense, User, user_expenses
from service.expense_service import add_expense, get_expense_by_id, get_user_expenses, show_overall_expenses

# Mock database session
class MockDB:
    def __init__(self):
        self.expenses = []
        self.users = []
        self.user_expenses = []
        self._query_fields = None
        self._filter_conditions = None

    def query(self, *args):
        # Store the model or columns being queried
        self._query_fields = args
        return self

    def filter(self, *args):
        # Store filter conditions if used
        self._filter_conditions = args
        return self

    def all(self):
        # Simulate returning all records for the query
        if self._query_fields:
            if User in self._query_fields:
                return self.users
            if user_expenses in self._query_fields and self._filter_conditions:
                return self.user_expenses
        return []

    def first(self):
        return self.expenses[0] if self.expenses else None

    def add(self, record):
        if isinstance(record, Expense):
            self.expenses.append(record)
        elif isinstance(record, User):
            self.users.append(record)

    def commit(self):
        pass

    def refresh(self, record):
        pass

    def execute(self, query):
        return self

    def fetchall(self):
        return self.user_expenses

@pytest.fixture
def mock_db():
    return MockDB()


def test_add_expense_exact_split_invalid_total(mock_db):
    data = {
        "created_by_id": 1,
        "description": "Dinner",
        "total_amount": 100,
        "split_method": "exact",
        "split_list": [{"user_id": 1, "split_amount": 30}, {"user_id": 2, "split_amount": 60}]
    }
    with pytest.raises(HTTPException) as exc_info:
        add_expense(data, mock_db)
    assert exc_info.value.status_code == 400
    assert "Split amounts do not sum up to total amount" in str(exc_info.value.detail)

def test_add_expense_percentage_split_invalid_percentage(mock_db):
    data = {
        "created_by_id": 1,
        "description": "Trip",
        "total_amount": 100,
        "split_method": "percentage",
        "split_list": [{"user_id": 1, "split_amount": 50}, {"user_id": 2, "split_amount": 30}]
    }
    with pytest.raises(HTTPException) as exc_info:
        add_expense(data, mock_db)
    assert exc_info.value.status_code == 400
    assert "Split percentages do not add up to 100" in str(exc_info.value.detail)

def test_get_expense_by_id_not_found(mock_db):
    with pytest.raises(HTTPException) as exc_info:
        get_expense_by_id(1, 1, mock_db)
    assert exc_info.value.status_code == 404
    assert "Expense not found for the given user" in str(exc_info.value.detail)

def test_show_overall_expenses_no_users(mock_db):
    with pytest.raises(HTTPException) as exc_info:
        show_overall_expenses(mock_db)
    assert exc_info.value.status_code == 404
    assert "No users found" in str(exc_info.value.detail)
