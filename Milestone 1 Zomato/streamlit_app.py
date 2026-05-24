"""Streamlit app for Phase 7: Streamlit Cloud Deployment.

This app directly uses the Phase 1-4 pipeline (data/, phase3/, phase4/)
without going through the FastAPI backend layer.
"""

import os
import sys
from typing import List

import streamlit as st

# Add project root to sys.path
# Streamlit Cloud runs from git root, but our project is in a subdirectory
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(current_file)

# Add both project root and parent directory to sys.path
if project_root not in sys.path:
    sys.path.insert(0, project_root)
parent_dir = os.path.dirname(project_root)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

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
    # Debug: check if restaurant is a Restaurant object
    if not hasattr(restaurant, 'location'):
        st.error(f"Error: restaurant object is not a Restaurant object. Type: {type(restaurant)}")
        st.error(f"Restaurant data: {restaurant}")
        return
    
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
    
    # Load restaurant data to get options
    with st.spinner("Loading restaurant data..."):
        try:
            restaurants = get_restaurants()
            # Get unique locations and cuisines
            locations = sorted(list(set(r.location for r in restaurants)))
            all_cuisines = sorted(list(set(cuisine for r in restaurants for cuisine in r.cuisines)))
        except Exception as e:
            st.error(f"Error loading restaurant data: {str(e)}")
            return
    
    # Create tabs for main interface
    tab1, tab2 = st.tabs(["🔍 Find Restaurants", "ℹ️ About"])
    
    with tab1:
        # Preferences form in center
        st.markdown("### Your Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Location dropdown
            location = st.selectbox(
                "Location",
                options=locations,
                index=0,
                help="Select the area or locality in Bangalore"
            )
            
            # Budget manual input
            budget_amount = st.number_input(
                "Budget (₹ for two)",
                min_value=0,
                max_value=10000,
                value=1000,
                step=100,
                help="Enter your budget for two people"
            )
            
            # Determine budget band based on amount
            if budget_amount <= 500:
                budget = BudgetBand.LOW
            elif budget_amount <= 1500:
                budget = BudgetBand.MEDIUM
            else:
                budget = BudgetBand.HIGH
        
        with col2:
            # Cuisine dropdown (multi-select)
            selected_cuisines = st.multiselect(
                "Cuisine",
                options=all_cuisines,
                default=[],
                max_selections=5,
                help="Select up to 5 cuisines (leave empty for any)"
            )
            
            # Minimum rating
            min_rating = st.slider(
                "Minimum Rating",
                min_value=0.0,
                max_value=5.0,
                value=4.0,
                step=0.1,
                help="Minimum restaurant rating"
            )
        
        # Submit button
        submitted = st.button("Get Recommendations", type="primary", use_container_width=True)
        
        if not submitted:
            st.info("👆 Select your preferences and click 'Get Recommendations' to find restaurants.")
            return
        
        # Create user preferences
        st.write(f"DEBUG: Creating UserPreferences with:")
        st.write(f"  location: {location} (type: {type(location)})")
        st.write(f"  budget: {budget} (type: {type(budget)})")
        st.write(f"  selected_cuisines: {selected_cuisines} (type: {type(selected_cuisines)})")
        st.write(f"  min_rating: {min_rating} (type: {type(min_rating)})")
        
        preferences = UserPreferences(
            location=location,
            budget=budget,
            cuisine=selected_cuisines,
            min_rating=min_rating,
            extras={}
        )
        
        # Debug: check preferences type
        st.write(f"DEBUG: Preferences type: {type(preferences)}")
        st.write(f"DEBUG: Preferences: {preferences}")
        
        # Show search summary
        st.markdown("---")
        st.markdown("### Your Search")
        st.markdown(f"""
        **Location:** {preferences.location} · 
        **Budget:** {preferences.budget.value} · 
        **Cuisine:** {', '.join(preferences.cuisine) if preferences.cuisine else 'Any'} · 
        **Min Rating:** {preferences.min_rating}
        """)
        
        # Generate recommendations
        with st.spinner("Generating recommendations..."):
            try:
                # Apply integration layer (Phase 3)
                st.write(f"DEBUG: Before integration.process - preferences type: {type(preferences)}")
                integration = IntegrationLayer()
                shortlist, prompt = integration.process(preferences, restaurants)
                st.write(f"DEBUG: After integration.process - shortlist type: {type(shortlist)}")
                
                st.write(f"DEBUG: Shortlist type: {type(shortlist)}, length: {len(shortlist)}")
                if shortlist:
                    st.write(f"DEBUG: First shortlist item type: {type(shortlist[0])}")
                    st.write(f"DEBUG: First shortlist item: {shortlist[0]}")
                
                # Generate recommendations using LLM (Phase 4)
                groq_api_key = os.getenv("GROQ_API_KEY")
                if not groq_api_key:
                    st.warning("⚠️ GROQ_API_KEY not found. Using rule-based recommendations instead.")
                    st.caption("To use AI recommendations, add GROQ_API_KEY to Streamlit Cloud secrets.")
                
                engine = RecommendationEngine(
                    groq_api_key=groq_api_key,
                    model="llama-3.3-70b-versatile",
                    timeout=30,
                    max_retries=3,
                )
                
                summary = engine.generate_recommendations(prompt, shortlist)
                
                st.write(f"DEBUG: Summary type: {type(summary)}")
                st.write(f"DEBUG: Summary has recommendations: {hasattr(summary, 'recommendations')}")
                if hasattr(summary, 'recommendations'):
                    st.write(f"DEBUG: Recommendations type: {type(summary.recommendations)}")
                    if summary.recommendations:
                        st.write(f"DEBUG: First recommendation type: {type(summary.recommendations[0])}")
                        st.write(f"DEBUG: First recommendation: {summary.recommendations[0]}")
                
                # Display results
                st.markdown("---")
                st.markdown("### Top Recommendations")
                
                if summary.recommendations:
                    for rec in summary.recommendations:
                        # Type checking to ensure we have the right data structure
                        if not hasattr(rec, 'restaurant'):
                            st.error(f"Error: Recommendation object missing 'restaurant' attribute. Type: {type(rec)}")
                            st.error(f"Recommendation data: {rec}")
                            continue
                        if not hasattr(rec.restaurant, 'location'):
                            st.error(f"Error: Restaurant object missing 'location' attribute. Type: {type(rec.restaurant)}")
                            st.error(f"Restaurant data: {rec.restaurant}")
                            continue
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
                st.error(f"Error type: {type(e).__name__}")
                import traceback
                st.error(f"Traceback: {traceback.format_exc()}")
                st.caption("Please try again or check your preferences.")
    
    with tab2:
        # Additional information tab
        st.markdown("### About This App")
        st.info(
            """
            This app uses AI to recommend restaurants based on your preferences. 
            It filters the dataset and uses an LLM to rank and explain the recommendations.
            
            **How it works:**
            1. You select your preferences (location, budget, cuisine, rating)
            2. The app filters the restaurant dataset based on your criteria
            3. An AI model (LLM) ranks the matching restaurants and provides explanations
            4. You get personalized recommendations with AI-generated insights
            
            **Features:**
            - AI-powered restaurant recommendations
            - Personalized explanations for each recommendation
            - Filter by location, budget, cuisine, and rating
            - Dataset of 24,000+ restaurants in Bangalore
            """
        )
        
        st.markdown("---")
        st.markdown("### Dataset Information")
        st.success(
            f"""
            **Total Restaurants:** {len(restaurants):,}
            
            **Available Locations:** {len(locations)}
            
            **Available Cuisines:** {len(all_cuisines)}
            
            **Data Source:** Hugging Face - ManikaSaini/zomato-restaurant-recommendation
            """
        )
        
        st.markdown("---")
        st.markdown("### Technology Stack")
        st.markdown("""
        - **Frontend:** Streamlit
        - **AI/LLM:** Groq (Llama 3.3 70B)
        - **Data Processing:** Pandas, PyArrow
        - **Dataset:** Hugging Face Datasets
        """)


if __name__ == "__main__":
    main()
