"""Streamlit app for Phase 7: Streamlit Cloud Deployment.

This app directly uses the Phase 1-4 pipeline (data/, phase3/, phase4/)
without going through the FastAPI backend layer.
"""

import os
import sys
from typing import List

import streamlit as st

# Add project root to path for imports
# On Streamlit Cloud, the directory structure may vary
# We'll add multiple potential paths to ensure modules can be found
current_file = os.path.abspath(__file__)
# Go up 2 directories to get to project root (Milestone 1 Zomato/)
project_root = os.path.dirname(os.path.dirname(current_file))
# Go up 3 directories to get to git root
git_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))

# Add both paths to sys.path
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if git_root not in sys.path:
    sys.path.insert(0, git_root)

from data import get_restaurants
from models.schemas import BudgetBand, Restaurant, UserPreferences
from phase3.integration import IntegrationLayer
from phase4.recommendation_engine import RecommendationEngine

# Page configuration
st.set_page_config(
    page_title="Zomato AI Restaurant Finder",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: 700;
    color: #E23744;
    margin-bottom: 0.5rem;
}
.sub-header {
    color: #686b78;
    font-size: 1.1rem;
    margin-bottom: 2rem;
}
.recommendation-card {
    border: 1px solid #e8e8e8;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    background: #fff;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.rank-badge {
    display: inline-block;
    background: #E23744;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.875rem;
    margin-right: 0.5rem;
}
</style>
""", unsafe_allow_html=True)


def render_recommendation_card(rank: int, restaurant: Restaurant, explanation: str) -> None:
    """Render a single recommendation card."""
    cost = f"₹{restaurant.cost_for_two:.0f} for two" if restaurant.cost_for_two else "Cost N/A"
    cuisines = ", ".join(restaurant.cuisines) if restaurant.cuisines else "—"
    
    st.markdown(f"""
    <div class="recommendation-card">
        <span class="rank-badge">#{rank}</span>
        <span style="font-size: 1.25rem; font-weight: 600;">{restaurant.name}</span>
        <br><br>
        <strong>Cuisines:</strong> {cuisines}<br>
        <strong>Location:</strong> {restaurant.location}<br>
        <strong>Rating:</strong> ★ {restaurant.rating:.1f}<br>
        <strong>Cost:</strong> {cost}
        <br><br>
        <em>{explanation}</em>
    </div>
    """, unsafe_allow_html=True)


def main() -> None:
    """Main Streamlit app."""
    # Header
    st.markdown('<p class="main-header">🍽️ Zomato AI Restaurant Finder</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Tell us what you want — we\'ll find the best matches for you using AI.</p>',
        unsafe_allow_html=True,
    )
    
    # Sidebar for preferences
    with st.sidebar:
        st.header("Your Preferences")
        
        # Location input
        location = st.text_input(
            "Location",
            placeholder="e.g., Bellandur, Indiranagar",
            help="Enter the area or locality in Bangalore"
        )
        
        # Budget selection
        budget_option = st.selectbox(
            "Budget",
            options=["Low", "Medium", "High"],
            index=1,
            help="Select your budget range"
        )
        budget_map = {"Low": BudgetBand.LOW, "Medium": BudgetBand.MEDIUM, "High": BudgetBand.HIGH}
        budget = budget_map[budget_option]
        
        # Cuisine input
        cuisine_input = st.text_input(
            "Cuisine (optional)",
            placeholder="e.g., Italian, North Indian",
            help="Enter cuisine type (leave empty for any)"
        )
        cuisines = [c.strip() for c in cuisine_input.split(",")] if cuisine_input else []
        
        # Minimum rating
        min_rating = st.slider(
            "Minimum Rating",
            min_value=0.0,
            max_value=5.0,
            value=4.0,
            step=0.1,
            help="Minimum restaurant rating"
        )
        
        st.markdown("---")
        st.subheader("About")
        st.info(
            "This app uses AI to recommend restaurants based on your preferences. "
            "It filters the dataset and uses an LLM to rank and explain the recommendations."
        )
    
    # Main content area
    if not location:
        st.warning("Please enter a location in the sidebar to get started.")
        return
    
    # Create user preferences
    preferences = UserPreferences(
        location=location,
        budget=budget,
        cuisine=cuisines,
        min_rating=min_rating,
        extras={}
    )
    
    # Show search summary
    st.markdown("### Your Search")
    st.markdown(f"""
    **Location:** {preferences.location} · 
    **Budget:** {preferences.budget.value} · 
    **Cuisine:** {', '.join(preferences.cuisine) if preferences.cuisine else 'Any'} · 
    **Min Rating:** {preferences.min_rating}
    """)
    
    # Generate recommendations
    with st.spinner("Loading restaurant data and generating recommendations..."):
        try:
            # Load restaurant data
            restaurants = get_restaurants()
            
            # Apply integration layer (Phase 3)
            integration = IntegrationLayer()
            shortlist, prompt = integration.generate_prompt(preferences, restaurants)
            
            # Generate recommendations using LLM (Phase 4)
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                st.warning("⚠️ GROQ_API_KEY not found. Using rule-based recommendations instead.")
                st.caption("To use AI recommendations, add GROQ_API_KEY to Streamlit Cloud secrets.")
            
            engine = RecommendationEngine(
                model="llama-3.3-70b-versatile",
                timeout=30,
                max_retries=3,
            )
            
            summary = engine.generate_recommendations(prompt, shortlist)
            
            # Display results
            st.markdown("---")
            st.markdown("### Top Recommendations")
            
            if summary.recommendations:
                for rec in summary.recommendations:
                    render_recommendation_card(rec.rank, rec.restaurant, rec.explanation)
                
                if summary.overall_summary:
                    st.markdown("---")
                    st.markdown(f"**Summary:** {summary.overall_summary}")
            else:
                st.warning("No recommendations found. Try adjusting your preferences.")
                st.caption(f"Shortlist size: {len(shortlist)} restaurants matched your criteria.")
            
            # Show shortlist info
            with st.expander("View Shortlist Details"):
                st.markdown(f"**Shortlist size:** {len(shortlist)} restaurants")
                st.mark("**Top 10 restaurants in shortlist:**")
                for i, r in enumerate(shortlist[:10], 1):
                    st.markdown(f"{i}. {r.name} - Rating: {r.rating:.1f} - {', '.join(r.cuisines[:3])}")
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.caption("Please try again or check your preferences.")


if __name__ == "__main__":
    main()
