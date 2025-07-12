from enum import Enum

class ProductCondition(Enum):
    NEW = "new"
    LIKE_NEW = "like_new"
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    FOR_PARTS = "for_parts"

class AuctionStatus(Enum):
    ACTIVE = "active"
    ENDED = "ended"
    CANCELLED = "cancelled"
    SOLD = "sold"

class BidStatus(Enum):
    ACTIVE = "active"
    WINNING = "winning"
    OUTBID = "outbid"
    WON = "won"
    LOST = "lost"