# Phase 3: Integration Layer

This module implements the Integration Layer as specified in the ARCHITECTURE.md. It filters the full restaurant dataset to a relevant shortlist and builds an LLM prompt that grounds the model in real data.

## Components

### FilterPipeline (`filters.py`)
Sequential filter pipeline that narrows restaurants based on user preferences:
- **Location filter**: Case-insensitive partial match on restaurant location
- **Cuisine filter**: Matches any of the user's preferred cuisines
- **Rating filter**: Filters by minimum rating
- **Budget filter**: Filters by budget band (low/medium/high)
- **Extras filter**: Optional filters for family_friendly, quick_service, outdoor_seating

### PromptBuilder (`prompt_builder.py`)
Builds LLM prompts with guardrails:
- System message with role and constraints
- User message with preferences and restaurant JSON data
- Guardrails: "Only recommend from the list below", "cite restaurant names exactly"
- Handles empty shortlist case gracefully

### IntegrationLayer (`integration.py`)
Orchestrator that combines filtering and prompt building:
- Applies filter pipeline to restaurants
- Caps shortlist to control token/cost (default: 20 restaurants)
- Builds LLM-ready prompt
- Provides utility methods for checking match availability

## Usage Example

```python
from models.schemas import Restaurant, UserPreferences, BudgetBand
from phase3.integration import IntegrationLayer

# Create sample restaurants
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
    # ... more restaurants
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

# Process restaurants
shortlist, prompt = integration.process(restaurants, preferences)

print(f"Shortlist size: {len(shortlist)}")
print(f"Prompt length: {len(prompt)}")
```

## Exit Criteria Met

✅ Filters return sensible subsets for test cases (Delhi + Italian + high budget)
✅ Prompt fits within model context limits (shortlist cap controls token usage)
✅ Zero restaurants → graceful message (skip LLM call)
✅ Guardrails in prompt ensure grounded recommendations
