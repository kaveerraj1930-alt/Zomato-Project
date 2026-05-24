# Phase 4: Recommendation Engine

This module implements the Recommendation Engine as specified in the ARCHITECTURE.md. It uses Groq LLM to rank shortlist items and generate human-readable explanations.

## Components

### GroqClient (`groq_client.py`)
Groq LLM client wrapper with retries and timeout:
- Uses OpenAI-compatible API to connect to Groq
- Configurable model (default: llama3-70b-8192)
- Exponential backoff retry mechanism
- Timeout handling

### ResponseParser (`response_parser.py`)
Parses LLM response into structured Recommendation objects:
- Extracts JSON from markdown code blocks or plain text
- Handles various JSON formatting styles
- Maps restaurant names to Restaurant objects from shortlist
- Extracts overall summary if present

### HallucinationChecker (`hallucination_check.py`)
Verifies that LLM recommendations are grounded in the shortlist:
- Checks that all recommended restaurants exist in the shortlist
- Filters out hallucinated restaurants
- Returns list of invalid names for debugging

### RecommendationEngine (`recommendation_engine.py`)
Orchestrator that combines all components:
- Generates recommendations using Groq LLM
- Parses and validates responses
- Implements fallback mechanism for failures
- Returns rule-based top-N if LLM fails

## Setup

1. Install required dependencies:
```bash
pip install openai
```

2. Set your Groq API key:
```bash
export GROQ_API_KEY=your_api_key_here
```
Or add to your `.env` file:
```
GROQ_API_KEY=your_api_key_here
```

## Usage Example

```python
from models.schemas import Restaurant, UserPreferences, BudgetBand
from phase4.recommendation_engine import RecommendationEngine

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
    # ... more restaurants
]

# Create prompt (from Phase 3)
prompt = "User wants Italian food in Bangalore with medium budget..."

# Initialize recommendation engine
engine = RecommendationEngine(
    groq_api_key="your_api_key",  # or set GROQ_API_KEY env var
    model="llama3-70b-8192",
    timeout=30,
    max_retries=3,
)

# Generate recommendations
summary = engine.generate_recommendations(prompt, shortlist)

# Access results
for rec in summary.recommendations:
    print(f"#{rec.rank} {rec.restaurant.name}")
    print(f"   Rating: {rec.restaurant.rating}")
    print(f"   Explanation: {rec.explanation}")

print(f"Summary: {summary.overall_summary}")
```

## Exit Criteria Met

✅ Top 5 recommendations with explanations for sample inputs
✅ No restaurant names outside the shortlist in output (hallucination check)
✅ API errors handled without crashing the app (retry mechanism + fallback)
✅ Fallback mechanism for parse failures (rule-based top-N)
