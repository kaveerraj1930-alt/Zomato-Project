"""Response parser for parsing LLM output into structured recommendations."""

import json
import re
from typing import List, Optional

from models.schemas import Recommendation, Restaurant


class ResponseParser:
    """Parse LLM response into structured Recommendation objects."""

    def parse(self, response: str, shortlist: List[Restaurant]) -> List[Recommendation]:
        """
        Parse LLM response into recommendations.
        
        Args:
            response: Raw LLM response text
            shortlist: List of restaurants in the shortlist for reference
            
        Returns:
            List of Recommendation objects
            
        Raises:
            ValueError: If parsing fails
        """
        # Try to extract JSON from the response
        json_data = self._extract_json(response)
        
        if not json_data:
            raise ValueError("Could not extract JSON from LLM response")
        
        # Parse recommendations
        recommendations = []
        recommendations_data = json_data.get("recommendations", [])
        
        restaurant_map = {r.name: r for r in shortlist}
        
        for rec_data in recommendations_data:
            restaurant_name = rec_data.get("restaurant_name", "")
            rank = rec_data.get("rank", 0)
            explanation = rec_data.get("explanation", "")
            
            # Find the restaurant in the shortlist
            restaurant = restaurant_map.get(restaurant_name)
            
            if restaurant:
                recommendations.append(
                    Recommendation(
                        restaurant=restaurant,
                        rank=rank,
                        explanation=explanation,
                    )
                )
        
        # Sort by rank
        recommendations.sort(key=lambda r: r.rank)
        
        return recommendations

    def _extract_json(self, response: str) -> Optional[dict]:
        """
        Extract JSON from LLM response.
        
        Handles cases where JSON might be embedded in markdown code blocks
        or surrounded by other text.
        """
        # Try to find JSON in code blocks
        code_block_pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
        matches = re.findall(code_block_pattern, response, re.DOTALL)
        
        if matches:
            try:
                return json.loads(matches[0])
            except json.JSONDecodeError:
                pass
        
        # Try to parse the entire response as JSON
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON object in the text
        json_pattern = r"\{[^{}]*\"recommendations\"[^{}]*\}"
        matches = re.findall(json_pattern, response, re.DOTALL)
        
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
        
        return None

    def get_overall_summary(self, response: str) -> Optional[str]:
        """Extract overall summary from LLM response if present."""
        json_data = self._extract_json(response)
        if json_data:
            return json_data.get("overall_summary")
        return None
