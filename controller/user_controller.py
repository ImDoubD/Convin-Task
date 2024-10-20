from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from schemas.user_schema import UserCreate, UserLogin, UserResponse
from service.user_service import register_user, authenticate_user, get_user_details
from security import get_current_user
from database import get_db

router = APIRouter()

security = HTTPBearer()

# User Endpoints
@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    return register_user(user.model_dump(), db)

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    return authenticate_user(user.email, user.password, db)

@router.get("/user/details", response_model=UserResponse)
def get_user_details_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    current_user = get_current_user(credentials)
    return get_user_details(current_user['email'], db)