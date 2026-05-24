"""Hallucination checker to verify LLM recommendations are grounded in the shortlist."""

from typing import List

from models.schemas import Restaurant


class HallucinationChecker:
    """Verify that LLM recommendations only contain restaurants from the shortlist."""

    def verify(
        self,
        recommendations: List,
        shortlist: List[Restaurant],
    ) -> tuple[bool, List[str]]:
        """
        Verify that all recommended restaurants exist in the shortlist.
        
        Args:
            recommendations: List of Recommendation objects
            shortlist: List of restaurants in the shortlist
            
        Returns:
            Tuple of (is_valid, list_of_invalid_names)
        """
        shortlist_names = {r.name.lower() for r in shortlist}
        invalid_names = []
        
        for rec in recommendations:
            restaurant_name = rec.restaurant.name.lower()
            if restaurant_name not in shortlist_names:
                invalid_names.append(rec.restaurant.name)
        
        is_valid = len(invalid_names) == 0
        return is_valid, invalid_names

    def filter_valid_recommendations(
        self,
        recommendations: List,
        shortlist: List[Restaurant],
    ) -> List:
        """
        Filter out recommendations that are not in the shortlist.
        
        Args:
            recommendations: List of Recommendation objects
            shortlist: List of restaurants in the shortlist
            
        Returns:
            List of valid recommendations only
        """
        shortlist_names = {r.name.lower() for r in shortlist}
        valid_recommendations = []
        
        for rec in recommendations:
            restaurant_name = rec.restaurant.name.lower()
            if restaurant_name in shortlist_names:
                valid_recommendations.append(rec)
        
        return valid_recommendations
