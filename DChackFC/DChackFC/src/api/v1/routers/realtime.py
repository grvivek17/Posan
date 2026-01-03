from fastapi import APIRouter, WebSocket, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.dependencies import get_db, get_current_user
from core.schemas.orders import OrderCreate, OrderResponse
from core.ml.queue_optimizer import optimize_queue
from core.services.order_service import OrderService

router = APIRouter()

class QueueUpdate(BaseModel):
    order_id: int
    position: int
    estimated_wait_time: int
    status: str

@router.websocket("/queue/{order_id}")
async def queue_updates(
    websocket: WebSocket,
    order_id: int,
    db: Session = Depends(get_db)
):
    await websocket.accept()
    try:
        while True:
            # Get real-time queue updates
            queue_status = await OrderService.get_queue_status(order_id, db)
            
            # Optimize queue using ML
            optimized_queue = await optimize_queue(queue_status)
            
            # Send updates to client
            await websocket.send_json(optimized_queue)
            
    except Exception as e:
        await websocket.close(code=1000)

@router.post("/orders/", response_model=OrderResponse)
async def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new order with real-time tracking."""
    try:
        # Create order
        order_service = OrderService(db)
        new_order = await order_service.create_order(order, current_user)
        
        # Optimize queue
        await optimize_queue(new_order.id)
        
        return new_order
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/orders/{order_id}/status")
async def get_order_status(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get real-time order status."""
    try:
        order_service = OrderService(db)
        status = await order_service.get_order_status(order_id, current_user)
        return status
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
