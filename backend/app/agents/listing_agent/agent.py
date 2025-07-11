import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import os
from PIL import Image
from datetime import datetime

# Google ADK imports
from google.adk.agents import Agent
from google.adk.sessions import Session

from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductCondition(Enum):
    NEW = "new"
    LIKE_NEW = "like_new"
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    FOR_PARTS = "for_parts"

@dataclass
class ProductListing:
    title: str
    description: str
    condition: ProductCondition
    category: str
    suggested_price: Optional[float] = None
    price_range: Optional[Tuple[float, float]] = None
    shipping_info: Optional[Dict[str, Any]] = None
    tags: List[str] = None
    dimensions: Optional[Dict[str, str]] = None
    weight_estimate: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    confidence_score: float = 0.0
    
    def to_dict(self):
        d = asdict(self)
        # Convert ProductCondition enum to its value for JSON serialization
        if isinstance(d.get('condition'), ProductCondition):
            d['condition'] = d['condition'].value
        return d

class ListingAgentConfig:
    """Configuration for the listing agent"""
    def __init__(self):
        self.gemini_api_key = os.getenv("GOOGLE_API_KEY", "your-gemini-api-key")

# Tool Functions for the Listing Agent
def analyze_product_image(image_path: str) -> dict:
    """
    Analyzes a product image to extract product details such as brand, model, condition, features, and more.

    Args:
        image_path: Path to the product image file.

    Returns:
        dict: {'status': 'success', 'analysis': {...}} on success, or {'status': 'error', 'error_message': ...} on failure.
    """
    try:
        if not image_path:
            return {"status": "error", "error_message": "No image path provided."}
        image = Image.open(image_path)
        # Example: Just get image size and mode for demo; real logic would use vision models or APIs
        analysis = {
            "product_type": "unknown",
            "brand": None,
            "model": None,
            "condition_assessment": "good",
            "key_features": [],
            "visible_defects": [],
            "material": None,
            "color": None,
            "estimated_dimensions": f"{image.size[0]}x{image.size[1]}",
            "unique_identifiers": [],
            "category_suggestions": ["General"],
            "notable_details": f"Image mode: {image.mode}",
            "confidence_score": 0.7
        }
        return {"status": "success", "analysis": analysis}
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        return {"status": "error", "error_message": str(e)}

def generate_listing_title(product_analysis: dict) -> dict:
    """
    Generates an SEO-friendly, compelling title for the product listing.

    Args:
        product_analysis: Dictionary containing the product analysis results.

    Returns:
        dict: {'status': 'success', 'title': ...} or {'status': 'error', 'error_message': ...}
    """
    try:
        if not product_analysis:
            return {"status": "error", "error_message": "No product analysis provided.", "title": ""}
        brand = product_analysis.get("brand") or "Product"
        model = product_analysis.get("model") or ""
        key_features = product_analysis.get("key_features", [])
        features_str = ", ".join(key_features[:2]) if key_features else ""
        title = f"{brand} {model} {features_str}".strip()
        # Truncate to 80 chars
        title = title[:80]
        return {"status": "success", "title": title}
    except Exception as e:
        logger.error(f"Error generating title: {e}")
        return {"status": "error", "error_message": str(e), "title": ""}

def generate_listing_description(product_analysis: dict) -> dict:
    """
    Generates a detailed, professional product description for the listing.

    Args:
        product_analysis: Dictionary containing the product analysis results.

    Returns:
        dict: {'status': 'success', 'description': ...} or {'status': 'error', 'error_message': ...}
    """
    try:
        if not product_analysis:
            return {"status": "error", "error_message": "No product analysis provided.", "description": ""}
        lines = [f"This is a listing for a {product_analysis.get('product_type', 'product')}.", ""]
        if product_analysis.get("brand"):
            lines.append(f"Brand: {product_analysis['brand']}")
        if product_analysis.get("model"):
            lines.append(f"Model: {product_analysis['model']}")
        if product_analysis.get("condition_assessment"):
            lines.append(f"Condition: {product_analysis['condition_assessment']}")
        if product_analysis.get("key_features"):
            lines.append("Key Features: " + ", ".join(product_analysis["key_features"]))
        if product_analysis.get("material"):
            lines.append(f"Material: {product_analysis['material']}")
        if product_analysis.get("color"):
            lines.append(f"Color: {product_analysis['color']}")
        if product_analysis.get("estimated_dimensions"):
            lines.append(f"Estimated Dimensions: {product_analysis['estimated_dimensions']}")
        if product_analysis.get("notable_details"):
            lines.append(f"Notable Details: {product_analysis['notable_details']}")
        lines.append("")
        lines.append("Bid now to own this item!")
        description = "\n".join(lines)
        return {"status": "success", "description": description}
    except Exception as e:
        logger.error(f"Error generating description: {e}")
        return {"status": "error", "error_message": str(e), "description": ""}

def assess_product_condition(product_analysis: dict) -> dict:
    """
    Assesses the product condition based on visual analysis.
    
    Args:
        product_analysis: Dictionary containing the product analysis results
        
    Returns:
        dict: A dictionary containing the assessed condition and confidence
    """
    try:
        condition_assessment = product_analysis.get("condition_assessment", "good").lower()
        
        condition_map = {
            "new": ProductCondition.NEW,
            "like new": ProductCondition.LIKE_NEW,
            "excellent": ProductCondition.EXCELLENT,
            "good": ProductCondition.GOOD,
            "fair": ProductCondition.FAIR,
            "poor": ProductCondition.POOR,
            "for parts": ProductCondition.FOR_PARTS
        }
        
        # Find the best match
        condition = ProductCondition.GOOD  # Default
        for key, cond in condition_map.items():
            if key in condition_assessment:
                condition = cond
                break
        
        return {
            "status": "success",
            "condition": condition.value,
            "confidence": product_analysis.get("confidence_score", 0.7)
        }
        
    except Exception as e:
        logger.error(f"Error assessing condition: {e}")
        return {
            "status": "error",
            "error_message": str(e),
            "condition": ProductCondition.GOOD.value,
            "confidence": 0.5
        }

def suggest_pricing(product_analysis: dict, condition: str) -> dict:
    """
    Suggests pricing for the product based on analysis and condition.

    Args:
        product_analysis: Dictionary containing the product analysis results.
        condition: The assessed condition of the product.

    Returns:
        dict: {'status': 'success', 'pricing': {...}} or {'status': 'error', 'error_message': ...}
    """
    try:
        if not product_analysis or not condition:
            return {
                "status": "error",
                "error_message": "Missing product analysis or condition.",
                "pricing": {}
            }
        # Demo logic: price based on condition
        base_price = 20.0
        condition_factor = {
            "new": 1.5,
            "like_new": 1.3,
            "excellent": 1.2,
            "good": 1.0,
            "fair": 0.7,
            "poor": 0.4,
            "for_parts": 0.2
        }.get(condition, 1.0)
        suggested_starting_price = round(base_price * condition_factor, 2)
        suggested_buy_now_price = round(suggested_starting_price * 1.5, 2)
        price_range_min = round(suggested_starting_price * 0.8, 2)
        price_range_max = round(suggested_buy_now_price * 1.1, 2)
        pricing = {
            "suggested_starting_price": suggested_starting_price,
            "suggested_buy_now_price": suggested_buy_now_price,
            "price_range_min": price_range_min,
            "price_range_max": price_range_max,
            "pricing_rationale": f"Base price adjusted for condition '{condition}'.",
            "market_factors": ["condition", "base_price"],
            "confidence_level": "medium"
        }
        return {"status": "success", "pricing": pricing}
    except Exception as e:
        logger.error(f"Error suggesting pricing: {e}")
        return {
            "status": "error",
            "error_message": str(e),
            "pricing": {}
        }

def generate_shipping_info(product_analysis: dict) -> dict:
    """
    Generates shipping information and label details for the product.

    Args:
        product_analysis: Dictionary containing the product analysis results.

    Returns:
        dict: {'status': 'success', 'shipping_info': {...}} or {'status': 'error', 'error_message': ...}
    """
    try:
        if not product_analysis:
            return {"status": "error", "error_message": "No product analysis provided.", "shipping_info": {}}
        # Demo logic: estimate based on dimensions if available
        dims = product_analysis.get("estimated_dimensions", "12x12").split("x")
        length = dims[0] if len(dims) > 0 else "12"
        width = dims[1] if len(dims) > 1 else "12"
        height = dims[2] if len(dims) > 2 else "6"
        shipping_info = {
            "estimated_weight": "2 lb",
            "estimated_dimensions": {"length": length, "width": width, "height": height},
            "packaging_requirements": ["bubble wrap", "sturdy box"],
            "shipping_category": "standard",
            "recommended_services": ["USPS Priority"],
            "handling_instructions": "Handle with care",
            "insurance_recommended": False,
            "estimated_shipping_cost_range": {"min": 8.00, "max": 15.00}
        }
        return {"status": "success", "shipping_info": shipping_info}
    except Exception as e:
        logger.error(f"Error generating shipping info: {e}")
        return {"status": "error", "error_message": str(e), "shipping_info": {}}

def create_complete_listing(image_path: str, user_preferences: dict) -> dict:
    """
    Creates a complete product listing from an image by orchestrating all the individual tools.
    
    Args:
        image_path: Path to the product image file
        user_preferences: Optional dictionary with user preferences for pricing, shipping, etc.
        
    Returns:
        dict: A dictionary containing the complete listing with all details
    """
    try:
        logger.info(f"Creating complete listing for image: {image_path}")
        
        # Step 1: Perform web image search
        search_result = perform_web_image_search(image_path)
        if search_result["status"] != "success":
            return search_result

        product_info = search_result["product_info"]

        # Step 2: Analyze the product image
        analysis_result = analyze_product_image(image_path)
        if analysis_result["status"] != "success":
            return analysis_result
        
        analysis = analysis_result["analysis"]
        
        # Step 2: Generate title
        title_result = generate_listing_title(analysis)
        if title_result["status"] != "success":
            return title_result
        
        # Step 3: Generate description
        desc_result = generate_listing_description(analysis)
        if desc_result["status"] != "success":
            return desc_result
        
        # Step 4: Assess condition
        condition_result = assess_product_condition(analysis)
        if condition_result["status"] != "success":
            return condition_result
        
        # Step 5: Suggest pricing
        pricing_result = suggest_pricing(analysis, condition_result["condition"])
        if pricing_result["status"] != "success":
            return pricing_result
        
        # Step 6: Generate shipping info
        shipping_result = generate_shipping_info(analysis)
        if shipping_result["status"] != "success":
            return shipping_result
        
        # Step 7: Create complete listing
        listing = ProductListing(
            title=title_result["title"],
            description=desc_result["description"],
            condition=ProductCondition(condition_result["condition"]),
            category=analysis.get("category_suggestions", ["General"])[0],
            suggested_price=pricing_result["pricing"]["suggested_starting_price"],
            price_range=(
                pricing_result["pricing"]["price_range_min"],
                pricing_result["pricing"]["price_range_max"]
            ),
            shipping_info=shipping_result["shipping_info"],
            tags=analysis.get("key_features", []),
            brand=analysis.get("brand"),
            model=analysis.get("model"),
            confidence_score=analysis.get("confidence_score", 0.7)
        )
        
        return {
            "status": "success",
            "listing": listing.to_dict(),
            "analysis": analysis,
            "pricing_details": pricing_result["pricing"]
        }
        
    except Exception as e:
        logger.error(f"Error creating complete listing: {e}")
        return {
            "status": "error",
            "error_message": str(e)
        }

def communicate_with_pricing_agent(listing_data: dict, message_type: str) -> dict:
    """
    Communicates with the pricing agent for market analysis and pricing updates.
    
    Args:
        listing_data: Dictionary containing listing information
        message_type: Type of communication (e.g., "market_analysis", "price_update")
        
    Returns:
        dict: Response from the pricing agent
    """
    try:
        # This is a placeholder for inter-agent communication
        # In a real implementation, this would communicate with other ADK agents
        
        message = {
            "timestamp": datetime.now().isoformat(),
            "sender": "listing_agent",
            "receiver": "pricing_agent",
            "message_type": message_type,
            "payload": listing_data
        }
        
        logger.info(f"Sending message to pricing agent: {message_type}")
        
        # Simulate response from pricing agent
        return {
            "status": "success",
            "message": "Message sent to pricing agent",
            "response": "Pricing agent acknowledged the request"
        }
        
    except Exception as e:
        logger.error(f"Error communicating with pricing agent: {e}")
        return {
            "status": "error",
            "error_message": str(e)
        }

def communicate_with_shipping_agent(listing_data: dict, message_type: str) -> dict:
    """
    Communicates with the shipping agent for shipping optimization and updates.
    
    Args:
        listing_data: Dictionary containing listing information
        message_type: Type of communication (e.g., "shipping_optimization", "cost_update")
        
    Returns:
        dict: Response from the shipping agent
    """
    try:
        # This is a placeholder for inter-agent communication
        # In a real implementation, this would communicate with other ADK agents
        
        message = {
            "timestamp": datetime.now().isoformat(),
            "sender": "listing_agent",
            "receiver": "shipping_agent",
            "message_type": message_type,
            "payload": listing_data
        }
        
        logger.info(f"Sending message to shipping agent: {message_type}")
        
        # Simulate response from shipping agent
        return {
            "status": "success",
            "message": "Message sent to shipping agent",
            "response": "Shipping agent acknowledged the request"
        }
        
    except Exception as e:
        logger.error(f"Error communicating with shipping agent: {e}")
        return {
            "status": "error",
            "error_message": str(e)
        }
    
def perform_web_image_search(image_path: str) -> dict:
    """
    Performs a web image search using Google's ADK to identify the product.

    Args:
        image_path: Path to the product image file.

    Returns:
        dict: {'status': 'success', 'product_info': {...}} on success, or {'status': 'error', 'error_message': ...} on failure.
    """
    """
    Performs a web image search using image features to simulate product identification.

    Args:
        image_path: Path to the product image file.

    Returns:
        dict: {'status': 'success', 'product_info': {...}} on success, or {'status': 'error', 'error_message': ...} on failure.
    """
    try:
        if not image_path:
            return {"status": "error", "error_message": "No image path provided."}
        image = Image.open(image_path)
        # Simulate extracting features from the image
        width, height = image.size
        mode = image.mode
        # Simulate a lookup table for demo purposes
        if width > 1000 and height > 1000:
            product_info = {
                "product_name": "Large Canvas Print",
                "brand": "Artify",
                "category": "Home Decor",
                "confidence_score": 0.92
            }
        elif mode == "RGB":
            product_info = {
                "product_name": "Colorful Mug",
                "brand": "MugMaster",
                "category": "Kitchenware",
                "confidence_score": 0.81
            }
        else:
            product_info = {
                "product_name": "Generic Product",
                "brand": "Brandless",
                "category": "Miscellaneous",
                "confidence_score": 0.65
            }
        return {"status": "success", "product_info": product_info}
    except Exception as e:
        logger.error(f"Error performing web image search: {e}")
        return {"status": "error", "error_message": str(e)}

root_agent = listing_agent = Agent(
    name="listing_agent",
    model="gemini-2.0-flash",
    description="AI-powered agent that creates complete auction listings from product images",
    instruction="""
    I am an AI listing agent for an auction marketplace. I can analyze product images and create complete listings with:
    
    - SEO-friendly titles
    - Detailed descriptions
    - Condition assessments
    - Pricing suggestions
    - Shipping information
    - Complete product details
    
    I work with other agents in the system to provide the best possible listings for your auction marketplace.
    
    To create a listing, provide me with the path to a product image, and I'll generate all the necessary information.
    """,
    tools=[
        perform_web_image_search,
        analyze_product_image,
        generate_listing_title,
        generate_listing_description,
        assess_product_condition,
        suggest_pricing,
        generate_shipping_info,
        create_complete_listing,
        communicate_with_pricing_agent,
        communicate_with_shipping_agent
    ]
)

# Additional configuration for multi-agent communication
class ListingAgentOrchestrator:
    """
    Orchestrator for managing the listing agent and its interactions with other agents
    """
    
    def __init__(self):
        self.listing_agent = listing_agent
        self.config = ListingAgentConfig()
        self.session = None
    
    def initialize_session(self):
        """Initialize a new session for the listing agent"""
        self.session = Session(
            agent=self.listing_agent
        )
        return self.session
    
    async def process_listing_request(self, image_path: str, user_preferences: dict):
        """
        Process a complete listing request using the orchestrated agent system
        """
        try:
            if not self.session:
                self.initialize_session()
            
            # Create the listing using the main tool
            result = create_complete_listing(image_path, user_preferences)
            
            if result["status"] == "success":
                # Communicate with other agents
                await self.notify_other_agents(result["listing"])
                
            return result
            
        except Exception as e:
            logger.error(f"Error processing listing request: {e}")
            return {
                "status": "error",
                "error_message": str(e)
            }
    
    async def notify_other_agents(self, listing_data: dict):
        """
        Notify other agents about the new listing
        """
        try:
            # Notify pricing agent
            pricing_response = communicate_with_pricing_agent(
                listing_data, "new_listing_created"
            )
            logger.info(f"Pricing agent response: {pricing_response}")
            
            # Notify shipping agent
            shipping_response = communicate_with_shipping_agent(
                listing_data, "shipping_analysis_request"
            )
            logger.info(f"Shipping agent response: {shipping_response}")
            
        except Exception as e:
            logger.error(f"Error notifying other agents: {e}")

# Example usage
if __name__ == "__main__":
    # Initialize the orchestrator
    orchestrator = ListingAgentOrchestrator()
    
    # Example usage
    print("Listing Agent initialized successfully!")
    RESULT = orchestrator.process_listing_request("image.jpg")
    print(f"Result: {RESULT}")