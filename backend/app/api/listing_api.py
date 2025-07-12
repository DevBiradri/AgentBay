from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from ..agents.listing_agent.agent import ListingAgentOrchestrator
from ..agents.recommendation_agent.agent import RecommendationAgentOrchestrator

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with frontend's URL for better security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ListingRequest(BaseModel):
    image_path: str
    user_preferences: Optional[dict] = None

class RecommendationRequest(BaseModel):
    query_string: str


@app.post("/api/create-listing")
async def create_listing(request: ListingRequest):
    if not os.path.exists(request.image_path):
        raise HTTPException(status_code=400, detail="Image file not found.")

    listing_agent = ListingAgentOrchestrator()

    result = await listing_agent.process_listing_request(request.image_path, request.user_preferences)
    if result.get("status") != "success":
        raise HTTPException(status_code=500, detail=result.get("error_message", "Unknown error occurred."))
    
    return result

@app.post("/api/recommendations")
async def get_recommendations(request: RecommendationRequest):
    recommendation_agent = RecommendationAgentOrchestrator()
    result = await recommendation_agent.process_recommendation_request(
        query_string=request.query_string
    )
    if result.get("status") != "success":
        raise HTTPException(status_code=500, detail=result.get("error_message", "Unknown error occurred."))
    return result

