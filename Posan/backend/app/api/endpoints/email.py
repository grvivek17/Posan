from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from app.services.email_service import email_service
from typing import Optional

router = APIRouter()

class EmailRequest(BaseModel):
    to_email: EmailStr
    subject: str = "Hello from Posan"
    content: Optional[str] = None # Optional custom content
    name: Optional[str] = "Friend"

@router.post("/send-test")
async def send_test_email(request: EmailRequest, background_tasks: BackgroundTasks):
    """
    Send a test email using Resend
    """
    
    # Use custom content if provided, otherwise use default html
    html_content = request.content if request.content else f"""
    <p>Congrats on sending your <strong>first email</strong> via Posan!</p>
    <p>Hello {request.name}, this is a test email.</p>
    """
    
    # We can run this in background
    background_tasks.add_task(
        email_service.send_email,
        to_email=request.to_email,
        subject=request.subject,
        html_content=html_content
    )
    
    return {"message": "Email queued for sending", "recipient": request.to_email}

@router.post("/send-welcome")
async def send_welcome_email(request: EmailRequest, background_tasks: BackgroundTasks):
    """
    Send a welcome email
    """
    background_tasks.add_task(
        email_service.send_welcome_email,
        to_email=request.to_email,
        name=request.name
    )
    
    return {"message": "Welcome email queued", "recipient": request.to_email}
