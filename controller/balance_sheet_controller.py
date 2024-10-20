from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import StreamingResponse
from service.balance_sheet_service import download_overall_balance_sheet, download_individual_balance_sheet
from security import get_current_user
from database import get_db

router = APIRouter()

security = HTTPBearer()

# Controller to download overall balance sheet (requires authentication)
@router.get("/overall", response_class=StreamingResponse)
def download_overall_balance_sheet_controller(
    db: Session = Depends(get_db), 
    credentials: HTTPAuthorizationCredentials = Depends(get_current_user)
):
    """
    Download the overall balance sheet for all users in CSV format.
    Accessible only to authenticated users.
    """
    return download_overall_balance_sheet(db)

# Controller to download individual balance sheet (requires authentication)
@router.get("/user/{user_id}", response_class=StreamingResponse)
def download_individual_balance_sheet_controller(
    user_id: int, 
    db: Session = Depends(get_db), 
    credentials: HTTPAuthorizationCredentials = Depends(get_current_user)
):
    """
    Download the balance sheet for a specific user in CSV format.
    Accessible only to authenticated users.
    """
    if int(credentials['user_id']) != user_id:
        raise HTTPException(status_code=403, detail="You are not authorized to access this user's balance sheet.")
    
    return download_individual_balance_sheet(user_id, db)
