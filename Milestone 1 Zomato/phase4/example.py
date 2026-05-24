"""Example usage of Phase 4 Recommendation Engine."""

from models.schemas import Restaurant, BudgetBand
from phase4.recommendation_engine import RecommendationEngine


def main():
    """Demonstrate Phase 4 recommendation engine usage."""
    
    # Create sample shortlist
    shortlist = [
        Restaurant(
            id="1",
            name="Italian Place",
            location="Bangalore",
            cuisines=["Italian", "Pizza"],
            cost_for_two=500,
            cost_band=BudgetBand.MEDIUM,
            rating=4.5
        ),
        Restaurant(
            id="2",
            name="Chinese Wok",
            location="Bangalore",
            cuisines=["Chinese", "Asian"],
            cost_for_two=300,
            cost_band=BudgetBand.LOW,
            rating=4.2
        ),
        Restaurant(
            id="3",
            name="Fine Dining",
            location="Delhi",
            cuisines=["Italian", "Continental"],
            cost_for_two=2000,
            cost_band=BudgetBand.HIGH,
            rating=4.8
        ),
        Restaurant(
            id="4",
            name="Pizza Hut",
            location="Bangalore",
            cuisines=["Italian", "Pizza", "Fast Food"],
            cost_for_two=400,
            cost_band=BudgetBand.LOW,
            rating=3.9
        ),
        Restaurant(
            id="5",
            name="Truffles",
            location="Bangalore",
            cuisines=["American", "Burgers"],
            cost_for_two=600,
            cost_band=BudgetBand.MEDIUM,
            rating=4.6
        ),
    ]
    
    # Create a sample prompt (normally from Phase 3)
    prompt = """User Preferences:
{
  "location": "Bangalore",
  "budget": "medium",
  "cuisine": ["Italian"],
  "min_rating": 4.0,
  "extras": {}
}

Available Restaurants:
[
  {
    "id": "1",
    "name": "Italian Place",
    "location": "Bangalore",
    "cuisines": ["Italian", "Pizza"],
    "cost_for_two": 500,
    "cost_band": "medium",
    "rating": 4.5
  },
  {
    "id": "2",
    "name": "Chinese Wok",
    "location": "Bangalore",
    "cuisines": ["Chinese", "Asian"],
    "cost_for_two": 300,
    "cost_band": "low",
    "rating": 4.2
  },
  {
    "id": "3",
    "name": "Fine Dining",
    "location": "Delhi",
    "cuisines": ["Italian", "Continental"],
    "cost_for_two": 2000,
    "cost_band": "high",
    "rating": 4.8
  },
  {
    "id": "4",
    "name": "Pizza Hut",
    "location": "Bangalore",
    "cuisines": ["Italian", "Pizza", "Fast Food"],
    "cost_for_two": 400,
    "cost_band": "low",
    "rating": 3.9
  },
  {
    "id": "5",
    "name": "Truffles",
    "location": "Bangalore",
    "cuisines": ["American", "Burgers"],
    "cost_for_two": 600,
    "cost_band": "medium",
    "rating": 4.6
  }
]

Please rank the top 5 restaurants from the list above that best match the user's preferences. 
For each recommendation, provide:
1. Restaurant name (exactly as shown)
2. Rank (1-5)
3. Explanation of why it fits the user's preferences

Format your response as a JSON object with the following structure:
{
  "recommendations": [
    {
      "restaurant_name": "exact name from list",
      "rank": 1,
      "explanation": "brief explanation"
    }
  ],
  "overall_summary": "optional one-line summary"
}"""
    
    # Initialize recommendation engine
    # Note: Set GROQ_API_KEY environment variable before running
    try:
        engine = RecommendationEngine(
            model="llama3-70b-8192",
            timeout=30,
            max_retries=3,
        )
        
        print("Generating recommendations using Groq LLM...")
        summary = engine.generate_recommendations(prompt, shortlist)
        
        print(f"\nGenerated {len(summary.recommendations)} recommendations:\n")
        
        for rec in summary.recommendations:
            print(f"#{rec.rank} {rec.restaurant.name}")
            print(f"   Location: {rec.restaurant.location}")
            print(f"   Rating: {rec.restaurant.rating}")
            print(f"   Cuisines: {', '.join(rec.restaurant.cuisines)}")
            print(f"   Cost for two: ₹{rec.restaurant.cost_for_two}")
            print(f"   Explanation: {rec.explanation}")
            print()
        
        if summary.overall_summary:
            print(f"Overall Summary: {summary.overall_summary}")
            
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set GROQ_API_KEY environment variable to use the LLM.")
        print("\nUsing fallback recommendations instead...")
        
        # Demonstrate fallback
        engine = RecommendationEngine(use_fallback=True)
        summary = engine.generate_recommendations(prompt, shortlist, use_fallback=True)
        
        print(f"\nFallback recommendations (rule-based):\n")
        for rec in summary.recommendations:
            print(f"#{rec.rank} {rec.restaurant.name} - Rating: {rec.restaurant.rating}")
            print(f"   {rec.explanation}\n")


if __name__ == "__main__":
    main()
