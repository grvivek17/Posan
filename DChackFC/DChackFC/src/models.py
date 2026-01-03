from pydantic import BaseModel
from typing import Optional

class Vendor(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

class MenuItem(BaseModel):
    id: int
    name: str
    price: float
    vendor_id: int
