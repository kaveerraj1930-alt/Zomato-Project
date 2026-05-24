"""Streamlit web UI — primary user input surface (Phase 2)."""

from __future__ import annotations

import logging

import streamlit as st

from config import get_settings
from models import Recommendation
from services import run_recommendation
from ui.phase2.exceptions import PreferenceValidationError
from ui.phase2.options import get_cuisine_options, get_location_options
from ui.phase2.preferences_form import BUDGET_LABELS, build_preferences
from ui.phase2.serializer import log_preferences, preferences_to_json

logging.basicConfig(level=logging.INFO)

PAGE_TITLE = "Zomato AI Restaurant Finder"
CUSTOM_LOCATION = "Other (type below)"


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        .main-header {
            font-size: 1.75rem;
            font-weight: 700;
            color: #E23744;
            margin-bottom: 0.25rem;
        }
        .sub-header {
            color: #686b78;
            font-size: 0.95rem;
            margin-bottom: 1.5rem;
        }
        div[data-testid="stForm"] {
            border: 1px solid #e8e8e8;
            border-radius: 12px;
            padding: 1rem 1.25rem 0.5rem;
            background: #fffaf9;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_recommendation_card(rec: Recommendation) -> None:
    r = rec.restaurant
    cost = f"₹{r.cost_for_two:.0f} for two" if r.cost_for_two else "Cost N/A"
    cuisines = ", ".join(r.cuisines) if r.cuisines else "—"
    st.markdown(f"### #{rec.rank} {r.name}")
    st.markdown(f"**{cuisines}** · {r.location} · ★ {r.rating:.1f} · {cost}")
    st.info(rec.explanation)


def _render_validation_errors(messages: list[str]) -> None:
    st.error("Please fix the following:")
    for msg in messages:
        st.markdown(f"- {msg}")


def main() -> None:
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon="🍽️",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    _inject_styles()

    st.markdown('<p class="main-header">🍽️ Zomato AI Restaurant Finder</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Tell us what you want — we\'ll find the best matches for you.</p>',
        unsafe_allow_html=True,
    )

    settings = get_settings()
    locations = get_location_options()
    cuisines = get_cuisine_options()
    location_choices = locations + [CUSTOM_LOCATION]

    with st.form("preferences_form", clear_on_submit=False):
        st.subheader("Your preferences")

        col1, col2 = st.columns(2)
        with col1:
            location_pick = st.selectbox(
                "Location",
                options=location_choices,
                index=0,
                help="Localities from the Zomato dataset (run Phase 1 if the list is empty).",
            )
            custom_location = ""
            if location_pick == CUSTOM_LOCATION:
                custom_location = st.text_input(
                    "Custom location",
                    placeholder="e.g. Indiranagar",
                    max_chars=100,
                )
            budget_label = st.selectbox(
                "Budget",
                options=list(BUDGET_LABELS.keys()),
                index=1,
                help="Low, medium, or high spend for two",
            )
        with col2:
            cuisine = st.multiselect(
                "Cuisine",
                options=cuisines,
                default=[cuisines[0]] if cuisines else [],
                max_selections=5,
                help="Select up to 5 cuisines",
            )
            min_rating = st.slider(
                "Minimum rating",
                min_value=0.0,
                max_value=5.0,
                value=4.0,
                step=0.5,
            )

        st.markdown("**Additional preferences**")
        ex1, ex2 = st.columns(2)
        with ex1:
            family_friendly = st.checkbox("Family-friendly")
        with ex2:
            quick_service = st.checkbox("Quick service")

        submitted = st.form_submit_button(
            "Get recommendations",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        st.caption(
            "Locations and cuisines are loaded from your cached dataset when available. "
            "Run `python -m data` first if needed."
        )
        return

    location = custom_location.strip() if location_pick == CUSTOM_LOCATION else location_pick

    try:
        preferences = build_preferences(
            location=location,
            budget_label=budget_label,
            cuisine=cuisine,
            min_rating=min_rating,
            family_friendly=family_friendly,
            quick_service=quick_service,
        )
    except PreferenceValidationError as exc:
        _render_validation_errors(exc.messages)
        return

    log_preferences(preferences)

    with st.spinner("Finding restaurants for you…"):
        result = run_recommendation(preferences, settings=settings)

    st.success("Preferences validated")
    st.markdown("#### Your search")
    st.markdown(
        f"**{preferences.location}** · **{preferences.budget.value.title()}** budget · "
        f"**{', '.join(preferences.cuisine_list())}** · min rating **{preferences.min_rating}**"
    )
    if preferences.extras:
        extras_text = ", ".join(k.replace("_", " ").title() for k in preferences.extras)
        st.caption(f"Also: {extras_text}")

    if result.summary.recommendations:
        st.markdown("#### Top recommendations")
        for rec in result.summary.recommendations:
            _render_recommendation_card(rec)
        if result.summary.overall_summary:
            st.markdown(f"*{result.summary.overall_summary}*")
    else:
        st.markdown("#### Results")
        st.warning(result.message)
        st.caption(
            f"Shortlist size: {result.shortlist_size} · "
            f"Pipeline configured for top {settings.top_k} picks."
        )

    with st.expander("Preferences JSON (Phase 2)"):
        st.code(preferences_to_json(preferences, indent=2), language="json")

    with st.expander("Pipeline response"):
        st.json(result.to_dict())


if __name__ == "__main__":
    main()
