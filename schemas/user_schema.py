from pydantic import BaseModel, EmailStr
from typing import List, Optional

# User Schemas
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    mobile: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    mobile: str