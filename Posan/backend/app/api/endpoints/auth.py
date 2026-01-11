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
    # Convert username to lowercase for case-insensitive comparison
    username_lower = user_data.username.lower()
    
    # Check if user already exists (case-insensitive)
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == username_lower)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Create new user with lowercase username
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=username_lower,  # Store in lowercase
        hashed_password=hashed_password,
        role=user_data.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(new_user.id), "username": new_user.username})
    refresh_token = create_refresh_token(data={"sub": str(new_user.id)})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=new_user.id,
        username=new_user.username
    )


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return tokens."""
    # Convert username to lowercase for case-insensitive comparison
    username_lower = credentials.username.lower()
    
    # Find user by username (case-insensitive)
    user = db.query(User).filter(User.username == username_lower).first()
    
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
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id,
        username=user.username
    )


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


# ============= PASSWORD RESET ENDPOINTS =============

@router.post("/forgot-password")
def request_password_reset(
    email: str,
    db: Session = Depends(get_db)
):
    """
    Request password reset - generates a reset token.
    
    In production, this would send an email with the reset link.
    For now, it returns the token directly for testing.
    """
    from app.schemas.password_reset import PasswordResetResponse
    import secrets
    from datetime import datetime, timedelta
    
    # Find user by email
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        # Don't reveal if email exists for security
        return PasswordResetResponse(
            success=True,
            message="If an account exists with this email, you will receive a password reset link."
        )
    
    # Generate secure reset token
    reset_token = secrets.token_urlsafe(32)
    
    # Store token with expiration (1 hour)
    # In production, store this in database with expiration
    # For now, we'll use a simple in-memory approach
    # You should add a PasswordResetToken model to store these properly
    
    # For demo purposes, we'll encode the user_id and timestamp in the token
    import base64
    import json
    token_data = {
        "user_id": user.id,
        "email": user.email,
        "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
        "secret": reset_token
    }
    encoded_token = base64.urlsafe_b64encode(json.dumps(token_data).encode()).decode()
    
    # In production: Send email with reset link
    # For now, return the token
    return {
        "success": True,
        "message": "Password reset instructions sent to your email",
        "reset_token": encoded_token,  # Remove this in production
        "reset_link": f"http://localhost:5173/reset-password?token={encoded_token}"  # For testing
    }


@router.post("/reset-password")
def reset_password(
    token: str,
    new_password: str,
    db: Session = Depends(get_db)
):
    """
    Reset password using the token from email.
    """
    from app.schemas.password_reset import PasswordResetResponse
    import base64
    import json
    from datetime import datetime
    
    try:
        # Decode and validate token
        token_data = json.loads(base64.urlsafe_b64decode(token.encode()).decode())
        
        # Check expiration
        expires_at = datetime.fromisoformat(token_data["expires_at"])
        if datetime.utcnow() > expires_at:
            raise HTTPException(
                status_code=400,
                detail="Reset token has expired. Please request a new one."
            )
        
        # Find user
        user = db.query(User).filter(
            User.id == token_data["user_id"],
            User.email == token_data["email"]
        ).first()
        
        if not user:
            raise HTTPException(status_code=400, detail="Invalid reset token")
        
        # Update password
        print(f"Updating password for user: {user.email} (ID: {user.id})")
        user.hashed_password = get_password_hash(new_password)
        db.add(user)  # Explicitly add to session
        db.commit()
        db.refresh(user)  # Refresh to ensure changes are persisted
        print(f"Password updated successfully for user: {user.email}")
        
        return PasswordResetResponse(
            success=True,
            message="Password successfully reset. You can now login with your new password."
        )
        
    except (json.JSONDecodeError, KeyError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid reset token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting password: {str(e)}")


@router.post("/verify-reset-token")
def verify_reset_token(token: str):
    """
    Verify if a reset token is valid and not expired.
    """
    import base64
    import json
    from datetime import datetime
    
    try:
        token_data = json.loads(base64.urlsafe_b64decode(token.encode()).decode())
        expires_at = datetime.fromisoformat(token_data["expires_at"])
        
        if datetime.utcnow() > expires_at:
            return {"valid": False, "message": "Token has expired"}
        
        return {
            "valid": True,
            "email": token_data["email"],
            "message": "Token is valid"
        }
    except:
        return {"valid": False, "message": "Invalid token"}

