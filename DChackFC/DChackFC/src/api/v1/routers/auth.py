from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str
    role: str  # 'vendor' or 'customer'

@router.post("/login")
async def login(request: LoginRequest):
    # Mock login logic
    if request.password == "password":
        user_data = {
            "email": request.email,
            "role": request.role,
            "name": request.email.split('@')[0].title()
        }
        
        # Assign dynamic vendor ID based on email number (vendor1 -> 1)
        if request.role == 'vendor':
            import re
            match = re.search(r'\d+', request.email)
            user_data['vendor_id'] = int(match.group()) if match else 1
            
        return {
            "success": True,
            "token": "mock-jwt-token",
            "user": user_data
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")
