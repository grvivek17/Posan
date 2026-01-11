from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.user import UserRole, AgeGroup


# User Schemas
class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: str


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.CHILD


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str
    password: str


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Schema for authentication token."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: Optional[int] = None
    username: Optional[str] = None


class TokenData(BaseModel):
    """Schema for token payload data."""
    user_id: Optional[int] = None
    username: Optional[str] = None


# Parent Account Schemas
class ParentAccountCreate(BaseModel):
    """Schema for creating parent account."""
    full_name: str
    phone: Optional[str] = None


class ParentAccountResponse(BaseModel):
    """Schema for parent account response."""
    id: int
    user_id: int
    full_name: str
    phone: Optional[str]
    
    model_config = {"from_attributes": True}


# Child Profile Schemas
class ChildProfileCreate(BaseModel):
    """Schema for creating child profile."""
    full_name: str
    age: int = Field(..., ge=3, le=14)
    avatar_url: Optional[str] = None


class ChildProfileUpdate(BaseModel):
    """Schema for updating child profile."""
    full_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=3, le=14)
    avatar_url: Optional[str] = None


class ChildProfileResponse(BaseModel):
    """Schema for child profile response."""
    id: int
    user_id: int
    parent_id: int
    full_name: str
    age: int
    age_group: AgeGroup
    avatar_url: Optional[str]
    total_points: int
    
    model_config = {"from_attributes": True}
