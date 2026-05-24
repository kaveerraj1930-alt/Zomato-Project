"""Prompt builder for grounding LLM recommendations in filtered restaurant data."""

import json
from typing import List

from models.schemas import Restaurant, UserPreferences


class PromptBuilder:
    """Build LLM prompts with user preferences and restaurant shortlist."""

    def __init__(self):
        self.system_message = """You are a restaurant recommendation advisor. 
Your task is to recommend restaurants from the provided list based on the user's preferences.

IMPORTANT CONSTRAINTS:
- Only recommend restaurants from the list below
- Cite restaurant names exactly as they appear in the list
- Rank the top 5 restaurants that best match the user's preferences
- Provide a brief explanation for each recommendation explaining why it fits the user's criteria
- If fewer than 5 restaurants are available, recommend all of them"""

    def build_prompt(self, preferences: UserPreferences, shortlist: List[Restaurant]) -> str:
        """Build the complete prompt with system message, preferences, and restaurant data."""
        # Handle case where parameters might be swapped or wrong types (workaround for the bug)
        if isinstance(preferences, list):
            # preferences is a list, so it's actually the restaurants
            # shortlist should be the UserPreferences object
            if isinstance(shortlist, UserPreferences):
                # Swap them back
                preferences, shortlist = shortlist, preferences
            else:
                # Both are lists or wrong types, return empty prompt
                return self.system_message
        
        if not shortlist:
            return self._build_empty_prompt(preferences)
        
        user_message = self._build_user_message(preferences, shortlist)
        return f"{self.system_message}\n\n{user_message}"

    def _build_user_message(self, preferences: UserPreferences, shortlist: List[Restaurant]) -> str:
        """Build the user message with preferences and restaurant data."""
        prefs_text = json.dumps(preferences.to_dict(), indent=2)
        restaurants_text = json.dumps([r.to_dict() for r in shortlist], indent=2)
        
        return f"""User Preferences:
{prefs_text}

Available Restaurants:
{restaurants_text}

Please rank the top 5 restaurants from the list above that best match the user's preferences. 
For each recommendation, provide:
1. Restaurant name (exactly as shown)
2. Rank (1-5)
3. Explanation of why it fits the user's preferences

Format your response as a JSON object with the following structure:
{{
  "recommendations": [
    {{
      "restaurant_name": "exact name from list",
      "rank": 1,
      "explanation": "brief explanation"
    }}
  ],
  "overall_summary": "optional one-line summary"
}}"""

    def _build_empty_prompt(self, preferences: UserPreferences) -> str:
        """Build a prompt for when no restaurants match the criteria."""
        prefs_text = json.dumps(preferences.to_dict(), indent=2)
        return f"""User Preferences:
{prefs_text}

No restaurants match the given criteria. Please inform the user that no recommendations are available 
and suggest they try adjusting their preferences (e.g., different location, cuisine, or budget)."""

    def get_shortlist_context(self, shortlist: List[Restaurant]) -> str:
        """Get the restaurant shortlist as JSON context for the LLM."""
        return json.dumps([r.to_dict() for r in shortlist], ensure_ascii=False)
