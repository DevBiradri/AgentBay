from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from ..enums.enums import BidStatus

class Product(BaseModel):
    title: str
    description: str
    condition: str
    category: str
    suggested_price: Optional[float] = None
    current_bid: Optional[float] = None
    tags: List[str] = []
    brand: Optional[str] = None
    model: Optional[str] = None
    confidence_score: float = Field(default=0.7)
    image_url: Optional[str] = None

class Bid(BaseModel):
    user_id: str
    product_id: str
    amount: float
    timestamp: Optional[datetime] = None
    status: BidStatus
    is_auto_bid: bool = False
    max_auto_bid: Optional[float] = None
    
    def to_dict(self):
        d = self.model_dump()
        if self.timestamp:
            d['timestamp'] = self.timestamp.isoformat()
        d['status'] = self.status.value
        return d
    