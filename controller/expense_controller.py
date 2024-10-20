from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from schemas.expense_schema import UserExpenseListResponse, ExpenseCreate, ExpenseResponse, OverallExpenseResponse
from service.expense_service import add_expense, get_expense_by_id, get_user_expenses, show_overall_expenses
from security import get_current_user
from models import User
from database import get_db

router = APIRouter()

security = HTTPBearer()

# Expense Endpoints

# Add an expense (only by the authenticated, logged in user)
@router.post("/expense/add", response_model=ExpenseResponse)
def add_expense_endpoint(expense: ExpenseCreate, db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    current_user = get_current_user(credentials)
    expense_data = expense.model_dump()
    expense_data["created_by_id"] = current_user["user_id"]
    return add_expense(expense_data, db)

# fetch expense details created by the user
@router.get("/expense/{expense_id}", response_model=ExpenseResponse)
def get_expense(expense_id: int, db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    current_user = get_current_user(credentials)
    return get_expense_by_id(current_user["user_id"], expense_id, db)

# fetch the all various expenses of the user part of that expense
@router.get("/expenses/user", response_model=UserExpenseListResponse)
def get_user_expenses_endpoint(db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    current_user = get_current_user(credentials)
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    expense_list = get_user_expenses(current_user["user_id"], db)
    return UserExpenseListResponse(
        user_id=user.id,
        name=user.name,
        email=user.email,
        mobile=user.mobile,
        expense_list=expense_list
    )

# fetch the expenses of all the users in the system
@router.get("/expenses/overall", response_model=OverallExpenseResponse)
def show_overall_expenses_endpoint(db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    current_user = get_current_user(credentials)
    overall_expenses = show_overall_expenses(db)
    return OverallExpenseResponse(overall_expense=overall_expenses)