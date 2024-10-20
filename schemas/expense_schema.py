import datetime
from pydantic import BaseModel, ConfigDict, EmailStr
from typing import List, Optional

# Expense Schemas
class ExpenseParticipant(BaseModel):
    user_id: int
    split_amount: Optional[float] = None

class ExpenseCreate(BaseModel):
    description: str
    total_amount: float
    split_method: str  # "equal", "exact", "percentage"
    split_list: List[ExpenseParticipant]

class ExpenseResponse(BaseModel):
    id: int
    description: str
    total_amount: float
    split_method: str
    participants: List[ExpenseParticipant]

class IndividualExpenseResponse(BaseModel):
    user_id: int
    individual_expenses: List[ExpenseResponse]

class OverallExpenseResponse(BaseModel):
    user_id: int
    name: str
    email: str
    phone: str
    expense_list: List[ExpenseResponse]

class UserExpenseResponse(BaseModel):
    expense_id: int
    description: str
    total_amount: float
    amount_owed: float
    created_at: datetime

    model_config = ConfigDict(arbitrary_types_allowed=True)

class UserExpenseListResponse(BaseModel):
    user_id: int
    name: str
    email: str
    mobile: str
    expense_list: List[UserExpenseResponse]

class OverallExpenseResponse(BaseModel):
    overall_expense: List[UserExpenseListResponse]