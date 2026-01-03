from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import random
import string
import qrcode
import io
import base64

router = APIRouter()

# In-memory storage
PREORDERS = []

class PreorderCreate(BaseModel):
    vendor_id: int
    items: list
    total_amount: float
    customer_name: str
    scheduled_for: str  # ISO datetime string
    customization_notes: Optional[str] = None

class CustomizationResponse(BaseModel):
    approved: bool
    additional_cost: float = 0.0
    vendor_notes: Optional[str] = None

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def generate_qr_code(data: str):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

@router.post("/")
async def create_preorder(preorder: PreorderCreate):
    otp = generate_otp()
    order_id = len(PREORDERS) + 1
    qr_data = f"ORDER:{order_id}:OTP:{otp}"
    qr_code = generate_qr_code(qr_data)
    
    # Calculate ETA (15 mins before scheduled time)
    scheduled = datetime.fromisoformat(preorder.scheduled_for.replace('Z', '+00:00'))
    eta = scheduled - timedelta(minutes=15)
    
    new_preorder = {
        "id": order_id,
        "order_number": f"PRE-{order_id + 1000}",
        "vendor_id": preorder.vendor_id,
        "items": preorder.items,
        "total_amount": preorder.total_amount,
        "customer_name": preorder.customer_name,
        "scheduled_for": preorder.scheduled_for,
        "eta": eta.isoformat(),
        "customization_notes": preorder.customization_notes,
        "customization_approved": None,
        "additional_cost": 0.0,
        "status": "pending",
        "qr_code": qr_code,
        "otp": otp,
        "pickup_verified": False,
        "created_at": datetime.now().isoformat()
    }
    
    PREORDERS.append(new_preorder)
    return {"success": True, "preorder": new_preorder}

@router.get("/{preorder_id}")
async def get_preorder(preorder_id: int):
    preorder = next((p for p in PREORDERS if p["id"] == preorder_id), None)
    if not preorder:
        raise HTTPException(status_code=404, detail="Preorder not found")
    return {"success": True, "preorder": preorder}

@router.put("/{preorder_id}/verify")
async def verify_pickup(preorder_id: int, otp: str):
    preorder = next((p for p in PREORDERS if p["id"] == preorder_id), None)
    if not preorder:
        raise HTTPException(status_code=404, detail="Preorder not found")
    
    if preorder["otp"] != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    preorder["pickup_verified"] = True
    preorder["status"] = "completed"
    return {"success": True, "message": "Pickup verified", "preorder": preorder}

@router.put("/{preorder_id}/customization")
async def respond_to_customization(preorder_id: int, response: CustomizationResponse):
    preorder = next((p for p in PREORDERS if p["id"] == preorder_id), None)
    if not preorder:
        raise HTTPException(status_code=404, detail="Preorder not found")
    
    preorder["customization_approved"] = response.approved
    preorder["additional_cost"] = response.additional_cost
    preorder["total_amount"] += response.additional_cost
    
    return {"success": True, "preorder": preorder}

@router.get("/vendor/{vendor_id}")
async def get_vendor_preorders(vendor_id: int):
    vendor_preorders = [p for p in PREORDERS if p["vendor_id"] == vendor_id]
    return {"success": True, "preorders": vendor_preorders}
