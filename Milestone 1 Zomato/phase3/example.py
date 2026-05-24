"""Example usage of Phase 3 Integration Layer."""

from models.schemas import Restaurant, UserPreferences, BudgetBand
from phase3.integration import IntegrationLayer


def main():
    """Demonstrate Phase 3 integration layer usage."""
    
    # Create sample restaurant data
    restaurants = [
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
    
    # Create user preferences
    preferences = UserPreferences(
        location="Bangalore",
        budget=BudgetBand.MEDIUM,
        cuisine="Italian",
        min_rating=4.0
    )
    
    # Initialize integration layer
    integration = IntegrationLayer(shortlist_cap=20)
    
    # Check if there are matches
    if integration.has_matches(restaurants, preferences):
        print(f"Found {integration.get_shortlist_size(restaurants, preferences)} matching restaurants")
        
        # Process restaurants
        shortlist, prompt = integration.process(restaurants, preferences)
        
        print(f"\nShortlist size: {len(shortlist)}")
        print("\nShortlisted restaurants:")
        for r in shortlist:
            print(f"  - {r.name} ({r.location}) | Rating: {r.rating} | Cuisines: {', '.join(r.cuisines)}")
        
        print(f"\nPrompt length: {len(prompt)} characters")
        print("\n--- Prompt Preview (first 500 chars) ---")
        print(prompt[:500] + "...")
    else:
        print("No restaurants match the given preferences.")


if __name__ == "__main__":
    main()
