from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from ..agents.listing_agent.agent import ListingAgentOrchestrator

app = FastAPI()

class ListingRequest(BaseModel):
    image_path: str
    user_preferences: Optional[dict] = None



@app.post("/api/create-listing")
async def create_listing(request: ListingRequest):
    if not os.path.exists(request.image_path):
        raise HTTPException(status_code=400, detail="Image file not found.")

    listing_agent = ListingAgentOrchestrator()

    result = await listing_agent.process_listing_request(request.image_path, request.user_preferences)
    if result.get("status") != "success":
        raise HTTPException(status_code=500, detail=result.get("error_message", "Unknown error occurred."))
    
    return result
