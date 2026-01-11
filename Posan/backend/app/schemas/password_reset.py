"""
Password Reset Token Schema and Models
"""
from pydantic import BaseModel, EmailStr
from typing import Optional

class PasswordResetRequest(BaseModel):
    """Schema for requesting password reset"""
    email: EmailStr

class PasswordResetVerify(BaseModel):
    """Schema for verifying reset token"""
    token: str
    new_password: str

class PasswordResetResponse(BaseModel):
    """Schema for password reset response"""
    message: str
    success: bool
