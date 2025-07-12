import json
import logging
from typing import List, Optional
import os
from datetime import datetime, timedelta
import asyncio
import uuid

import google.generativeai as genai
from google.adk.agents import Agent
from google.adk.sessions import Session

from ...services.product_service import ProductService
from ...services.bid_service import BidService

from ...models.agent_models import Product, Bid
from ...enums.enums import AuctionStatus, BidStatus, ProductCondition
from ...models.converters.converters import product_db_to_pydantic, bid_db_to_pydantic
 
from dotenv import load_dotenv
 
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

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
    """
)

class RecommendationAgentOrchestrator:
    """
    Orchestrator for managing the recommendation agent and its interactions
    """
    
    def __init__(self):
        self.recommendation_agent = recommendation_agent
        self.gemini_api_key = os.getenv("GOOGLE_API_KEY")
        self.product_service = ProductService()
        self.bid_service = BidService()
        self.session = None
        
        if not self.gemini_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
    
    def initialize_session(self):
        """Initialize a new session for the recommendation agent"""
        try:
            self.session = Session(agent=self.recommendation_agent)
            return self.session
        except Exception as e:
            logger.error(f"Error initializing session: {e}")
            return None
    
    async def process_recommendation_request(self, query_string: str, ):
        """
        Process a recommendation request based on a natural language query string.
        """
        try:
            if not self.session:
                self.initialize_session()
            
            products_db = self.product_service.get_all_products()
            products_list = [product_db_to_pydantic(product) for product in products_db]

            # Convert products to dict format for Gemini
            products_for_gemini = []
            for product in products_list:
                products_for_gemini.append({
                    "title": product.title,
                    "description": product.description,
                    "category": product.category,
                    "brand": product.brand,
                    "model": product.model,
                    "current_bid": product.current_bid,
                    "suggested_price": product.suggested_price,
                    "tags": product.tags
                })

            # Use Gemini to find related products
            model = genai.GenerativeModel('gemini-2.0-flash')
            prompt = f"""
            You are an AI assistant. Based on the user query, return a JSON array of products that match the request.
            
            Query: "{query_string}"
            
            Available Products:
            {products_for_gemini}
            
            Return only a JSON array of the matching products (use the exact product objects from the list above).
            """
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON from the response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text
            
            recommended_products = json.loads(json_text)
            
            return {
                "status": "success",
                "results": recommended_products,
                "total_found": len(recommended_products)
            }
        
        except Exception as e:
            logger.error(f"Error processing recommendation request: {e}")
            return {
                "status": "error",
                "error_message": str(e)
            }