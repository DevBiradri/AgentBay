"""
Utility functions to convert between Pydantic models and SQLAlchemy models.
"""
from typing import List
from .product import Product
from .bid import Bid
from ..db_models import ProductDB, BidDB
from ...enums.enums import BidStatus
from datetime import datetime


def product_db_to_pydantic(product_db: ProductDB) -> Product:
    """
    Convert SQLAlchemy ProductDB model to Pydantic Product model.
    """
    return Product(
        title=product_db.title,
        description=product_db.description,
        condition=product_db.condition,
        category=product_db.category,
        suggested_price=product_db.suggested_price,
        tags=product_db.tags or [],
        brand=product_db.brand,
        model=product_db.model,
        confidence_score=product_db.confidence_score,
        image_url=product_db.image_url
    )


def product_pydantic_to_db(product: Product) -> ProductDB:
    """
    Convert Pydantic Product model to SQLAlchemy ProductDB model.
    """
    return ProductDB(
        title=product.title,
        description=product.description,
        condition=product.condition,
        category=product.category,
        suggested_price=product.suggested_price,
        tags=product.tags,
        brand=product.brand,
        model=product.model,
        confidence_score=product.confidence_score,
        image_url=product.image_url
    )


def bid_db_to_pydantic(bid_db: BidDB) -> Bid:
    """
    Convert SQLAlchemy BidDB model to Pydantic-like Bid model.
    Note: Bid class is not a Pydantic model, so we return a Bid instance.
    """
    bid = Bid()
    bid.bid_id = bid_db.bid_id
    bid.user_id = bid_db.user_id
    bid.product_id = str(bid_db.product_id)
    bid.amount = bid_db.amount
    bid.timestamp = bid_db.timestamp
    bid.status = BidStatus(bid_db.status)
    bid.is_auto_bid = bid_db.is_auto_bid
    bid.max_auto_bid = bid_db.max_auto_bid
    return bid


def bid_pydantic_to_db(bid: Bid, product_id: int) -> BidDB:
    """
    Convert Bid model to SQLAlchemy BidDB model.
    """
    return BidDB(
        bid_id=bid.bid_id,
        user_id=bid.user_id,
        product_id=product_id,
        amount=bid.amount,
        timestamp=bid.timestamp,
        status=bid.status.value,
        is_auto_bid=bid.is_auto_bid,
        max_auto_bid=bid.max_auto_bid
    )