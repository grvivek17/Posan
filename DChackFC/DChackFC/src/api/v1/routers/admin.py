from fastapi import APIRouter
from .orders import MOCK_ORDERS
from .menu import MOCK_MENU

router = APIRouter()

# Mock Vendors
MOCK_VENDORS = [
    {"id": 1, "name": "Burger King", "email": "vendor1@test.com", "status": "Active"},
    {"id": 2, "name": "Pizza Hut", "email": "vendor2@test.com", "status": "Active"},
    {"id": 3, "name": "Subway", "email": "vendor3@test.com", "status": "Inactive"},
]

@router.get("/stats")
async def get_admin_stats():
    total_revenue = sum(o["total_amount"] for o in MOCK_ORDERS)
    return {
        "success": True,
        "stats": {
            "total_vendors": len(MOCK_VENDORS),
            "total_orders": len(MOCK_ORDERS),
            "total_revenue": total_revenue,
            "active_vendors": len([v for v in MOCK_VENDORS if v["status"] == "Active"])
        }
    }

@router.get("/vendors")
async def get_vendors():
    return {"success": True, "vendors": MOCK_VENDORS}
