from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api import deps
from app.core import security
from app.models.user import User, UserRole
from pydantic import BaseModel

router = APIRouter()

# Simple Schema for Signup
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: UserRole = UserRole.PUBLIC # Default to Public

@router.post("/signup")
def signup(user_in: UserCreate, db: Session = Depends(deps.get_db)):
    # 1. Check if user exists
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 2. Create new user
    new_user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role.value  # <--- CHANGE THIS: Add .value
    )
    db.add(new_user)
    db.commit()
    return {"msg": "User created successfully"}

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(deps.get_db)
):
    # 1. Find user
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    # 2. Create Token
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}