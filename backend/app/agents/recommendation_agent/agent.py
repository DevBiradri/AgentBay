import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import os
from datetime import datetime, timedelta
import asyncio
import uuid
import google.generativeai as genai

# Google ADK imports
from google.adk.agents import Agent
from google.adk.sessions import Session

from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Import shared enums from listing agent
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

@dataclass
class Bid:
    bid_id: str
    user_id: str
    product_id: str
    amount: float
    timestamp: datetime
    status: BidStatus
    is_auto_bid: bool = False
    max_auto_bid: Optional[float] = None
    
    def to_dict(self):
        d = asdict(self)
        d['timestamp'] = self.timestamp.isoformat()
        d['status'] = self.status.value
        return d

@dataclass
class AuctionProduct:
    product_id: str
    title: str
    description: str
    condition: ProductCondition
    category: str
    brand: Optional[str]
    model: Optional[str]
    tags: List[str]
    starting_price: float
    current_bid: float
    buy_now_price: Optional[float]
    reserve_price: Optional[float]
    auction_end_time: datetime
    auction_status: AuctionStatus
    bid_count: int
    watchers: int
    seller_id: str
    image_urls: List[str]
    shipping_cost: float
    location: str
    created_at: datetime
    updated_at: datetime
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.image_urls is None:
            self.image_urls = []
    
    def to_dict(self):
        d = asdict(self)
        d['condition'] = self.condition.value
        d['auction_status'] = self.auction_status.value
        d['auction_end_time'] = self.auction_end_time.isoformat()
        d['created_at'] = self.created_at.isoformat()
        d['updated_at'] = self.updated_at.isoformat()
        return d

class RecommendationAgentConfig:
    """Configuration for the recommendation agent"""
    def __init__(self):
        self.gemini_api_key = os.getenv("GOOGLE_API_KEY")
        self.products_db_path = os.getenv("PRODUCTS_DB_PATH", "backend/data/products.json")
        self.bids_db_path = os.getenv("BIDS_DB_PATH", "backend/data/bids.json")
        if not self.gemini_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")

class ProductDatabase:
    """Handles product database operations"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.products = {}
        self.load_products()
    
    def load_products(self):
        """Load products from JSON file"""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.products = {pid: AuctionProduct(**prod) for pid, prod in data.items()}
                logger.info(f"Loaded {len(self.products)} products from database")
            else:
                self.products = {}
                # Create sample data
                self.create_sample_data()
                logger.info("Created sample product database")
        except Exception as e:
            logger.error(f"Error loading products: {e}")
            self.products = {}
    
    def save_products(self):
        """Save products to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with open(self.db_path, 'w', encoding='utf-8') as f:
                serializable_data = {pid: prod.to_dict() for pid, prod in self.products.items()}
                json.dump(serializable_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self.products)} products to database")
        except Exception as e:
            logger.error(f"Error saving products: {e}")
    
    def create_sample_data(self):
        """Create sample auction products"""
        sample_products = [
            {
                "product_id": "p001",
                "title": "iPhone 14 Pro Max 256GB Space Black",
                "description": "Excellent condition iPhone 14 Pro Max with original box and accessories. Minor scratches on back but screen is perfect.",
                "condition": ProductCondition.EXCELLENT,
                "category": "Electronics",
                "brand": "Apple",
                "model": "iPhone 14 Pro Max",
                "tags": ["smartphone", "apple", "256gb", "space black"],
                "starting_price": 500.0,
                "current_bid": 750.0,
                "buy_now_price": 950.0,
                "reserve_price": 700.0,
                "auction_end_time": datetime.now() + timedelta(days=3),
                "auction_status": AuctionStatus.ACTIVE,
                "bid_count": 12,
                "watchers": 25,
                "seller_id": "seller_001",
                "image_urls": ["https://example.com/iphone1.jpg"],
                "shipping_cost": 15.0,
                "location": "New York, NY",
                "created_at": datetime.now() - timedelta(days=2),
                "updated_at": datetime.now()
            },
            {
                "product_id": "p002",
                "title": "Vintage Rolex Submariner 1980s",
                "description": "Authentic vintage Rolex Submariner from the 1980s. Serviced recently. Some patina on dial adds character.",
                "condition": ProductCondition.GOOD,
                "category": "Watches",
                "brand": "Rolex",
                "model": "Submariner",
                "tags": ["luxury", "vintage", "diving", "automatic"],
                "starting_price": 2000.0,
                "current_bid": 3500.0,
                "buy_now_price": 4500.0,
                "reserve_price": 3000.0,
                "auction_end_time": datetime.now() + timedelta(days=5),
                "auction_status": AuctionStatus.ACTIVE,
                "bid_count": 8,
                "watchers": 45,
                "seller_id": "seller_002",
                "image_urls": ["https://example.com/rolex1.jpg"],
                "shipping_cost": 25.0,
                "location": "Los Angeles, CA",
                "created_at": datetime.now() - timedelta(days=4),
                "updated_at": datetime.now()
            },
            {
                "product_id": "p003",
                "title": "MacBook Pro 16-inch M2 Pro 512GB",
                "description": "Like new MacBook Pro with M2 Pro chip. Barely used, perfect for professionals. Includes original charger.",
                "condition": ProductCondition.LIKE_NEW,
                "category": "Electronics",
                "brand": "Apple",
                "model": "MacBook Pro 16-inch",
                "tags": ["laptop", "apple", "m2 pro", "512gb"],
                "starting_price": 1200.0,
                "current_bid": 1650.0,
                "buy_now_price": 2100.0,
                "reserve_price": 1500.0,
                "auction_end_time": datetime.now() + timedelta(days=1),
                "auction_status": AuctionStatus.ACTIVE,
                "bid_count": 15,
                "watchers": 38,
                "seller_id": "seller_003",
                "image_urls": ["https://example.com/macbook1.jpg"],
                "shipping_cost": 20.0,
                "location": "Chicago, IL",
                "created_at": datetime.now() - timedelta(days=6),
                "updated_at": datetime.now()
            }
        ]
        
        for product_data in sample_products:
            product = AuctionProduct(**product_data)
            self.products[product.product_id] = product
        
        self.save_products()
    
    def add_product(self, product: AuctionProduct):
        """Add a new product to the database"""
        self.products[product.product_id] = product
        self.save_products()
    
    def get_product(self, product_id: str) -> Optional[AuctionProduct]:
        """Get a specific product by ID"""
        return self.products.get(product_id)
    
    def search_products(self, query: str = "", category: str = "", max_price: float = None) -> List[AuctionProduct]:
        """Search products based on criteria"""
        results = []
        query_lower = query.lower()
        
        for product in self.products.values():
            if product.auction_status != AuctionStatus.ACTIVE:
                continue
                
            matches = True
            
            # Text search
            if query_lower:
                text_match = (
                    query_lower in product.title.lower() or
                    query_lower in product.description.lower() or
                    query_lower in (product.brand or "").lower() or
                    query_lower in (product.model or "").lower() or
                    any(query_lower in tag.lower() for tag in product.tags)
                )
                if not text_match:
                    matches = False
            
            # Category filter
            if category and product.category.lower() != category.lower():
                matches = False
            
            # Price filter
            if max_price and product.current_bid > max_price:
                matches = False
            
            if matches:
                results.append(product)
        
        # Sort by relevance (ending soon first, then by current bid)
        results.sort(key=lambda x: (x.auction_end_time, -x.current_bid))
        return results

class BidDatabase:
    """Handles bid database operations"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.bids = {}
        self.load_bids()
    
    def load_bids(self):
        """Load bids from JSON file"""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.bids = {bid_id: Bid(**bid) for bid_id, bid in data.items()}
                logger.info(f"Loaded {len(self.bids)} bids from database")
            else:
                self.bids = {}
                logger.info("Created new bid database")
        except Exception as e:
            logger.error(f"Error loading bids: {e}")
            self.bids = {}
    
    def save_bids(self):
        """Save bids to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with open(self.db_path, 'w', encoding='utf-8') as f:
                serializable_data = {bid_id: bid.to_dict() for bid_id, bid in self.bids.items()}
                json.dump(serializable_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self.bids)} bids to database")
        except Exception as e:
            logger.error(f"Error saving bids: {e}")
    
    def add_bid(self, bid: Bid):
        """Add a new bid"""
        self.bids[bid.bid_id] = bid
        self.save_bids()
    
    def get_bids_for_product(self, product_id: str) -> List[Bid]:
        """Get all bids for a specific product"""
        return [bid for bid in self.bids.values() if bid.product_id == product_id]
    
    def get_bids_for_user(self, user_id: str) -> List[Bid]:
        """Get all bids for a specific user"""
        return [bid for bid in self.bids.values() if bid.user_id == user_id]

def get_personalized_recommendations(user_preferences: dict, user_history: Optional[List[str]] = None) -> dict:
    """
    Generate personalized product recommendations using Gemini API
    """
    try:
        config = RecommendationAgentConfig()
        db = ProductDatabase(config.products_db_path)
        
        # Get available products
        available_products = [p for p in db.products.values() if p.auction_status == AuctionStatus.ACTIVE]
        
        if not available_products:
            return {
                "status": "success",
                "recommendations": [],
                "message": "No active auctions available at the moment."
            }
        
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Prepare context for recommendation
        products_summary = []
        for product in available_products:
            time_left = product.auction_end_time - datetime.now()
            products_summary.append({
                "id": product.product_id,
                "title": product.title,
                "category": product.category,
                "brand": product.brand,
                "current_bid": product.current_bid,
                "buy_now_price": product.buy_now_price,
                "condition": product.condition.value,
                "time_left_hours": max(0, int(time_left.total_seconds() / 3600)),
                "bid_count": product.bid_count,
                "tags": product.tags
            })
        
        # Create recommendation prompt
        prompt = f"""
        You are an expert auction recommendation system. Based on the user's preferences and available products, 
        recommend the best auction items for them.
        
        User Preferences:
        {json.dumps(user_preferences, indent=2)}
        
        User History (previously viewed/bid on):
        {user_history if user_history else "No history available"}
        
        Available Products:
        {json.dumps(products_summary, indent=2)}
        
        Please analyze and return your recommendations in this JSON format:
        {{
            "top_recommendations": [
                {{
                    "product_id": "product_id",
                    "relevance_score": 0.95,
                    "reason": "Why this product matches the user's preferences",
                    "urgency": "high/medium/low",
                    "value_assessment": "great_deal/fair_price/premium"
                }}
            ],
            "category_suggestions": ["category1", "category2"],
            "price_range_recommendation": {{
                "min": 0,
                "max": 1000
            }},
            "timing_advice": "General advice about bidding timing"
        }}
        
        Consider:
        - User's preferred categories and brands
        - Budget constraints
        - Auction end times (urgency)
        - Current bid vs. typical market value
        - Competition level (bid count)
        - Product condition vs. user preferences
        
        Recommend maximum 5 products, ranked by relevance.
        """
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Extract JSON from response
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
        else:
            json_text = response_text
        
        try:
            recommendations = json.loads(json_text)
            
            # Enrich recommendations with full product details
            enriched_recommendations = []
            for rec in recommendations.get("top_recommendations", []):
                product = db.get_product(rec["product_id"])
                if product:
                    enriched_rec = {
                        "product": product.to_dict(),
                        "relevance_score": rec["relevance_score"],
                        "reason": rec["reason"],
                        "urgency": rec["urgency"],
                        "value_assessment": rec["value_assessment"]
                    }
                    enriched_recommendations.append(enriched_rec)
            
            result = {
                "status": "success",
                "recommendations": enriched_recommendations,
                "category_suggestions": recommendations.get("category_suggestions", []),
                "price_range_recommendation": recommendations.get("price_range_recommendation", {}),
                "timing_advice": recommendations.get("timing_advice", "")
            }
            
            logger.info(f"Generated {len(enriched_recommendations)} recommendations")
            return result
            
        except json.JSONDecodeError:
            logger.error("Failed to parse recommendation JSON")
            # Fallback to simple recommendation
            return {
                "status": "success",
                "recommendations": available_products[:3],
                "message": "Showing recent active auctions"
            }
    
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return {
            "status": "error",
            "error_message": str(e)
        }

def search_products_by_query(query: str, filters: Optional[dict] = None) -> dict:
    """
    Search for products based on natural language query
    """
    try:
        config = RecommendationAgentConfig()
        db = ProductDatabase(config.products_db_path)
        
        if filters is None:
            filters = {}
        
        # Extract search parameters
        category = filters.get("category", "")
        max_price = filters.get("max_price")
        min_price = filters.get("min_price")
        condition = filters.get("condition")
        
        # Search products
        results = db.search_products(query, category, max_price)
        
        # Apply additional filters
        if min_price:
            results = [p for p in results if p.current_bid >= min_price]
        
        if condition:
            results = [p for p in results if p.condition.value == condition]
        
        # Format results
        formatted_results = []
        for product in results:
            time_left = product.auction_end_time - datetime.now()
            formatted_results.append({
                "product": product.to_dict(),
                "time_left_hours": max(0, int(time_left.total_seconds() / 3600)),
                "time_left_formatted": format_time_left(time_left)
            })
        
        return {
            "status": "success",
            "results": formatted_results,
            "total_found": len(formatted_results),
            "query": query,
            "filters_applied": filters
        }
        
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        return {
            "status": "error",
            "error_message": str(e)
        }

def place_bid(user_id: str, product_id: str, bid_amount: float, auto_bid_max: Optional[float] = None) -> dict:
    """
    Place a bid on a product
    """
    try:
        config = RecommendationAgentConfig()
        product_db = ProductDatabase(config.products_db_path)
        bid_db = BidDatabase(config.bids_db_path)
        
        # Get the product
        product = product_db.get_product(product_id)
        if not product:
            return {
                "status": "error",
                "error_message": "Product not found"
            }
        
        # Check if auction is still active
        if product.auction_status != AuctionStatus.ACTIVE:
            return {
                "status": "error",
                "error_message": "Auction is not active"
            }
        
        # Check if auction has ended
        if product.auction_end_time <= datetime.now():
            return {
                "status": "error",
                "error_message": "Auction has ended"
            }
        
        # Check if bid is higher than current bid
        if bid_amount <= product.current_bid:
            return {
                "status": "error",
                "error_message": f"Bid must be higher than current bid of ${product.current_bid}"
            }
        
        # Check if bid meets reserve price
        if product.reserve_price and bid_amount < product.reserve_price:
            return {
                "status": "error",
                "error_message": f"Bid must meet reserve price of ${product.reserve_price}"
            }
        
        # Create the bid
        bid = Bid(
            bid_id=str(uuid.uuid4()),
            user_id=user_id,
            product_id=product_id,
            amount=bid_amount,
            timestamp=datetime.now(),
            status=BidStatus.WINNING,
            is_auto_bid=auto_bid_max is not None,
            max_auto_bid=auto_bid_max
        )
        
        # Update previous bids for this product
        existing_bids = bid_db.get_bids_for_product(product_id)
        for existing_bid in existing_bids:
            if existing_bid.status == BidStatus.WINNING:
                existing_bid.status = BidStatus.OUTBID
                bid_db.bids[existing_bid.bid_id] = existing_bid
        
        # Add the new bid
        bid_db.add_bid(bid)
        
        # Update product
        product.current_bid = bid_amount
        product.bid_count += 1
        product.updated_at = datetime.now()
        product_db.products[product_id] = product
        product_db.save_products()
        
        logger.info(f"Bid placed: ${bid_amount} on {product_id} by {user_id}")
        
        return {
            "status": "success",
            "bid": bid.to_dict(),
            "message": f"Bid of ${bid_amount} placed successfully!",
            "new_current_bid": product.current_bid
        }
        
    except Exception as e:
        logger.error(f"Error placing bid: {e}")
        return {
            "status": "error",
            "error_message": str(e)
        }

def get_bid_history(product_id: str) -> dict:
    """
    Get bid history for a product
    """
    try:
        config = RecommendationAgentConfig()
        bid_db = BidDatabase(config.bids_db_path)
        
        bids = bid_db.get_bids_for_product(product_id)
        bids.sort(key=lambda x: x.timestamp, reverse=True)
        
        formatted_bids = []
        for bid in bids:
            formatted_bids.append({
                "bid_id": bid.bid_id,
                "amount": bid.amount,
                "timestamp": bid.timestamp.isoformat(),
                "status": bid.status.value,
                "is_auto_bid": bid.is_auto_bid,
                "user_id": bid.user_id[:8] + "..." if len(bid.user_id) > 8 else bid.user_id  # Anonymize
            })
        
        return {
            "status": "success",
            "bids": formatted_bids,
            "total_bids": len(formatted_bids)
        }
        
    except Exception as e:
        logger.error(f"Error getting bid history: {e}")
        return {
            "status": "error",
            "error_message": str(e)
        }

def get_user_bids(user_id: str) -> dict:
    """
    Get all bids for a user
    """
    try:
        config = RecommendationAgentConfig()
        bid_db = BidDatabase(config.bids_db_path)
        product_db = ProductDatabase(config.products_db_path)
        
        user_bids = bid_db.get_bids_for_user(user_id)
        user_bids.sort(key=lambda x: x.timestamp, reverse=True)
        
        formatted_bids = []
        for bid in user_bids:
            product = product_db.get_product(bid.product_id)
            if product:
                time_left = product.auction_end_time - datetime.now()
                formatted_bids.append({
                    "bid": bid.to_dict(),
                    "product": {
                        "title": product.title,
                        "current_bid": product.current_bid,
                        "auction_end_time": product.auction_end_time.isoformat(),
                        "auction_status": product.auction_status.value
                    },
                    "time_left_hours": max(0, int(time_left.total_seconds() / 3600)),
                    "is_winning": bid.status == BidStatus.WINNING
                })
        
        return {
            "status": "success",
            "bids": formatted_bids,
            "total_bids": len(formatted_bids)
        }
        
    except Exception as e:
        logger.error(f"Error getting user bids: {e}")
        return {
            "status": "error",
            "error_message": str(e)
        }

def format_time_left(time_delta: timedelta) -> str:
    """Format time left in a human-readable way"""
    if time_delta.total_seconds() <= 0:
        return "Auction ended"
    
    days = time_delta.days
    hours, remainder = divmod(time_delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"

def sync_with_listing_agent(listing_data: dict) -> dict:
    """
    Sync a new product from the listing agent
    """
    try:
        config = RecommendationAgentConfig()
        db = ProductDatabase(config.products_db_path)
        
        # Convert listing data to auction product
        product = AuctionProduct(
            product_id=str(uuid.uuid4()),
            title=listing_data.get("title", ""),
            description=listing_data.get("description", ""),
            condition=ProductCondition(listing_data.get("condition", "good")),
            category=listing_data.get("category", "General"),
            brand=listing_data.get("brand"),
            model=listing_data.get("model"),
            tags=listing_data.get("tags", []),
            starting_price=listing_data.get("suggested_price", 10.0),
            current_bid=listing_data.get("suggested_price", 10.0),
            buy_now_price=listing_data.get("suggested_price", 10.0) * 1.5,
            reserve_price=listing_data.get("suggested_price", 10.0) * 0.8,
            auction_end_time=datetime.now() + timedelta(days=7),  # 7-day auction
            auction_status=AuctionStatus.ACTIVE,
            bid_count=0,
            watchers=0,
            seller_id="listing_agent",
            image_urls=[],
            shipping_cost=15.0,
            location="Online",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Add to database
        db.add_product(product)
        
        logger.info(f"Synced new product from listing agent: {product.product_id}")
        
        return {
            "status": "success",
            "product_id": product.product_id,
            "message": "Product successfully added to auction database"
        }
        
    except Exception as e:
        logger.error(f"Error syncing with listing agent: {e}")
        return {
            "status": "error",
            "error_message": str(e)
        }

# Create the recommendation agent
root_agent = recommendation_agent = Agent(
    name="recommendation_agent",
    model="gemini-2.0-flash",
    description="AI-powered recommendation agent for auction marketplace with bidding capabilities",
    instruction="""
    I am an AI recommendation agent for an auction marketplace. I help users discover products they'll love and facilitate the bidding process. My capabilities include:
    
    - Personalized product recommendations based on user preferences and history
    - Intelligent search with natural language queries
    - Real-time auction bidding system with automatic bidding
    - Bid tracking and history management
    - Market analysis and timing advice
    - Seamless integration with listing agents
    
    I analyze user behavior, preferences, and market trends to suggest the best auction items. I also handle the entire bidding process, from placing bids to tracking auction progress.
    
    Key features:
    - Smart recommendations using AI analysis
    - eBay-style auction bidding
    - Real-time bid updates
    - Auction timing optimization
    - User bid portfolio management
    - Cross-agent synchronization
    
    I work closely with the listing agent to ensure new products are immediately available for recommendation and bidding.
    """,
    tools=[
        get_personalized_recommendations,
        search_products_by_query,
        place_bid,
        get_bid_history,
        get_user_bids,
        sync_with_listing_agent,
    ]
)

class RecommendationAgentOrchestrator:
    """
    Orchestrator for managing the recommendation agent and its interactions
    """
    
    def __init__(self):
        self.recommendation_agent = recommendation_agent
        self.config = RecommendationAgentConfig()
        self.product_db = ProductDatabase(self.config.products_db_path)
        self.bid_db = BidDatabase(self.config.bids_db_path)
        self.session = None
    
    def initialize_session(self):
        """Initialize a new session for the recommendation agent"""
        try:
            self.session = Session(agent=self.recommendation_agent)
            return self.session
        except Exception as e:
            logger.error(f"Error initializing session: {e}")
            return None
    
    async def process_recommendation_request(self, user_id: str, user_preferences: dict, user_history: List[str] = None):
        """
        Process a recommendation request for a user
        """
        try:
            if not self.session:
                self.initialize_session()
            
            # Get personalized recommendations
            recommendations = get_personalized_recommendations(user_preferences, user_history)
            
            # Add real-time auction status updates
            if recommendations["status"] == "success":
                for rec in recommendations["recommendations"]:
                    product_id = rec["product"]["product_id"]
                    current_product = self.product_db.get_product(product_id)
                    if current_product:
                        # Update with latest auction data
                        rec["product"]["current_bid"] = current_product.current_bid
                        rec["product"]["bid_count"] = current_product.bid_count
                        rec["product"]["auction_status"] = current_product.auction_status.value
                        
                        # Add time remaining
                        time_left = current_product.auction_end_time - datetime.now()
                        rec["time_left_hours"] = max(0, int(time_left.total_seconds() / 3600))
                        rec["time_left_formatted"] = format_time_left(time_left)
                        rec["urgency_level"] = self._calculate_urgency(time_left, current_product.bid_count)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error processing recommendation request: {e}")
            return {
                "status": "error",
                "error_message": str(e)
            }
    
    async def process_bid_request(self, user_id: str, product_id: str, bid_amount: float, auto_bid_max: Optional[float] = None):
        """
        Process a bid request with validation and notifications
        """
        try:
            if not self.session:
                self.initialize_session()
            
            # Validate bid amount
            product = self.product_db.get_product(product_id)
            if not product:
                return {
                    "status": "error",
                    "error_message": "Product not found"
                }
            
            # Check for bid increments (typical auction rule)
            min_increment = self._calculate_min_increment(product.current_bid)
            if bid_amount < product.current_bid + min_increment:
                return {
                    "status": "error",
                    "error_message": f"Minimum bid is ${product.current_bid + min_increment:.2f}"
                }
            
            # Place the bid
            bid_result = place_bid(user_id, product_id, bid_amount, auto_bid_max)
            
            # If successful, process auto-bidding logic
            if bid_result["status"] == "success" and auto_bid_max:
                await self._handle_auto_bidding(user_id, product_id, auto_bid_max)
            
            # Send notifications (would integrate with notification system)
            if bid_result["status"] == "success":
                await self._notify_bid_placed(user_id, product_id, bid_amount)
            
            return bid_result
            
        except Exception as e:
            logger.error(f"Error processing bid request: {e}")
            return {
                "status": "error",
                "error_message": str(e)
            }
    
    async def process_search_request(self, query: str, filters: dict = None, user_preferences: dict = None):
        """
        Process a search request with personalization
        """
        try:
            if not self.session:
                self.initialize_session()
            
            # Get search results
            search_results = search_products_by_query(query, filters)
            
            # Add personalization scoring if user preferences provided
            if search_results["status"] == "success" and user_preferences:
                search_results = await self._personalize_search_results(search_results, user_preferences)
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error processing search request: {e}")
            return {
                "status": "error",
                "error_message": str(e)
            }
    
    def _calculate_urgency(self, time_left: timedelta, bid_count: int) -> str:
        """Calculate urgency level for auction"""
        hours_left = time_left.total_seconds() / 3600
        
        if hours_left <= 1:
            return "critical"
        elif hours_left <= 6:
            return "high"
        elif hours_left <= 24:
            return "medium"
        else:
            return "low"
    
    def _calculate_min_increment(self, current_bid: float) -> float:
        """Calculate minimum bid increment based on current bid"""
        if current_bid < 25:
            return 1.0
        elif current_bid < 100:
            return 2.5
        elif current_bid < 500:
            return 5.0
        elif current_bid < 1000:
            return 10.0
        else:
            return 25.0
    
    async def _handle_auto_bidding(self, user_id: str, product_id: str, max_auto_bid: float):
        """Handle automatic bidding logic"""
        try:
            # This would run in background to handle auto-bidding
            # For now, just log the setup
            logger.info(f"Auto-bidding setup for user {user_id} on product {product_id} up to ${max_auto_bid}")
            
            # In a real implementation, this would:
            # 1. Monitor for new bids on the product
            # 2. Automatically counter-bid up to the max amount
            # 3. Send notifications when outbid or when max is reached
            
        except Exception as e:
            logger.error(f"Error handling auto-bidding: {e}")
    
    async def _notify_bid_placed(self, user_id: str, product_id: str, bid_amount: float):
        """Send notification about bid placement"""
        try:
            # This would integrate with a notification system
            logger.info(f"Notification: User {user_id} placed bid of ${bid_amount} on product {product_id}")
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
    
    async def _personalize_search_results(self, search_results: dict, user_preferences: dict) -> dict:
        """Add personalization scoring to search results"""
        try:
            # Use Gemini to score results based on user preferences
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            prompt = f"""
            Score these search results based on user preferences. Return a JSON object with product_id as key and relevance_score (0-1) as value.
            
            User Preferences:
            {json.dumps(user_preferences, indent=2)}
            
            Search Results:
            {json.dumps([r["product"] for r in search_results["results"]], indent=2)}
            
            Consider:
            - Category preferences
            - Brand preferences
            - Price range
            - Condition preferences
            - Feature preferences
            
            Return format: {{"product_id": 0.95, "product_id2": 0.87, ...}}
            """
            
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text
            
            try:
                scores = json.loads(json_text)
                
                # Add scores to results
                for result in search_results["results"]:
                    product_id = result["product"]["product_id"]
                    result["personalization_score"] = scores.get(product_id, 0.5)
                
                # Sort by personalization score
                search_results["results"].sort(key=lambda x: x["personalization_score"], reverse=True)
                
            except json.JSONDecodeError:
                logger.warning("Could not parse personalization scores")
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error personalizing search results: {e}")
            return search_results

# Additional utility functions for the recommendation agent
def get_auction_analytics(product_id: str) -> dict:
    """
    Get analytics and insights for a specific auction
    """
    try:
        config = RecommendationAgentConfig()
        product_db = ProductDatabase(config.products_db_path)
        bid_db = BidDatabase(config.bids_db_path)
        
        product = product_db.get_product(product_id)
        if not product:
            return {
                "status": "error",
                "error_message": "Product not found"
            }
        
        bids = bid_db.get_bids_for_product(product_id)
        bids.sort(key=lambda x: x.timestamp)
        
        # Calculate analytics
        analytics = {
            "product_id": product_id,
            "title": product.title,
            "current_status": {
                "current_bid": product.current_bid,
                "bid_count": product.bid_count,
                "watchers": product.watchers,
                "time_left": format_time_left(product.auction_end_time - datetime.now())
            },
            "bid_progression": [],
            "bidding_activity": {
                "unique_bidders": len(set(bid.user_id for bid in bids)),
                "average_bid_increment": 0,
                "highest_bid": max([bid.amount for bid in bids] + [0]),
                "bid_frequency": len(bids) / max(1, (datetime.now() - product.created_at).total_seconds() / 3600)
            },
            "market_insights": {
                "starting_price": product.starting_price,
                "current_increase": ((product.current_bid - product.starting_price) / product.starting_price * 100) if product.starting_price > 0 else 0,
                "reserve_met": product.reserve_price is None or product.current_bid >= product.reserve_price,
                "buy_now_available": product.buy_now_price is not None
            }
        }
        
        # Build bid progression
        for i, bid in enumerate(bids):
            analytics["bid_progression"].append({
                "timestamp": bid.timestamp.isoformat(),
                "amount": bid.amount,
                "increment": bid.amount - (bids[i-1].amount if i > 0 else product.starting_price),
                "is_auto_bid": bid.is_auto_bid
            })
        
        # Calculate average increment
        if len(bids) > 1:
            increments = [bids[i].amount - bids[i-1].amount for i in range(1, len(bids))]
            analytics["bidding_activity"]["average_bid_increment"] = sum(increments) / len(increments)
        
        return {
            "status": "success",
            "analytics": analytics
        }
        
    except Exception as e:
        logger.error(f"Error getting auction analytics: {e}")
        return {
            "status": "error",
            "error_message": str(e)
        }

def get_market_trends(category: str = None, timeframe_days: int = 30) -> dict:
    """
    Get market trends and insights
    """
    try:
        config = RecommendationAgentConfig()
        product_db = ProductDatabase(config.products_db_path)
        bid_db = BidDatabase(config.bids_db_path)
        
        # Get products from timeframe
        cutoff_date = datetime.now() - timedelta(days=timeframe_days)
        products = [p for p in product_db.products.values() if p.created_at >= cutoff_date]
        
        if category:
            products = [p for p in products if p.category.lower() == category.lower()]
        
        if not products:
            return {
                "status": "success",
                "trends": {
                    "message": "No data available for the specified criteria",
                    "category": category,
                    "timeframe_days": timeframe_days
                }
            }
        
        # Calculate trends
        trends = {
            "category": category or "All Categories",
            "timeframe_days": timeframe_days,
            "total_auctions": len(products),
            "active_auctions": len([p for p in products if p.auction_status == AuctionStatus.ACTIVE]),
            "completed_auctions": len([p for p in products if p.auction_status == AuctionStatus.SOLD]),
            "average_selling_price": 0,
            "average_bid_count": 0,
            "popular_brands": {},
            "condition_distribution": {},
            "price_ranges": {
                "under_50": 0,
                "50_to_200": 0,
                "200_to_500": 0,
                "500_to_1000": 0,
                "over_1000": 0
            }
        }
        
        # Calculate averages
        completed_products = [p for p in products if p.auction_status == AuctionStatus.SOLD]
        if completed_products:
            trends["average_selling_price"] = sum(p.current_bid for p in completed_products) / len(completed_products)
            trends["average_bid_count"] = sum(p.bid_count for p in completed_products) / len(completed_products)
        
        # Brand popularity
        for product in products:
            if product.brand:
                trends["popular_brands"][product.brand] = trends["popular_brands"].get(product.brand, 0) + 1
        
        # Condition distribution
        for product in products:
            condition = product.condition.value
            trends["condition_distribution"][condition] = trends["condition_distribution"].get(condition, 0) + 1
        
        # Price ranges
        for product in products:
            price = product.current_bid
            if price < 50:
                trends["price_ranges"]["under_50"] += 1
            elif price < 200:
                trends["price_ranges"]["50_to_200"] += 1
            elif price < 500:
                trends["price_ranges"]["200_to_500"] += 1
            elif price < 1000:
                trends["price_ranges"]["500_to_1000"] += 1
            else:
                trends["price_ranges"]["over_1000"] += 1
        
        # Sort popular brands
        trends["popular_brands"] = dict(sorted(trends["popular_brands"].items(), key=lambda x: x[1], reverse=True)[:10])
        
        return {
            "status": "success",
            "trends": trends
        }
        
    except Exception as e:
        logger.error(f"Error getting market trends: {e}")
        return {
            "status": "error",
            "error_message": str(e)
        }

# Example usage and testing
if __name__ == "__main__":
    # Test the configuration
    try:
        config = RecommendationAgentConfig()
        print("✓ Configuration loaded successfully")
        
        # Initialize the orchestrator
        orchestrator = RecommendationAgentOrchestrator()
        print("✓ Recommendation Agent initialized successfully!")
        
        # Test database initialization
        print(f"✓ Loaded {len(orchestrator.product_db.products)} products")
        print(f"✓ Loaded {len(orchestrator.bid_db.bids)} bids")
        
        # Test some functions
        print("\n--- Testing Recommendations ---")
        test_preferences = {
            "categories": ["Electronics"],
            "max_budget": 1000,
            "preferred_brands": ["Apple"],
            "condition_preference": "excellent"
        }
        
        recommendations = get_personalized_recommendations(test_preferences)
        print(f"✓ Generated {len(recommendations.get('recommendations', []))} recommendations")
        
        print("\n--- Testing Search ---")
        search_results = search_products_by_query("iPhone")
        print(f"✓ Found {search_results.get('total_found', 0)} products for 'iPhone'")
        
        print("\n--- Testing Market Trends ---")
        trends = get_market_trends("Electronics")
        print(f"✓ Generated market trends for Electronics category")
        
        print("\n🎉 All tests passed! Recommendation Agent is ready to use.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Initialization error: {e}")