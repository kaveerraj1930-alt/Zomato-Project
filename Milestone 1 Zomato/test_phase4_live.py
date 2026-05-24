"""Live test of Phase 4 recommendation engine with actual data."""

import os
import sys
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Load environment variables from .env file
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

# Manual fallback: read .env file directly if dotenv doesn't work
if not os.getenv('GROQ_API_KEY') and os.path.exists(env_path):
    print(f"DEBUG: Attempting manual read of {env_path}")
    try:
        with open(env_path, 'r') as f:
            content = f.read()
            print(f"DEBUG: File content: {repr(content)}")
            for line in content.split('\n'):
                line = line.strip()
                print(f"DEBUG: Processing line: {repr(line)}")
                if line.startswith('GROQ_API_KEY='):
                    key = line.split('=', 1)[1].strip()
                    os.environ['GROQ_API_KEY'] = key
                    print(f"DEBUG: Manually set GROQ_API_KEY from file")
                    break
    except Exception as e:
        print(f"DEBUG: Error reading file: {e}")

# Debug: Check if GROQ_API_KEY is loaded
print(f"DEBUG: GROQ_API_KEY loaded: {'Yes' if os.getenv('GROQ_API_KEY') else 'No'}")
print(f"DEBUG: GROQ_API_KEY length: {len(os.getenv('GROQ_API_KEY', ''))}")
print(f"DEBUG: .env path: {env_path}")
print(f"DEBUG: .env exists: {os.path.exists(env_path)}")
print()

from data import get_restaurants
from models.schemas import UserPreferences, BudgetBand
from phase3.integration import IntegrationLayer
from phase4.recommendation_engine import RecommendationEngine


def main():
    """Test Phase 4 with live data: Bellandur, budget 2000, rating 4.0."""
    
    # Allow passing API key as parameter for testing
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--api-key', help='Groq API key (overrides .env)')
    args = parser.parse_args()
    
    if args.api_key:
        os.environ['GROQ_API_KEY'] = args.api_key
        print("Using API key from command line argument")
    
    print("=" * 60)
    print("Phase 4 Live Test - Restaurant Recommendation")
    print("=" * 60)
    
    # Test parameters
    location = "Bellandur"
    budget_amount = 2000
    min_rating = 4.0
    
    # Map budget amount to budget band
    # Based on typical Zomato pricing:
    # Low: < 500
    # Medium: 500 - 1500
    # High: > 1500
    if budget_amount < 500:
        budget_band = BudgetBand.LOW
    elif budget_amount < 1500:
        budget_band = BudgetBand.MEDIUM
    else:
        budget_band = BudgetBand.HIGH
    
    print(f"\nInput Parameters:")
    print(f"  Location: {location}")
    print(f"  Budget: {budget_amount} INR ({budget_band.value})")
    print(f"  Minimum Rating: {min_rating}")
    print()
    
    # Step 1: Load restaurant data (Phase 1)
    print("Step 1: Loading restaurant data...")
    try:
        restaurants = get_restaurants()
        print(f"  Loaded {len(restaurants)} restaurants from dataset")
    except Exception as e:
        print(f"  Error loading data: {e}")
        print("  Make sure you have internet connection and dependencies installed")
        return
    
    # Step 2: Create user preferences
    print("\nStep 2: Creating user preferences...")
    preferences = UserPreferences(
        location=location,
        budget=budget_band,
        cuisine="",  # Empty to get all cuisines
        min_rating=min_rating,
    )
    print(f"  Preferences: {preferences.to_dict()}")
    
    # Step 3: Apply integration layer (Phase 3)
    print("\nStep 3: Applying integration layer (filtering + prompt building)...")
    integration = IntegrationLayer(shortlist_cap=20)
    
    shortlist, prompt = integration.process(restaurants, preferences)
    print(f"  Shortlist size: {len(shortlist)} restaurants")
    print(f"  Prompt length: {len(prompt)} characters")
    
    if not shortlist:
        print("\n  No restaurants match the criteria. Exiting.")
        return
    
    print("\n  Shortlisted restaurants (top 10):")
    for i, r in enumerate(shortlist[:10], 1):
        print(f"    {i}. {r.name} | {r.location} | Rating: {r.rating} | Cuisines: {', '.join(r.cuisines[:3])}")
    
    # Step 4: Generate recommendations using Groq LLM (Phase 4)
    print("\nStep 4: Generating recommendations...")
    
    # Check if GROQ_API_KEY is set
    if not os.getenv("GROQ_API_KEY"):
        print("  WARNING: GROQ_API_KEY environment variable not set")
        print("  Using fallback (rule-based) recommendations instead")
        print("  To use Groq LLM, set: export GROQ_API_KEY=your_api_key")
        print()
        
        # Simple fallback: sort by rating and take top 5
        from models.schemas import Recommendation, Summary
        
        sorted_restaurants = sorted(shortlist, key=lambda r: r.rating, reverse=True)[:5]
        recommendations = []
        for rank, restaurant in enumerate(sorted_restaurants, start=1):
            explanation = (
                f"Recommended based on rating of {restaurant.rating} and "
                f"cuisines: {', '.join(restaurant.cuisines)}."
            )
            recommendations.append(
                Recommendation(
                    restaurant=restaurant,
                    rank=rank,
                    explanation=explanation,
                )
            )
        
        summary = Summary(
            recommendations=recommendations,
            overall_summary="Recommendations generated using rule-based fallback. These are top-rated restaurants from your filtered list.",
        )
        print(f"  Generated {len(summary.recommendations)} recommendations (fallback)")
    else:
        try:
            print(f"  Using Groq LLM with model: llama-3.3-70b-versatile")
            engine = RecommendationEngine(
                model="llama-3.3-70b-versatile",
                timeout=30,
                max_retries=3,
            )
            
            summary = engine.generate_recommendations(prompt, shortlist)
            
            print(f"  Generated {len(summary.recommendations)} recommendations")
            
        except Exception as e:
            print(f"  Error with Groq LLM: {e}")
            print("  Using fallback recommendations...")
            
            # Simple fallback
            from models.schemas import Recommendation, Summary
            
            sorted_restaurants = sorted(shortlist, key=lambda r: r.rating, reverse=True)[:5]
            recommendations = []
            for rank, restaurant in enumerate(sorted_restaurants, start=1):
                explanation = (
                    f"Recommended based on rating of {restaurant.rating} and "
                    f"cuisines: {', '.join(restaurant.cuisines)}."
                )
                recommendations.append(
                    Recommendation(
                        restaurant=restaurant,
                        rank=rank,
                        explanation=explanation,
                    )
                )
            
            summary = Summary(
                recommendations=recommendations,
                overall_summary="Recommendations generated using rule-based fallback after LLM error.",
            )
    
    # Step 5: Display results
    print("\n" + "=" * 60)
    print("RECOMMENDATION RESULTS")
    print("=" * 60)
    
    for rec in summary.recommendations:
        print(f"\n#{rec.rank} {rec.restaurant.name}")
        print(f"  Location: {rec.restaurant.location}")
        print(f"  Rating: {rec.restaurant.rating}")
        print(f"  Cuisines: {', '.join(rec.restaurant.cuisines)}")
        print(f"  Cost for two: {rec.restaurant.cost_for_two} INR")
        print(f"  Explanation: {rec.explanation}")
    
    if summary.overall_summary:
        print(f"\nOverall Summary: {summary.overall_summary}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
