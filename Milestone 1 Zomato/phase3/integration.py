"""Integration layer orchestrator: combines filtering and prompt building."""

from typing import List, Tuple

from models.schemas import Restaurant, UserPreferences
from phase3.filters import FilterPipeline, apply_shortlist_cap
from phase3.prompt_builder import PromptBuilder


class IntegrationLayer:
    """Orchestrates the integration layer: filtering and prompt building."""

    def __init__(self, shortlist_cap: int = 20):
        self.filter_pipeline = FilterPipeline()
        self.prompt_builder = PromptBuilder()
        self.shortlist_cap = shortlist_cap

    def process(
        self, 
        restaurants: List[Restaurant], 
        preferences: UserPreferences
    ) -> Tuple[List[Restaurant], str]:
        """
        Process restaurants through the integration layer.
        
        Args:
            restaurants: Full list of restaurants from the dataset
            preferences: Validated user preferences
            
        Returns:
            Tuple of (shortlist, prompt) where:
            - shortlist: Filtered and capped list of restaurants
            - prompt: LLM-ready prompt with preferences and restaurant data
        """
        # Handle parameter swapping at the entry point (workaround for the bug)
        if isinstance(restaurants, UserPreferences) and isinstance(preferences, list):
            # Parameters are swapped - swap them back
            restaurants, preferences = preferences, restaurants
        
        # Apply filter pipeline
        filtered = self.filter_pipeline.apply(restaurants, preferences)
        
        # Apply shortlist cap
        shortlist = apply_shortlist_cap(filtered, self.shortlist_cap)
        
        # Build prompt
        prompt = self.prompt_builder.build_prompt(preferences, shortlist)
        
        return shortlist, prompt

    def get_shortlist_size(self, restaurants: List[Restaurant], preferences: UserPreferences) -> int:
        """Get the size of the shortlist without building the prompt."""
        filtered = self.filter_pipeline.apply(restaurants, preferences)
        return len(filtered)

    def has_matches(self, restaurants: List[Restaurant], preferences: UserPreferences) -> bool:
        """Check if there are any matching restaurants."""
        return self.get_shortlist_size(restaurants, preferences) > 0
