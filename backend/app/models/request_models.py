from pydantic import BaseModel
from typing import Optional, List

class ProductCreateRequest(BaseModel):
    title: str
    description: str
    condition: str
    category: str
    suggested_price: Optional[float] = None
    tags: List[str] = []
    brand: Optional[str] = None
    model: Optional[str] = None
    confidence_score: float = 0.7
    image_url: Optional[str] = None

class BidCreateRequest(BaseModel):
    bid_id: str
    user_id: str
    amount: float
    is_auto_bid: bool = False
    max_auto_bid: Optional[float] = None