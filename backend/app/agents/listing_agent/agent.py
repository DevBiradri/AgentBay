import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import os
from PIL import Image
from datetime import datetime
import asyncio
import base64
import io
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
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    def to_dict(self):
        d = asdict(self)
        # Convert ProductCondition enum to its value for JSON serialization
        if isinstance(d.get('condition'), ProductCondition):
            d['condition'] = d['condition'].value
        return d

class ListingAgentConfig:
    """Configuration for the listing agent"""
    def __init__(self):
        self.gemini_api_key = os.getenv("GOOGLE_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")

# Helper function to encode image for Gemini API
def encode_image_for_gemini(image_path: str) -> str:
    """
    Encode image to base64 for Gemini API
    """
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encoding image: {e}")
        raise

def analyze_product_image(image_path: str) -> dict:
    """
    Analyzes a product image using Gemini Vision API to extract product details.

    Args:
        image_path: Path to the product image file.

    Returns:
        dict: {'status': 'success', 'analysis': {...}} on success, or {'status': 'error', 'error_message': ...} on failure.
    """
    try:
        # Input validation
        if not image_path:
            return {"status": "error", "error_message": "No image path provided."}
        
        # Check if file exists
        if not os.path.exists(image_path):
            return {"status": "error", "error_message": f"Image file not found: {image_path}"}
        
        # Validate image file
        try:
            with Image.open(image_path) as img:
                img.verify()
        except Exception as img_error:
            return {"status": "error", "error_message": f"Invalid image file: {str(img_error)}"}
        
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Load and prepare the image
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
            
        # Create the image object for Gemini
        image = {
            'mime_type': 'image/jpeg',
            'data': image_data
        }
        
        # Detailed prompt for product analysis
        prompt = """
        Analyze this product image and provide detailed information in JSON format. Please be thorough and accurate.
        
        Return a JSON object with the following structure:
        {
            "product_type": "specific product type (e.g., 'smartphone', 'book', 'clothing', 'electronics')",
            "brand": "brand name if visible (null if not identifiable)",
            "model": "model name/number if visible (null if not identifiable)",
            "condition_assessment": "estimated condition ('new', 'like_new', 'excellent', 'good', 'fair', 'poor', 'for_parts')",
            "key_features": ["list", "of", "visible", "features"],
            "visible_defects": ["list", "of", "any", "visible", "damage", "or", "defects"],
            "material": "primary material if identifiable (e.g., 'plastic', 'metal', 'wood', 'fabric')",
            "color": "primary color(s)",
            "estimated_size": "estimated size description (e.g., 'small', 'medium', 'large')",
            "unique_identifiers": ["any", "visible", "serial", "numbers", "or", "identifiers"],
            "category_suggestions": ["primary category", "secondary category"],
            "notable_details": "any other important details about the product",
            "confidence_score": 0.0-1.0,
            "text_visible": "any visible text on the product",
            "packaging_present": true/false,
            "accessories_visible": ["list", "of", "visible", "accessories"]
        }
        
        Be conservative with brand/model identification - only include if you're confident.
        Focus on what you can actually see in the image.
        """
        
        # Make the API call
        response = model.generate_content([prompt, image])
        
        # Parse the response
        response_text = response.text.strip()
        
        # Extract JSON from response (handle potential markdown formatting)
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
        else:
            json_text = response_text
        
        try:
            analysis = json.loads(json_text)
        except json.JSONDecodeError:
            # Fallback: try to extract key information from text response
            analysis = {
                "product_type": "unknown",
                "brand": None,
                "model": None,
                "condition_assessment": "good",
                "key_features": [],
                "visible_defects": [],
                "material": None,
                "color": None,
                "estimated_size": "medium",
                "unique_identifiers": [],
                "category_suggestions": ["General"],
                "notable_details": f"Gemini analysis: {response_text[:200]}...",
                "confidence_score": 0.6,
                "text_visible": None,
                "packaging_present": False,
                "accessories_visible": []
            }
        
        # Add image dimensions
        with Image.open(image_path) as img:
            analysis["image_dimensions"] = f"{img.width}x{img.height}"
            analysis["image_format"] = img.format
            analysis["image_mode"] = img.mode
        
        logger.info(f"Successfully analyzed image: {image_path}")
        return {"status": "success", "analysis": analysis}
        
    except Exception as e:
        logger.error(f"Error analyzing image {image_path}: {e}")
        return {"status": "error", "error_message": f"Analysis failed: {str(e)}"}

def generate_listing_title(product_analysis: dict) -> dict:
    """
    Generates an SEO-friendly, compelling title using Gemini API.
    """
    try:
        if not product_analysis:
            return {"status": "error", "error_message": "No product analysis provided.", "title": ""}
        
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Create prompt for title generation
        prompt = f"""
        Based on the following product analysis, create a compelling, SEO-friendly auction listing title.
        
        Product Analysis:
        {json.dumps(product_analysis, indent=2)}
        
        Requirements:
        - Maximum 80 characters
        - Include brand and model if available
        - Highlight key features
        - Mention condition if not "good"
        - Make it attractive to buyers
        - Use proper capitalization
        
        Return only the title, no additional text.
        """
        
        response = model.generate_content(prompt)
        title = response.text.strip()
        
        # Ensure title is within length limit
        if len(title) > 80:
            title = title[:77] + "..."
        
        # Fallback if title is too short
        if len(title) < 10:
            product_type = product_analysis.get("product_type", "Item")
            brand = product_analysis.get("brand", "")
            title = f"{brand} {product_type}".strip() if brand else product_type
        
        logger.info(f"Generated title: {title}")
        return {"status": "success", "title": title}
        
    except Exception as e:
        logger.error(f"Error generating title: {e}")
        # Fallback title generation
        product_type = product_analysis.get("product_type", "Item")
        brand = product_analysis.get("brand", "")
        fallback_title = f"{brand} {product_type}".strip() if brand else f"Quality {product_type}"
        return {"status": "success", "title": fallback_title}

def generate_listing_description(product_analysis: dict) -> dict:
    """
    Generates a detailed, professional product description using Gemini API.
    """
    try:
        if not product_analysis:
            return {"status": "error", "error_message": "No product analysis provided.", "description": ""}
        
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Create prompt for description generation
        prompt = f"""
        Create a professional, detailed auction listing description based on this product analysis.
        
        Product Analysis:
        {json.dumps(product_analysis, indent=2)}
        
        Requirements:
        - Write in a professional, auction-style tone
        - Include all relevant details from the analysis
        - Mention condition and any defects honestly
        - Highlight key features and selling points
        - Include dimensions, materials, and technical details
        - Make it concise but informative
        - Use proper formatting with line breaks
        - Be truthful and accurate based on the analysis
        
        Format the description with clear sections and bullet points where appropriate.
        """
        
        response = model.generate_content(prompt)
        description = response.text.strip()
        
        logger.info("Generated description successfully")
        return {"status": "success", "description": description}
        
    except Exception as e:
        logger.error(f"Error generating description: {e}")
        # Fallback description
        product_type = product_analysis.get("product_type", "item")
        condition = product_analysis.get("condition_assessment", "good")
        fallback_desc = f"Quality {product_type} in {condition} condition. See photos for details. Perfect for collectors and enthusiasts!"
        return {"status": "success", "description": fallback_desc}

def assess_product_condition(product_analysis: dict) -> dict:
    """
    Assesses the product condition based on Gemini's visual analysis.
    """
    try:
        if not product_analysis:
            return {
                "status": "error",
                "error_message": "No product analysis provided",
                "condition": ProductCondition.GOOD.value,
                "confidence": 0.5
            }
        
        condition_assessment = product_analysis.get("condition_assessment", "good").lower()
        visible_defects = product_analysis.get("visible_defects", [])
        confidence_score = product_analysis.get("confidence_score", 0.7)
        
        condition_map = {
            "new": ProductCondition.NEW,
            "like_new": ProductCondition.LIKE_NEW,
            "like new": ProductCondition.LIKE_NEW,
            "excellent": ProductCondition.EXCELLENT,
            "good": ProductCondition.GOOD,
            "fair": ProductCondition.FAIR,
            "poor": ProductCondition.POOR,
            "for_parts": ProductCondition.FOR_PARTS,
            "for parts": ProductCondition.FOR_PARTS
        }
        
        # Find the best match
        condition = ProductCondition.GOOD  # Default
        for key, cond in condition_map.items():
            if key in condition_assessment:
                condition = cond
                break
        
        # Adjust confidence based on defects
        final_confidence = confidence_score
        if visible_defects:
            final_confidence *= 0.9  # Slightly reduce confidence if defects are present
        
        final_confidence = max(0.3, min(1.0, final_confidence))
        
        logger.info(f"Assessed condition: {condition.value} (confidence: {final_confidence:.2f})")
        
        return {
            "status": "success",
            "condition": condition.value,
            "confidence": final_confidence,
            "reasoning": f"Based on Gemini visual analysis with {len(visible_defects)} visible defects"
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
    Suggests pricing using Gemini API for market analysis.
    """
    try:
        if not product_analysis or not condition:
            return {
                "status": "error",
                "error_message": "Missing product analysis or condition.",
                "pricing": {}
            }
        
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Create prompt for pricing analysis
        prompt = f"""
        Analyze this product and suggest appropriate auction pricing.
        
        Product Details:
        - Type: {product_analysis.get('product_type', 'unknown')}
        - Brand: {product_analysis.get('brand', 'unknown')}
        - Model: {product_analysis.get('model', 'unknown')}
        - Condition: {condition}
        - Category: {product_analysis.get('category_suggestions', ['General'])[0]}
        - Visible Defects: {len(product_analysis.get('visible_defects', []))}
        - Key Features: {', '.join(product_analysis.get('key_features', []))}
        
        Please provide realistic pricing suggestions in JSON format:
        {{
            "suggested_starting_price": 0.00,
            "suggested_buy_now_price": 0.00,
            "price_range_min": 0.00,
            "price_range_max": 0.00,
            "pricing_rationale": "explanation of pricing logic",
            "market_factors": ["factor1", "factor2"],
            "confidence_level": "low/medium/high"
        }}
        
        Consider:
        - Current market values for similar items
        - Condition impact on pricing
        - Brand recognition and popularity
        - Rarity or commonality of the item
        - Typical auction dynamics
        
        Return only the JSON object.
        """
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Extract JSON from response
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
        else:
            json_text = response_text
        
        try:
            pricing = json.loads(json_text)
        except json.JSONDecodeError:
            # Fallback pricing logic
            category = product_analysis.get("category_suggestions", ["General"])[0]
            category_base_prices = {
                "Electronics": 50.0,
                "Art": 30.0,
                "Books": 10.0,
                "Clothing": 15.0,
                "Collectibles": 25.0,
                "Home & Garden": 20.0,
                "General": 20.0
            }
            
            base_price = category_base_prices.get(category, 20.0)
            condition_factors = {
                "new": 1.5, "like_new": 1.3, "excellent": 1.2,
                "good": 1.0, "fair": 0.7, "poor": 0.4, "for_parts": 0.2
            }
            
            factor = condition_factors.get(condition, 1.0)
            adjusted_price = base_price * factor
            
            pricing = {
                "suggested_starting_price": round(adjusted_price * 0.7, 2),
                "suggested_buy_now_price": round(adjusted_price * 1.3, 2),
                "price_range_min": round(adjusted_price * 0.5, 2),
                "price_range_max": round(adjusted_price * 1.5, 2),
                "pricing_rationale": f"Based on {category} category and {condition} condition",
                "market_factors": ["condition", "category"],
                "confidence_level": "medium"
            }
        
        logger.info(f"Suggested pricing: ${pricing['suggested_starting_price']} - ${pricing['suggested_buy_now_price']}")
        return {"status": "success", "pricing": pricing}
        
    except Exception as e:
        logger.error(f"Error suggesting pricing: {e}")
        return {
            "status": "error",
            "error_message": str(e),
            "pricing": {}
        }

def create_complete_listing(image_path: str, user_preferences: Optional[dict] = None) -> dict:
    """
    Creates a complete product listing from an image using Gemini API.
    """
    try:
        if user_preferences is None:
            user_preferences = {}
        
        logger.info(f"Creating complete listing for image: {image_path}")
        
        # Step 1: Analyze the product image with Gemini
        analysis_result = analyze_product_image(image_path)
        if analysis_result["status"] != "success":
            logger.error(f"Image analysis failed: {analysis_result['error_message']}")
            return analysis_result
        
        analysis = analysis_result["analysis"]
        logger.info("Image analysis completed successfully")
        
        # Step 2: Generate title
        title_result = generate_listing_title(analysis)
        if title_result["status"] != "success":
            logger.error(f"Title generation failed: {title_result['error_message']}")
            return title_result
        
        logger.info(f"Title generated: {title_result['title']}")
        
        # Step 3: Generate description
        desc_result = generate_listing_description(analysis)
        if desc_result["status"] != "success":
            logger.error(f"Description generation failed: {desc_result['error_message']}")
            return desc_result
        
        logger.info("Description generated successfully")
        
        # Step 4: Assess condition
        condition_result = assess_product_condition(analysis)
        if condition_result["status"] != "success":
            logger.error(f"Condition assessment failed: {condition_result['error_message']}")
            return condition_result
        
        logger.info(f"Condition assessed: {condition_result['condition']}")
        
        # Step 5: Suggest pricing
        pricing_result = suggest_pricing(analysis, condition_result["condition"])
        if pricing_result["status"] != "success":
            logger.error(f"Pricing suggestion failed: {pricing_result['error_message']}")
            return pricing_result
        
        logger.info("Pricing suggested successfully")
        
        # Step 6: Create a clean, non-redundant JSON for auction listing (no price_range, no shipping_info)
        product_json = {
            "title": title_result["title"].strip(),
            "description": desc_result["description"].strip(),
            "condition": condition_result["condition"],
            "category": analysis.get("category_suggestions", ["General"])[0],
            "suggested_price": pricing_result["pricing"].get("suggested_starting_price"),
            "tags": [tag for tag in analysis.get("key_features", []) if tag],
            "brand": analysis.get("brand"),
            "model": analysis.get("model"),
            "confidence_score": analysis.get("confidence_score", 0.7)
        }
        logger.info("Complete listing created successfully")
        return product_json
        
    except Exception as e:
        logger.error(f"Error creating complete listing: {e}")
        return {
            "status": "error",
            "error_message": f"Failed to create listing: {str(e)}"
        }

# Create the agent
root_agent = listing_agent = Agent(
    name="listing_agent",
    model="gemini-2.0-flash",
    description="AI-powered agent that creates complete auction listings from product images using Gemini Vision API",
    instruction="""
    I am an AI listing agent for an auction marketplace. I use Google's Gemini Vision API to analyze product images and create complete listings with:
    
    - Accurate product identification using computer vision
    - SEO-friendly titles generated by AI
    - Detailed descriptions based on visual analysis
    - Condition assessments from image analysis
    - Market-based pricing suggestions
    - Comprehensive shipping information
    - Complete product categorization
    
    I can analyze any product image and generate a professional auction listing automatically.
    
    To create a listing, provide me with the path to a product image, and I'll use Gemini's advanced vision capabilities to analyze it and generate all the necessary information for your auction.
    """,
    tools=[
        analyze_product_image,
        generate_listing_title,
        generate_listing_description,
        assess_product_condition,
        suggest_pricing,
        create_complete_listing,
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
        try:
            self.session = Session(agent=self.listing_agent)
            return self.session
        except Exception as e:
            logger.error(f"Error initializing session: {e}")
            return None
    
    async def process_listing_request(self, image_path: str, user_preferences: dict = None):
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
        
# Example usage
if __name__ == "__main__":
    # Test the configuration
    try:
        config = ListingAgentConfig()
        print("✓ Configuration loaded successfully")
        
        # Initialize the orchestrator
        orchestrator = ListingAgentOrchestrator()
        print("✓ Listing Agent initialized successfully!")
        
        
    except Exception as e:
        print(f"Error: {e}")
        logger.error(f"Initialization error: {e}")