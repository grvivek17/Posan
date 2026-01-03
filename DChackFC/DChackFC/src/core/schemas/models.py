from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

class MenuItemVariantBase(BaseModel):
    name: str
    price_adjustment: Decimal = Field(ge=0)
    is_available: bool = True

class MenuItemBase(BaseModel):
    name: str
    description: str
    price: Decimal = Field(ge=0)
    is_available: bool = True
    preparation_time: int = Field(gt=0)
    is_vegetarian: bool = False
    is_vegan: bool = False
    is_gluten_free: bool = False
    contains_nuts: bool = False
    spice_level: int = Field(ge=1, le=5)

class OrderItemCreate(BaseModel):
    menu_item_id: int
    variant_id: Optional[int] = None
    quantity: int = Field(gt=0)
    special_instructions: Optional[str] = None

class OrderCreate(BaseModel):
    vendor_id: int
    items: List[OrderItemCreate]
    special_instructions: Optional[str] = None
    is_preorder: bool = False
    scheduled_for: Optional[datetime] = None
    payment_method: str
    use_employee_benefit: bool = False

class OrderResponse(BaseModel):
    id: int
    order_number: str
    status: str
    total_amount: Decimal
    queue_number: Optional[int]
    estimated_waiting_time: Optional[int]
    payment_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class QueueStatus(BaseModel):
    total_orders: int
    current_position: int
    estimated_wait_time: int
    status_update: str

class OrderStatusUpdate(BaseModel):
    order_id: int
    new_status: str
    estimated_wait_time: Optional[int]
    notes: Optional[str]

class UserPreferences(BaseModel):
    dietary_preferences: dict
    favorite_cuisines: List[str]
    spice_preference: int = Field(ge=1, le=5)
    price_range: dict
    allergies: List[str]

class RecommendationRequest(BaseModel):
    user_id: int
    current_time: datetime
    meal_type: Optional[str]
    max_wait_time: Optional[int]
    price_range: Optional[dict]

class RecommendationResponse(BaseModel):
    menu_items: List[dict]
    recommendation_scores: List[float]
    reasoning: Optional[str]
