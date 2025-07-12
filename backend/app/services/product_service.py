"""
ProductService with PostgreSQL database operations.
"""
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from ..database import get_db, DatabaseManager
from ..models.db_models import ProductDB
from ..models.agent_models import Product
from ..models.converters.converters import product_db_to_pydantic, product_pydantic_to_db

logger = logging.getLogger(__name__)


class ProductService:
    """Handles product database operations using PostgreSQL"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def create_product(self, product: Product) -> ProductDB:
        """Create a new product in the database"""
        session = self.db_manager.create_session()
        try:
            product_db = product_pydantic_to_db(product)
            session.add(product_db)
            self.db_manager.commit_session(session)
            session.refresh(product_db)
            logger.info(f"Created product: {product_db.title}")
            return product_db
        except Exception as e:
            self.db_manager.rollback_session(session)
            logger.error(f"Error creating product: {e}")
            raise
        finally:
            self.db_manager.close_session(session)
    
    def get_product_by_id(self, product_id: int) -> Optional[ProductDB]:
        """Get a product by its database ID"""
        session = self.db_manager.create_session()
        try:
            product = session.query(ProductDB).filter(ProductDB.id == product_id).first()
            return product
        except Exception as e:
            logger.error(f"Error getting product by ID {product_id}: {e}")
            return None
        finally:
            self.db_manager.close_session(session)
    
    def get_all_products(self, limit: int = 100, offset: int = 0) -> List[ProductDB]:
        """Get all products with pagination"""
        session = self.db_manager.create_session()
        try:
            products = session.query(ProductDB).offset(offset).limit(limit).all()
            return products
        except Exception as e:
            logger.error(f"Error getting all products: {e}")
            return []
        finally:
            self.db_manager.close_session(session)
    
    def update_product(self, product_id: int, updates: dict) -> Optional[ProductDB]:
        """Update a product with given updates"""
        session = self.db_manager.create_session()
        try:
            product = session.query(ProductDB).filter(ProductDB.id == product_id).first()
            if not product:
                return None
            
            # Update allowed fields
            allowed_fields = [
                'title', 'description', 'condition', 'category',
                'suggested_price', 'tags', 'brand', 'model', 'confidence_score', 'image_url'
            ]
            
            for field, value in updates.items():
                if field in allowed_fields and hasattr(product, field):
                    setattr(product, field, value)
            
            self.db_manager.commit_session(session)
            session.refresh(product)
            logger.info(f"Updated product: {product.title}")
            return product
            
        except Exception as e:
            self.db_manager.rollback_session(session)
            logger.error(f"Error updating product {product_id}: {e}")
            return None
        finally:
            self.db_manager.close_session(session)
    
    def delete_product(self, product_id: int) -> bool:
        """Delete a product by ID"""
        session = self.db_manager.create_session()
        try:
            product = session.query(ProductDB).filter(ProductDB.id == product_id).first()
            if not product:
                return False
            
            session.delete(product)
            self.db_manager.commit_session(session)
            logger.info(f"Deleted product: {product.title}")
            return True
            
        except Exception as e:
            self.db_manager.rollback_session(session)
            logger.error(f"Error deleting product {product_id}: {e}")
            return False
        finally:
            self.db_manager.close_session(session)
    
    def get_product_as_pydantic(self, product_id: int) -> Optional[Product]:
        """Get a product as a Pydantic model"""
        product_db = self.get_product_by_id(product_id)
        if product_db:
            return product_db_to_pydantic(product_db)
        return None