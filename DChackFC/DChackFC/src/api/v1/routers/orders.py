from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()

# In-memory storage for demo
MOCK_ORDERS = []

class OrderItem(BaseModel):
    name: str
    quantity: int
    price: float

class OrderCreate(BaseModel):
    vendor_id: int
    items: List[OrderItem]
    total_amount: float
    customer_name: str

@router.post("/")
async def create_order(order: OrderCreate):
    new_order = {
        "id": len(MOCK_ORDERS) + 1,
        "order_number": f"ORD-{len(MOCK_ORDERS) + 1000}",
        "vendor_id": order.vendor_id,
        "items": [item.dict() for item in order.items],
        "total_amount": order.total_amount,
        "customer_name": order.customer_name,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    MOCK_ORDERS.append(new_order)
    return {"success": True, "order": new_order}

@router.get("/vendor/{vendor_id}")
async def get_vendor_orders(vendor_id: int):
    # Filter orders for this vendor
    vendor_orders = [o for o in MOCK_ORDERS if o["vendor_id"] == vendor_id]
    return {"success": True, "orders": vendor_orders}

@router.put("/{order_id}/status")
async def update_order_status(order_id: int, status: str):
    for order in MOCK_ORDERS:
        if order["id"] == order_id:
            order["status"] = status
            return {"success": True, "order": order}
    raise HTTPException(status_code=404, detail="Order not found")
