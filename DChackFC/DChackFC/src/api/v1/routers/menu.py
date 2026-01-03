from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# In-memory storage
MOCK_MENU = [
    {
        "id": 1, "vendor_id": 1, "name": "Classic Burger", "price": 10.99, "category": "Main",
        "stock_available": 50, "max_per_order": 5, "is_takeaway_eligible": True,
        "avg_rating": 4.5, "total_ratings": 120,
        "nutrition_info": {"calories": 650, "protein": "28g", "carbs": "45g", "fat": "35g"}
    },
    {
        "id": 2, "vendor_id": 1, "name": "Fries", "price": 4.99, "category": "Side",
        "stock_available": 100, "max_per_order": 3, "is_takeaway_eligible": True,
        "avg_rating": 4.2, "total_ratings": 85,
        "nutrition_info": {"calories": 365, "protein": "4g", "carbs": "48g", "fat": "17g"}
    },
    {
        "id": 3, "vendor_id": 2, "name": "Pepperoni Pizza", "price": 15.99, "category": "Main",
        "stock_available": 30, "max_per_order": 2, "is_takeaway_eligible": True,
        "avg_rating": 4.7, "total_ratings": 200,
        "nutrition_info": {"calories": 285, "protein": "12g", "carbs": "36g", "fat": "10g"}
    },
]

class MenuItemCreate(BaseModel):
    vendor_id: int
    name: str
    price: float
    category: str
    stock_available: int = 100
    max_per_order: int = 10
    is_takeaway_eligible: bool = True
    nutrition_info: Optional[dict] = None

@router.get("/")
async def get_menu(vendor_id: Optional[int] = None):
    if vendor_id:
        return {"success": True, "items": [i for i in MOCK_MENU if i["vendor_id"] == vendor_id]}
    return {"success": True, "items": MOCK_MENU}

@router.post("/")
async def add_menu_item(item: MenuItemCreate):
    # Auto-generate nutrition info if not provided (mock AI)
    nutrition = item.nutrition_info or {
        "calories": 300,
        "protein": "15g",
        "carbs": "30g",
        "fat": "10g",
        "note": "AI-generated nutrition information"
    }
    
    new_item = {
        "id": len(MOCK_MENU) + 1,
        "vendor_id": item.vendor_id,
        "name": item.name,
        "price": item.price,
        "category": item.category,
        "stock_available": item.stock_available,
        "max_per_order": item.max_per_order,
        "is_takeaway_eligible": item.is_takeaway_eligible,
        "avg_rating": 0.0,
        "total_ratings": 0,
        "nutrition_info": nutrition
    }
    MOCK_MENU.append(new_item)
    return {"success": True, "item": new_item}

@router.put("/{item_id}/stock")
async def update_stock(item_id: int, quantity: int):
    item = next((i for i in MOCK_MENU if i["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item["stock_available"] = quantity
    return {"success": True, "item": item}

@router.post("/{item_id}/rate")
async def rate_item(item_id: int, rating: float):
    item = next((i for i in MOCK_MENU if i["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    # Update average rating
    total = item["avg_rating"] * item["total_ratings"]
    item["total_ratings"] += 1
    item["avg_rating"] = (total + rating) / item["total_ratings"]
    
    return {"success": True, "item": item}
