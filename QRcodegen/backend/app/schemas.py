from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import Optional

class QRCodeCreate(BaseModel):
    """Schema for creating a new QR code"""
    title: Optional[str] = Field(None, max_length=200, description="Title for the QR code")
    url: str = Field(..., description="URL to encode in the QR code")
    description: Optional[str] = Field(None, description="Description of the QR code")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "My Website",
                "url": "https://example.com",
                "description": "QR code for my awesome website"
            }
        }

class QRCodeResponse(BaseModel):
    """Schema for QR code response"""
    id: int
    title: Optional[str]
    url: str
    description: Optional[str]
    qr_code_image: str  # Base64 encoded image
    created_at: datetime
    scans: int

    class Config:
        from_attributes = True

class QRCodeList(BaseModel):
    """Schema for listing QR codes"""
    id: int
    title: Optional[str]
    url: str
    created_at: datetime
    scans: int

    class Config:
        from_attributes = True
