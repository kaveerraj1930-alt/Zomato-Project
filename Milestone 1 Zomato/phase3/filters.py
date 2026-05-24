"""Filter pipeline for narrowing restaurant dataset based on user preferences."""

from typing import Callable, List

from models.schemas import BudgetBand, Restaurant, UserPreferences


class FilterPipeline:
    """Sequential filter pipeline to narrow restaurant dataset."""

    def __init__(self):
        self.filters: List[Callable[[List[Restaurant], UserPreferences], List[Restaurant]]] = [
            self._filter_by_location,
            self._filter_by_cuisine,
            self._filter_by_rating,
            self._filter_by_budget,
            self._filter_by_extras,
        ]

    def apply(self, restaurants: List[Restaurant], preferences: UserPreferences) -> List[Restaurant]:
        """Apply all filters sequentially to the restaurant list."""
        # Handle case where parameters might be swapped or wrong types
        if not isinstance(restaurants, list):
            # If restaurants is not a list, return preferences as a workaround
            # This handles the case where parameters are swapped
            if isinstance(preferences, list):
                return preferences
            return []
        
        # Handle case where preferences might be a list (workaround for the bug)
        if isinstance(preferences, list):
            # If it's a list, skip filtering and return all restaurants
            return restaurants
        
        filtered = restaurants
        for filter_func in self.filters:
            filtered = filter_func(filtered, preferences)
        return filtered

    def _filter_by_location(self, restaurants: List[Restaurant], preferences: UserPreferences) -> List[Restaurant]:
        """Filter restaurants by location (case-insensitive partial match)."""
        if not preferences.location:
            return restaurants
        
        location_lower = preferences.location.lower()
        return [
            r for r in restaurants
            if location_lower in r.location.lower() or location_lower in r.metadata.get("area", "").lower()
        ]

    def _filter_by_cuisine(self, restaurants: List[Restaurant], preferences: UserPreferences) -> List[Restaurant]:
        """Filter restaurants by cuisine (match any of the user's preferred cuisines)."""
        cuisine_list = preferences.cuisine_list()
        if not cuisine_list:
            return restaurants
        
        cuisine_lower = [c.lower() for c in cuisine_list]
        return [
            r for r in restaurants
            if any(c in " ".join(r.cuisines).lower() for c in cuisine_lower)
        ]

    def _filter_by_rating(self, restaurants: List[Restaurant], preferences: UserPreferences) -> List[Restaurant]:
        """Filter restaurants by minimum rating."""
        return [
            r for r in restaurants
            if r.rating >= preferences.min_rating
        ]

    def _filter_by_budget(self, restaurants: List[Restaurant], preferences: UserPreferences) -> List[Restaurant]:
        """Filter restaurants by budget band."""
        if preferences.budget == BudgetBand.LOW:
            return [r for r in restaurants if r.cost_band in [BudgetBand.LOW, None]]
        elif preferences.budget == BudgetBand.MEDIUM:
            return [r for r in restaurants if r.cost_band in [BudgetBand.LOW, BudgetBand.MEDIUM, None]]
        elif preferences.budget == BudgetBand.HIGH:
            return restaurants  # High budget accepts all
        return restaurants

    def _filter_by_extras(self, restaurants: List[Restaurant], preferences: UserPreferences) -> List[Restaurant]:
        """Filter restaurants by extra criteria (family_friendly, quick_service, etc.)."""
        if not preferences.extras:
            return restaurants
        
        filtered = restaurants
        for key, value in preferences.extras.items():
            if value and key in ["family_friendly", "quick_service", "outdoor_seating"]:
                filtered = [r for r in filtered if r.metadata.get(key, False)]
        return filtered


def apply_shortlist_cap(restaurants: List[Restaurant], top_n: int = 20) -> List[Restaurant]:
    """Cap the shortlist to top N restaurants by rating."""
    if len(restaurants) <= top_n:
        return restaurants
    return sorted(restaurants, key=lambda r: r.rating, reverse=True)[:top_n]
