from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.models.user import User, ParentAccount, ChildProfile, UserRole, AgeGroup
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, ParentAccountCreate, ParentAccountResponse
from datetime import timedelta

router = APIRouter()


def get_age_group(age: int) -> AgeGroup:
    """Determine age group based on age."""
    if 3 <= age <= 5:
        return AgeGroup.TODDLER
    elif 6 <= age <= 8:
        return AgeGroup.EARLY
    elif 9 <= age <= 11:
        return AgeGroup.MIDDLE
    elif 12 <= age <= 14:
        return AgeGroup.PRETEEN
    else:
        raise ValueError("Age must be between 3 and 14")


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        role=user_data.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(new_user.id), "username": new_user.username})
    refresh_token = create_refresh_token(data={"sub": str(new_user.id)})
    
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return tokens."""
    # Find user by username
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id), "username": user.username})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/parent-account", response_model=ParentAccountResponse, status_code=status.HTTP_201_CREATED)
def create_parent_account(
    parent_data: ParentAccountCreate,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Create a parent account for a user."""
    # Check if user exists and is a parent
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role != UserRole.PARENT:
        raise HTTPException(status_code=400, detail="User must have parent role")
    
    # Check if parent account already exists
    existing_parent = db.query(ParentAccount).filter(ParentAccount.user_id == user_id).first()
    if existing_parent:
        raise HTTPException(status_code=400, detail="Parent account already exists")
    
    # Create parent account
    parent_account = ParentAccount(
        user_id=user_id,
        full_name=parent_data.full_name,
        phone=parent_data.phone
    )
    
    db.add(parent_account)
    db.commit()
    db.refresh(parent_account)
    
    return parent_account
