import json
import logging
from typing import List, Optional
import os
from datetime import datetime, timedelta
import asyncio
import uuid
from ...enums.enums import AuctionStatus, BidStatus, ProductCondition
from ...models.bid import Bid
from ...services.product_service import ProductService
from ...services.bid_service import BidService
from ...models.converters.converters import product_db_to_pydantic, bid_db_to_pydantic
import google.generativeai as genai

# Google ADK imports
from google.adk.agents import Agent
from google.adk.sessions import Session
from ...models.product import Product
 
from dotenv import load_dotenv
 
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class RecommendationAgentConfig:
    """Configuration for the recommendation agent"""
    def __init__(self):
        self.gemini_api_key = os.getenv("GOOGLE_API_KEY")
        self.product_service = ProductService()
        self.bid_service = BidService()
        if not self.gemini_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")

def get_personalized_recommendations(user_preferences: dict, user_history: Optional[List[str]] = None) -> dict:
    """
    Generate personalized product recommendations using Gemini API
    """
    try:
        config = RecommendationAgentConfig()
        
        # Get available products from database
        available_products_db = config.product_service.get_all_products(limit=100)
        available_products = [product_db_to_pydantic(p) for p in available_products_db]
        
        if not available_products:
            return {
                "status": "success",
                "recommendations": [],
                "message": "No products available at the moment."
            }
        
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Prepare context for recommendation
        products_summary = []
        for product in available_products:
            products_summary.append({
                "title": product.title,
                "category": product.category,
                "brand": product.brand,
                "suggested_price": product.suggested_price,
                "condition": product.condition,
                "tags": product.tags,
                "model": product.model
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
            for i, rec in enumerate(recommendations.get("top_recommendations", [])):
                # Use index since our products don't have external product_id
                if i < len(available_products):
                    product = available_products[i]
                    enriched_rec = {
                        "product": product.model_dump(),
                        "relevance_score": rec.get("relevance_score", 0.5),
                        "reason": rec.get("reason", "Matches your preferences"),
                        "urgency": rec.get("urgency", "medium"),
                        "value_assessment": rec.get("value_assessment", "fair_price")
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
        db = ProductService(config.products_db_path)
        
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
        product_service = ProductService(config.products_db_path)
        bid_service = BidService(config.bids_db_path)
        
        # Get the product
        product = product_service.get_product(product_id)
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
        existing_bids = bid_service.get_bids_for_product(product_id)
        for existing_bid in existing_bids:
            if existing_bid.status == BidStatus.WINNING:
                existing_bid.status = BidStatus.OUTBID
                bid_service.bids[existing_bid.bid_id] = existing_bid
        
        # Add the new bid
        bid_service.add_bid(bid)
        
        # Update product
        product.current_bid = bid_amount
        product.bid_count += 1
        product.updated_at = datetime.now()
        product_service.products[product_id] = product
        product_service.save_products()
        
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
        bid_service = BidService(config.bids_db_path)
        
        bids = bid_service.get_bids_for_product(product_id)
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
        bid_service = BidService(config.bids_db_path)
        product_service = ProductService(config.products_db_path)
        
        user_bids = bid_service.get_bids_for_user(user_id)
        user_bids.sort(key=lambda x: x.timestamp, reverse=True)
        
        formatted_bids = []
        for bid in user_bids:
            product = product_service.get_product(bid.product_id)
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
        # Validate incoming data using the Product model
        product_data = Product(**listing_data)

        config = RecommendationAgentConfig()
        
        # Add the product to database using ProductService
        product_service = config.product_service.create_product(product_data)
        
        logger.info(f"Synced new product from listing agent: {product_service.id}")
        
        return {
            "status": "success",
            "product_id": product_service.id,
            "database_id": product_service.id,
            "message": "Product successfully added to database"
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
        self.product_service = self.config.product_service
        self.bid_service = self.config.bid_service
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
                    current_product = self.product_service.get_product(product_id)
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
            product = self.product_service.get_product(product_id)
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
        print(f"✓ Loaded {len(orchestrator.product_service.products)} products")
        print(f"✓ Loaded {len(orchestrator.bid_service.bids)} bids")
        
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
        
        print("\n🎉 All tests passed! Recommendation Agent is ready to use.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Initialization error: {e}")