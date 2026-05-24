"""FastAPI backend for restaurant recommendation system."""

import sys
import os
from pathlib import Path

# Add parent directory to Python path to import project modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from models.schemas import UserPreferences, BudgetBand
from data import get_restaurants
from phase3.integration import IntegrationLayer
from phase4.recommendation_engine import RecommendationEngine

app = FastAPI(title="Restaurant Recommendation API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests/responses
class RecommendationRequest(BaseModel):
    location: str
    budget: str  # "low", "medium", "high"
    cuisine: List[str]
    min_rating: float

class RestaurantResponse(BaseModel):
    name: str
    location: str
    rating: float
    cuisines: List[str]
    price_range: str
    address: str

class RecommendationResponse(BaseModel):
    rank: int
    restaurant: RestaurantResponse
    explanation: str

class SummaryResponse(BaseModel):
    recommendations: List[RecommendationResponse]
    overall_summary: Optional[str]

class MetadataResponse(BaseModel):
    locations: List[str]
    cuisines: List[str]

# Lazy load restaurants - only load when first request comes in
restaurants = None
_restaurants_loaded = False

def get_restaurants_cached():
    """Lazy load restaurants to reduce memory usage."""
    global restaurants, _restaurants_loaded
    if not _restaurants_loaded:
        restaurants = get_restaurants()
        _restaurants_loaded = True
        print(f"Loaded {len(restaurants)} restaurants")
    return restaurants

@app.get("/")
async def root():
    return {"message": "Restaurant Recommendation API"}

@app.get("/metadata")
async def get_metadata():
    """Get available locations and cuisines."""
    restaurants_list = get_restaurants_cached()
    
    locations = sorted(list(set(r.location for r in restaurants_list)))
    cuisines = sorted(list(set(c for r in restaurants_list for c in r.cuisines)))
    
    return MetadataResponse(locations=locations, cuisines=cuisines)

@app.post("/recommendations", response_model=SummaryResponse)
async def get_recommendations(request: RecommendationRequest):
    """Generate restaurant recommendations based on user preferences."""
    restaurants_list = get_restaurants_cached()
    
    try:
        # Convert budget string to BudgetBand enum
        budget_map = {
            "low": BudgetBand.LOW,
            "medium": BudgetBand.MEDIUM,
            "high": BudgetBand.HIGH
        }
        budget = budget_map.get(request.budget.lower(), BudgetBand.MEDIUM)
        
        # Create UserPreferences
        preferences = UserPreferences(
            location=request.location,
            budget=budget,
            cuisine=request.cuisine,
            min_rating=request.min_rating,
            extras={}
        )
        
        # Apply integration layer
        integration = IntegrationLayer(shortlist_cap=50)
        shortlist, prompt = integration.process(preferences, restaurants_list)
        
        # Generate recommendations using LLM
        groq_api_key = os.getenv("GROQ_API_KEY")
        engine = RecommendationEngine(
            groq_api_key=groq_api_key,
            model="llama-3.3-70b-versatile",
            timeout=30,
            max_retries=3,
        )
        
        summary = engine.generate_recommendations(prompt, shortlist)
        
        # Convert to API response format
        recommendations = []
        for rec in summary.recommendations:
            restaurant_response = RestaurantResponse(
                name=rec.restaurant.name,
                location=rec.restaurant.location,
                rating=rec.restaurant.rating,
                cuisines=rec.restaurant.cuisines,
                price_range=rec.restaurant.price_range,
                address=rec.restaurant.address
            )
            recommendations.append(RecommendationResponse(
                rank=rec.rank,
                restaurant=restaurant_response,
                explanation=rec.explanation
            ))
        
        return SummaryResponse(
            recommendations=recommendations,
            overall_summary=summary.overall_summary
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
