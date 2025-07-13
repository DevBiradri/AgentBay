"""
SQLAlchemy database models for Product and Bid entities.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from ..database import Base

class ProductDB(Base):
    """
    SQLAlchemy model for Product table.
    """
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    condition = Column(String(50), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    suggested_price = Column(Float, nullable=True)
    current_bid = Column(Float, nullable=True)  # Current highest bid amount
    tags = Column(JSON, default=list)  # Store tags as JSON array
    brand = Column(String(100), nullable=True, index=True)
    model = Column(String(100), nullable=True)
    confidence_score = Column(Float, default=0.7)
    image_url = Column(String(500), nullable=True)  # Store image URL
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    bids = relationship("BidDB", back_populates="product", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ProductDB(id={self.id}, title='{self.title}', category='{self.category}')>"


class BidDB(Base):
    """
    SQLAlchemy model for Bid table.
    """
    __tablename__ = "bids"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(100), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    status = Column(String(20), nullable=False, default="active")  # BidStatus enum values
    is_auto_bid = Column(Boolean, default=False)
    max_auto_bid = Column(Float, nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    product = relationship("ProductDB", back_populates="bids")
    
    def __repr__(self):
        return f"<BidDB(id={self.id}, amount={self.amount}, status='{self.status}')>"