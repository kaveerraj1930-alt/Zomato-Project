"""Recommendation engine orchestrator: combines LLM client, parser, and hallucination check."""

from typing import List, Optional

from models.schemas import Recommendation, Restaurant, Summary
from phase4.groq_client import GroqClient
from phase4.response_parser import ResponseParser
from phase4.hallucination_check import HallucinationChecker


class RecommendationEngine:
    """Orchestrates the recommendation engine: LLM generation, parsing, and validation."""

    def __init__(
        self,
        groq_api_key: Optional[str] = None,
        model: str = "llama3-70b-8192",
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize the recommendation engine.
        
        Args:
            groq_api_key: Groq API key (defaults to GROQ_API_KEY env var)
            model: Model to use (default: llama3-70b-8192)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.groq_client = GroqClient(
            api_key=groq_api_key,
            model=model,
            timeout=timeout,
            max_retries=max_retries,
        )
        self.response_parser = ResponseParser()
        self.hallucination_checker = HallucinationChecker()

    def generate_recommendations(
        self,
        prompt: str,
        shortlist: List[Restaurant],
        use_fallback: bool = True,
    ) -> Summary:
        """
        Generate recommendations using the LLM.
        
        Args:
            prompt: LLM prompt with preferences and restaurant data
            shortlist: List of restaurants in the shortlist
            use_fallback: Whether to use rule-based fallback if LLM fails
            
        Returns:
            Summary object with recommendations and optional overall summary
        """
        if not shortlist:
            return Summary(
                recommendations=[],
                overall_summary="No restaurants available to recommend.",
            )

        try:
            # Generate completion from Groq
            print(f"  [DEBUG] Calling Groq LLM...")
            response = self.groq_client.generate_completion(prompt)
            print(f"  [DEBUG] LLM response received (length: {len(response)})")
            print(f"  [DEBUG] Response preview: {response[:200]}...")
            
            # Parse response into recommendations
            print(f"  [DEBUG] Parsing response...")
            recommendations = self.response_parser.parse(response, shortlist)
            print(f"  [DEBUG] Parsed {len(recommendations)} recommendations")
            
            # Verify no hallucinations
            is_valid, invalid_names = self.hallucination_checker.verify(
                recommendations, shortlist
            )
            
            if not is_valid:
                print(f"  [DEBUG] Found invalid restaurant names: {invalid_names}")
                # Filter out invalid recommendations
                recommendations = self.hallucination_checker.filter_valid_recommendations(
                    recommendations, shortlist
                )
                print(f"  [DEBUG] Filtered to {len(recommendations)} valid recommendations")
            
            # Get overall summary if available
            overall_summary = self.response_parser.get_overall_summary(response)
            
            # If we have valid recommendations, return them
            if recommendations:
                print(f"  [DEBUG] Returning {len(recommendations)} LLM recommendations")
                return Summary(
                    recommendations=recommendations[:5],  # Limit to top 5
                    overall_summary=overall_summary,
                )
            
            # If no valid recommendations after filtering, use fallback
            print(f"  [DEBUG] No valid recommendations, using fallback")
            if use_fallback:
                return self._generate_fallback_recommendations(shortlist)
            
            return Summary(
                recommendations=[],
                overall_summary="No valid recommendations could be generated.",
            )

        except Exception as e:
            print(f"  [DEBUG] LLM error: {str(e)}")
            # If LLM fails, use fallback
            if use_fallback:
                return self._generate_fallback_recommendations(shortlist)
            
            return Summary(
                recommendations=[],
                overall_summary=f"Error generating recommendations: {str(e)}",
            )

    def _generate_fallback_recommendations(self, shortlist: List[Restaurant]) -> Summary:
        """
        Generate rule-based fallback recommendations when LLM fails.
        
        Args:
            shortlist: List of restaurants in the shortlist
            
        Returns:
            Summary with rule-based recommendations
        """
        # Sort by rating and take top 5
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
        
        overall_summary = (
            "Recommendations generated using rule-based fallback. "
            "These are top-rated restaurants from your filtered list."
        )
        
        return Summary(
            recommendations=recommendations,
            overall_summary=overall_summary,
        )
