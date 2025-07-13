"""
BidService with PostgreSQL database operations.
"""
import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from ..database import get_db, DatabaseManager
from ..models.db_models import BidDB, ProductDB
from ..models.agent_models import Bid
from ..models.converters.converters import bid_db_to_pydantic, bid_pydantic_to_db
from ..enums.enums import BidStatus

logger = logging.getLogger(__name__)


class BidService:
    """Handles bid database operations using PostgreSQL"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def create_bid(self, bid: Bid, product_id: int) -> Optional[BidDB]:
        """Create a new bid in the database"""
        session = self.db_manager.create_session()
        try:
            # Verify product exists
            product = session.query(ProductDB).filter(ProductDB.id == product_id).first()
            if not product:
                logger.error(f"Product {product_id} not found for bid creation")
                return None
            
            bid_db = bid_pydantic_to_db(bid, product_id)
            session.add(bid_db)
            self.db_manager.commit_session(session)
            session.refresh(bid_db)
            logger.info(f"Created bid: {bid_db.id} for product {product_id}")
            return bid_db
        except Exception as e:
            self.db_manager.rollback_session(session)
            logger.error(f"Error creating bid: {e}")
            raise
        finally:
            self.db_manager.close_session(session)
    
    def get_bid_by_id(self, bid_id: int) -> Optional[BidDB]:
        """Get a bid by its database ID"""
        session = self.db_manager.create_session()
        try:
            bid = session.query(BidDB).filter(BidDB.id == bid_id).first()
            return bid
        except Exception as e:
            logger.error(f"Error getting bid by ID {bid_id}: {e}")
            return None
        finally:
            self.db_manager.close_session(session)
    
    
    def get_bids_by_product(self, product_id: int, limit: int = 100) -> List[BidDB]:
        """Get all bids for a specific product"""
        session = self.db_manager.create_session()
        try:
            bids = session.query(BidDB).filter(
                BidDB.product_id == product_id
            ).order_by(desc(BidDB.amount)).limit(limit).all()
            return bids
        except Exception as e:
            logger.error(f"Error getting bids for product {product_id}: {e}")
            return []
        finally:
            self.db_manager.close_session(session)
    
    def get_bids_by_user(self, user_id: str, limit: int = 100) -> List[BidDB]:
        """Get all bids for a specific user"""
        session = self.db_manager.create_session()
        try:
            bids = session.query(BidDB).filter(
                BidDB.user_id == user_id
            ).order_by(desc(BidDB.timestamp)).limit(limit).all()
            return bids
        except Exception as e:
            logger.error(f"Error getting bids for user {user_id}: {e}")
            return []
        finally:
            self.db_manager.close_session(session)
    
    def get_highest_bid_for_product(self, product_id: int) -> Optional[BidDB]:
        """Get the highest bid for a specific product"""
        session = self.db_manager.create_session()
        try:
            bid = session.query(BidDB).filter(
                and_(
                    BidDB.product_id == product_id,
                    BidDB.status.in_([BidStatus.ACTIVE.value, BidStatus.WINNING.value])
                )
            ).order_by(desc(BidDB.amount)).first()
            return bid
        except Exception as e:
            logger.error(f"Error getting highest bid for product {product_id}: {e}")
            return None
        finally:
            self.db_manager.close_session(session)
    
    def get_active_bids_by_user(self, user_id: str) -> List[BidDB]:
        """Get all active bids for a user"""
        session = self.db_manager.create_session()
        try:
            bids = session.query(BidDB).filter(
                and_(
                    BidDB.user_id == user_id,
                    BidDB.status.in_([
                        BidStatus.ACTIVE.value, 
                        BidStatus.WINNING.value
                    ])
                )
            ).order_by(desc(BidDB.timestamp)).all()
            return bids
        except Exception as e:
            logger.error(f"Error getting active bids for user {user_id}: {e}")
            return []
        finally:
            self.db_manager.close_session(session)
    
    def update_bid_status(self, bid_id: int, status: BidStatus) -> Optional[BidDB]:
        """Update the status of a bid"""
        session = self.db_manager.create_session()
        try:
            bid = session.query(BidDB).filter(BidDB.id == bid_id).first()
            if not bid:
                return None
            
            bid.status = status.value
            self.db_manager.commit_session(session)
            session.refresh(bid)
            logger.info(f"Updated bid {bid.id} status to {status.value}")
            return bid
            
        except Exception as e:
            self.db_manager.rollback_session(session)
            logger.error(f"Error updating bid status {bid_id}: {e}")
            return None
        finally:
            self.db_manager.close_session(session)
    
    def update_bid_amount(self, bid_id: int, new_amount: float) -> Optional[BidDB]:
        """Update the amount of a bid (for auto-bidding scenarios)"""
        session = self.db_manager.create_session()
        try:
            bid = session.query(BidDB).filter(BidDB.id == bid_id).first()
            if not bid:
                return None
            
            bid.amount = new_amount
            bid.timestamp = datetime.now()
            self.db_manager.commit_session(session)
            session.refresh(bid)
            logger.info(f"Updated bid {bid.id} amount to {new_amount}")
            return bid
            
        except Exception as e:
            self.db_manager.rollback_session(session)
            logger.error(f"Error updating bid amount {bid_id}: {e}")
            return None
        finally:
            self.db_manager.close_session(session)
    
    def delete_bid(self, bid_id: int) -> bool:
        """Delete a bid by ID"""
        session = self.db_manager.create_session()
        try:
            bid = session.query(BidDB).filter(BidDB.id == bid_id).first()
            if not bid:
                return False
            
            session.delete(bid)
            self.db_manager.commit_session(session)
            logger.info(f"Deleted bid: {bid.id}")
            return True
            
        except Exception as e:
            self.db_manager.rollback_session(session)
            logger.error(f"Error deleting bid {bid_id}: {e}")
            return False
        finally:
            self.db_manager.close_session(session)
    
    def get_bid_history_for_product(self, product_id: int) -> List[BidDB]:
        """Get complete bid history for a product ordered by timestamp"""
        session = self.db_manager.create_session()
        try:
            bids = session.query(BidDB).filter(
                BidDB.product_id == product_id
            ).order_by(desc(BidDB.timestamp)).all()
            return bids
        except Exception as e:
            logger.error(f"Error getting bid history for product {product_id}: {e}")
            return []
        finally:
            self.db_manager.close_session(session)
    
    def count_bids_for_product(self, product_id: int) -> int:
        """Count total number of bids for a product"""
        session = self.db_manager.create_session()
        try:
            count = session.query(BidDB).filter(BidDB.product_id == product_id).count()
            return count
        except Exception as e:
            logger.error(f"Error counting bids for product {product_id}: {e}")
            return 0
        finally:
            self.db_manager.close_session(session)
    
    def count_bids_by_user(self, user_id: str) -> int:
        """Count total number of bids by a user"""
        session = self.db_manager.create_session()
        try:
            count = session.query(BidDB).filter(BidDB.user_id == user_id).count()
            return count
        except Exception as e:
            logger.error(f"Error counting bids for user {user_id}: {e}")
            return 0
        finally:
            self.db_manager.close_session(session)
    
    def get_auto_bids_by_user(self, user_id: str) -> List[BidDB]:
        """Get all auto bids for a user"""
        session = self.db_manager.create_session()
        try:
            bids = session.query(BidDB).filter(
                and_(
                    BidDB.user_id == user_id,
                    BidDB.is_auto_bid == True
                )
            ).order_by(desc(BidDB.timestamp)).all()
            return bids
        except Exception as e:
            logger.error(f"Error getting auto bids for user {user_id}: {e}")
            return []
        finally:
            self.db_manager.close_session(session)

    def get_bid_as_pydantic(self, bid_id: int) -> Optional[Bid]:
        """Get a bid as a Pydantic model"""
        bid_db = self.get_bid_by_id(bid_id)
        if bid_db:
            return bid_db_to_pydantic(bid_db)
        return None
    
    def process_outbid_updates(self, product_id: int, winning_bid_id: int):
        """Update all other bids for a product to OUTBID status when there's a new winning bid"""
        session = self.db_manager.create_session()
        try:
            # Update all other bids for this product to OUTBID
            session.query(BidDB).filter(
                and_(
                    BidDB.product_id == product_id,
                    BidDB.id != winning_bid_id,
                    BidDB.status.in_([BidStatus.ACTIVE.value, BidStatus.WINNING.value])
                )
            ).update({BidDB.status: BidStatus.OUTBID.value})
            
            # Set the winning bid to WINNING status
            session.query(BidDB).filter(BidDB.id == winning_bid_id).update(
                {BidDB.status: BidStatus.WINNING.value}
            )

            # Get the winning bid to update the product's current_bid
            winning_bid = session.query(BidDB).filter(BidDB.id == winning_bid_id).first()
            if winning_bid:
                # Update the product's current_bid
                session.query(ProductDB).filter(ProductDB.id == product_id).update(
                    {ProductDB.current_bid: winning_bid.amount}
                )
            
            self.db_manager.commit_session(session)
            logger.info(f"Updated bid statuses and product current_bid for product {product_id}, winning bid: {winning_bid_id}")
            
        except Exception as e:
            self.db_manager.rollback_session(session)
            logger.error(f"Error processing outbid updates for product {product_id}: {e}")
            raise
        finally:
            self.db_manager.close_session(session)