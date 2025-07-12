from fastapi import FastAPI, HTTPException, Depends, Query, File, UploadFile, Form
from fastapi.responses import FileResponse
import fastapi
from typing import Optional
import os
import uuid
import shutil
import json
from pathlib import Path

from ..agents.listing_agent.agent import ListingAgentOrchestrator

from ..services.product_service import ProductService
from ..services.bid_service import BidService

from ..models.agent_models import Product, Bid
from ..models.request_models import BidCreateRequest, ProductCreateRequest
from ..models.converters.converters import product_db_to_pydantic, bid_db_to_pydantic

from ..enums.enums import BidStatus

app = FastAPI(title="AgentBay API", description="API for AgentBay auction platform")

# Dependency injection
def get_product_service():
    return ProductService()

def get_bid_service():
    return BidService()

# Helper functions
async def save_uploaded_file(file: UploadFile) -> str:
    """Save uploaded file and return the file path"""
    # Create uploads directory if it doesn't exist
    upload_dir = Path("uploads/images")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix if file.filename else ".jpg"
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = upload_dir / unique_filename
    
    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return str(file_path)

# === AGENT ENDPOINTS ===
@app.post("/api/agent/create-listing")
async def create_listing(
    image: UploadFile = File(..., description="Product image file"),
    user_preferences: Optional[str] = Form(None, description="User preferences as JSON string")
):
    """Create a new listing using the listing agent and save to database"""
    try:
        # Validate file type
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image.")
        
        # Save the uploaded image
        image_path = await save_uploaded_file(image)
        
        # Parse user preferences if provided
        preferences = {}
        if user_preferences:
            try:
                preferences = json.loads(user_preferences)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON in user_preferences.")
        
        # Process the listing request
        listing_agent = ListingAgentOrchestrator()
        result = await listing_agent.process_listing_request(image_path, preferences)
        
        if result.get("status") != "success":
            # Clean up the uploaded file if processing failed
            try:
                os.remove(image_path)
            except:
                pass
            raise HTTPException(status_code=500, detail=result.get("error_message", "Unknown error occurred."))
        
        # Extract product data and add image URL
        if "product" in result:
            try:
                product_data = result["product"]
                
                # Add the image path to the product data
                product_data["image_url"] = f"/uploads/images/{Path(image_path).name}"
                
                product = Product(**product_data)
                
                return {
                    "status": "success",
                    "message": "Listing created successfully",
                    "product": product.model_dump(),
                }
                
            except Exception as e:
                # Log the error but don't fail the request since the listing was successful
                return {
                    "status": "success",
                    "product": result["product"],
                    "database_warning": f"Failed to save to database: {str(e)}",
                    "image_url": f"/uploads/images/{Path(image_path).name}"
                }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process listing: {str(e)}")

# === PRODUCT ENDPOINTS ===

@app.post("/api/products", response_model=dict)
async def create_product(
    request: ProductCreateRequest,
    product_service: ProductService = Depends(get_product_service)
):
    """Create a new product"""
    try:
        product = Product(**request.dict())
        product_db = product_service.create_product(product)
        return {
            "id": product_db.id,
            "message": "Product created successfully",
            "product": product_db_to_pydantic(product_db).dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create product: {str(e)}")

@app.get("/api/products/{product_id}")
async def get_product(
    product_id: int,
    product_service: ProductService = Depends(get_product_service)
):
    """Get a specific product by ID"""
    product_db = product_service.get_product_by_id(product_id)
    if not product_db:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "product": product_db_to_pydantic(product_db).dict(),
        "database_info": {
            "created_at": product_db.created_at,
            "updated_at": product_db.updated_at
        }
    }

@app.get("/api/products/{product_id}/bids")
async def get_product_bids(
    product_id: int,
    limit: int = Query(100, ge=1, le=500, description="Maximum number of bids to return"),
    bid_service: BidService = Depends(get_bid_service)
):
    """Get all bids for a specific product"""
    try:
        bids_db = bid_service.get_bids_by_product(product_id, limit)
        bids = [bid_db_to_pydantic(b).to_dict() for b in bids_db]
        
        return {
            "product_id": product_id,
            "bids": bids,
            "bid_count": len(bids)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get bids: {str(e)}")

# === BID ENDPOINTS ===

@app.post("/api/products/{product_id}/bids")
async def create_bid(
    product_id: int,
    request: BidCreateRequest,
    bid_service: BidService = Depends(get_bid_service),
    product_service: ProductService = Depends(get_product_service)
):
    """Create a new bid for a product"""
    try:
        # Verify product exists
        if not product_service.get_product_by_id(product_id):
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Create bid object
        bid = Bid()
        bid.bid_id = request.bid_id
        bid.user_id = request.user_id
        bid.product_id = str(product_id)
        bid.amount = request.amount
        bid.timestamp = None
        bid.status = BidStatus.ACTIVE
        bid.is_auto_bid = request.is_auto_bid
        bid.max_auto_bid = request.max_auto_bid
        
        bid_db = bid_service.create_bid(bid, product_id)
        if not bid_db:
            raise HTTPException(status_code=500, detail="Failed to create bid")
        
        # Check if this is the new highest bid and update statuses
        highest_bid = bid_service.get_highest_bid_for_product(product_id)
        if highest_bid and highest_bid.id == bid_db.id:
            bid_service.process_outbid_updates(product_id, bid_db.id)
        
        return {
            "message": "Bid created successfully",
            "bid_id": bid_db.id,
            "bid": bid_db_to_pydantic(bid_db).to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create bid: {str(e)}")

@app.get("/api/users/{user_id}/bids")
async def get_user_bids(
    user_id: str,
    active_only: bool = Query(False, description="Return only active bids"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of bids to return"),
    bid_service: BidService = Depends(get_bid_service)
):
    """Get all bids for a specific user"""
    try:
        if active_only:
            bids_db = bid_service.get_active_bids_by_user(user_id)
        else:
            bids_db = bid_service.get_bids_by_user(user_id, limit)
        
        bids = [bid_db_to_pydantic(b).to_dict() for b in bids_db]
        
        return {
            "user_id": user_id,
            "bids": bids,
            "bid_count": len(bids)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user bids: {str(e)}")

@app.get("/api/products/{product_id}/highest-bid")
async def get_highest_bid(
    product_id: int,
    bid_service: BidService = Depends(get_bid_service)
):
    """Get the highest bid for a specific product"""
    try:
        bid_db = bid_service.get_highest_bid_for_product(product_id)
        if not bid_db:
            return {"message": "No bids found for this product"}
        
        return {
            "product_id": product_id,
            "highest_bid": bid_db_to_pydantic(bid_db).to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get highest bid: {str(e)}")
