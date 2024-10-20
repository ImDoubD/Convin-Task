from fastapi import HTTPException
from sqlalchemy.orm import Session
from pydantic import EmailStr, ValidationError, parse_obj_as
from security import hash_password, verify_password, create_access_token
from models import User


# Function to validate user registration data
def validate_registration_data(data):
    if "name" not in data or not data["name"]:
        raise HTTPException(status_code=400, detail="Name is required.")
    if "email" not in data or not data["email"]:
        raise HTTPException(status_code=400, detail="Email is required.")
    if "password" not in data or not data["password"]:
        raise HTTPException(status_code=400, detail="Password is required.")
    if "mobile" not in data or not data["mobile"]:
        raise HTTPException(status_code=400, detail="Mobile is required.")
    
    # Validate email format using Pydantic
    try:
        parse_obj_as(EmailStr, data["email"]) 
    except ValidationError:
        raise HTTPException(status_code=400, detail="Invalid email format.")

    # Ensure password meets minimum length
    if len(data["password"]) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long.")


# Logic to register a user with a hashed password
def register_user(data: dict, db: Session):
    # Validate the input data
    validate_registration_data(data)

    # Check if the email or mobile number is already taken
    user_exists = db.query(User).filter((User.email == data["email"]) | (User.mobile == data["mobile"])).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="Email or mobile number is already taken.")
    
    hashed_password = hash_password(data['password'])

    new_user = User(
        name=data['name'],
        email=data['email'],
        mobile=data['mobile'],
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# Logic to authenticate a user during login
def authenticate_user(email: str, password: str, db: Session):
    # Check if the user exists by their email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    # Verify password using bcrypt
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    
    # JWT token creation for the authenticated user
    token = create_access_token({"user_id": str(user.id), "email": email})

    user.token = token
    db.commit() 

    return {"access_token": token}


# retrieve user details
def get_user_details(email:str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "mobile": user.mobile
    }
