"""
ProductService with PostgreSQL database operations.
"""
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from ..database import get_db, DatabaseManager
from ..models.db_models import ProductDB
from ..models.product import Product
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
    
    def get_product_by_title(self, title: str) -> Optional[ProductDB]:
        """Get a product by its title"""
        session = self.db_manager.create_session()
        try:
            product = session.query(ProductDB).filter(ProductDB.title == title).first()
            return product
        except Exception as e:
            logger.error(f"Error getting product by title '{title}': {e}")
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
    
    def search_products(
        self, 
        query: str = "", 
        category: str = "", 
        brand: str = "",
        min_price: float = None,
        max_price: float = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ProductDB]:
        """Search products based on various criteria"""
        session = self.db_manager.create_session()
        try:
            # Start with base query
            query_builder = session.query(ProductDB)
            
            filters = []
            
            # Text search across title, description, brand, model, and tags
            if query:
                query_lower = f"%{query.lower()}%"
                text_filters = or_(
                    ProductDB.title.ilike(query_lower),
                    ProductDB.description.ilike(query_lower),
                    ProductDB.brand.ilike(query_lower),
                    ProductDB.model.ilike(query_lower),
                    ProductDB.tags.astext.ilike(query_lower)
                )
                filters.append(text_filters)
            
            # Category filter
            if category:
                filters.append(ProductDB.category.ilike(f"%{category}%"))
            
            # Brand filter
            if brand:
                filters.append(ProductDB.brand.ilike(f"%{brand}%"))
            
            # Price filters
            if min_price is not None:
                filters.append(ProductDB.suggested_price >= min_price)
            
            if max_price is not None:
                filters.append(ProductDB.suggested_price <= max_price)
            
            # Apply all filters
            if filters:
                query_builder = query_builder.filter(and_(*filters))
            
            # Order by created_at (newest first)
            query_builder = query_builder.order_by(ProductDB.created_at.desc())
            
            # Apply pagination
            products = query_builder.offset(offset).limit(limit).all()
            
            logger.info(f"Found {len(products)} products matching search criteria")
            return products
            
        except Exception as e:
            logger.error(f"Error searching products: {e}")
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
    
    def get_products_by_category(self, category: str, limit: int = 50) -> List[ProductDB]:
        """Get products by category"""
        session = self.db_manager.create_session()
        try:
            products = session.query(ProductDB).filter(
                ProductDB.category.ilike(f"%{category}%")
            ).limit(limit).all()
            return products
        except Exception as e:
            logger.error(f"Error getting products by category '{category}': {e}")
            return []
        finally:
            self.db_manager.close_session(session)
    
    def get_products_by_brand(self, brand: str, limit: int = 50) -> List[ProductDB]:
        """Get products by brand"""
        session = self.db_manager.create_session()
        try:
            products = session.query(ProductDB).filter(
                ProductDB.brand.ilike(f"%{brand}%")
            ).limit(limit).all()
            return products
        except Exception as e:
            logger.error(f"Error getting products by brand '{brand}': {e}")
            return []
        finally:
            self.db_manager.close_session(session)
    
    def count_products(self) -> int:
        """Count total number of products"""
        session = self.db_manager.create_session()
        try:
            count = session.query(ProductDB).count()
            return count
        except Exception as e:
            logger.error(f"Error counting products: {e}")
            return 0
        finally:
            self.db_manager.close_session(session)

    def get_product_as_pydantic(self, product_id: int) -> Optional[Product]:
        """Get a product as a Pydantic model"""
        product_db = self.get_product_by_id(product_id)
        if product_db:
            return product_db_to_pydantic(product_db)
        return None