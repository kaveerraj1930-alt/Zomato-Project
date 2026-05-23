# Phase 7: Streamlit Cloud Deployment

This document describes the implementation of Phase 7 - Streamlit Cloud Deployment for the AI-Powered Restaurant Recommendation System.

## Overview

Phase 7 packages the full recommendation pipeline (Phases 1-4) as a single-file Streamlit app and deploys it publicly on Streamlit Community Cloud. This provides a zero-infrastructure, shareable URL for the application.

## Architecture

The Streamlit app directly uses the existing Phase 1-4 pipeline without going through the FastAPI backend layer:

```
Streamlit App (streamlit_app_phase7.py)
    ↓
Phase 1: Data Loading (data/)
    ↓
Phase 3: Integration Layer (phase3/)
    ↓
Phase 4: Recommendation Engine (phase4/)
    ↓
Results Display
```

## Files Created

1. **`ui/phase2/streamlit_app_phase7.py`** - Main Streamlit application
   - Directly imports from `data/`, `phase3/`, `phase4/`
   - Sidebar for user preferences (location, budget, cuisine, rating)
   - Results display with recommendation cards
   - Fallback mode when GROQ_API_KEY is not available

2. **`requirements_streamlit.txt`** - Python dependencies for Streamlit Cloud
   - streamlit>=1.28.0
   - pandas>=2.0.0
   - pyarrow>=12.0.0
   - datasets>=2.14.0
   - openai>=1.0.0
   - groq>=0.4.0
   - python-dotenv>=1.0.0

3. **`.streamlit/config.toml`** - Streamlit configuration
   - Custom theme with Zomato-like colors
   - Server settings for production deployment

4. **`cache_dataset.py`** - Script to pre-cache dataset as Parquet
   - Loads dataset from Hugging Face
   - Saves as `data/cache/restaurants.parquet`
   - Reduces cold start time on Streamlit Cloud

5. **`data/cache/restaurants.parquet`** - Pre-cached dataset (0.66 MB)
   - Committed to repository for fast cold starts
   - Avoids re-downloading from Hugging Face

## Local Testing

### Prerequisites

1. Install dependencies:
```bash
pip install -r requirements_streamlit.txt
```

2. Ensure GROQ_API_KEY is set in `.env`:
```env
GROQ_API_KEY=your_groq_key_here
```

### Run Locally

```bash
streamlit run ui/phase2/streamlit_app_phase7.py
```

The app will be available at `http://localhost:8501`

## Deployment to Streamlit Cloud

### Step 1: Push to GitHub

Ensure the following files are committed to your GitHub repository:
- `ui/phase2/streamlit_app_phase7.py`
- `requirements_streamlit.txt`
- `.streamlit/config.toml`
- `data/cache/restaurants.parquet`
- All pipeline code (`data/`, `phase3/`, `phase4/`, `models/`)

### Step 2: Connect to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub repository
4. Set the entry file to: `ui/phase2/streamlit_app_phase7.py`

### Step 3: Add Secrets

In the Streamlit Cloud dashboard:
1. Go to your app → Settings → Secrets
2. Add the following secret:
   ```
   GROQ_API_KEY = "your_groq_key_here"
   ```

### Step 4: Deploy

Click "Deploy" and Streamlit Cloud will:
- Install dependencies from `requirements_streamlit.txt`
- Launch the app
- Make it publicly accessible at `https://<app-name>.streamlit.app`

## Features

### User Interface

- **Sidebar Preferences Form**
  - Location text input
  - Budget selection (Low/Medium/High)
  - Cuisine input (optional)
  - Minimum rating slider (0.0-5.0)

- **Results Display**
  - Top 5 recommendation cards
  - Restaurant name, location, rating, cuisines, cost
  - AI-generated explanations
  - Overall summary

- **Additional Features**
  - Loading spinner during recommendation generation
  - Error handling with user-friendly messages
  - Fallback mode when GROQ_API_KEY is missing
  - Expandable section to view shortlist details

### Fallback Mode

If `GROQ_API_KEY` is not set or the LLM call fails, the app automatically falls back to rule-based recommendations:
- Sorts shortlist by rating
- Returns top 5 restaurants
- Uses template explanations

## Environment Configuration

| Variable | Where Set | Notes |
|----------|-----------|-------|
| `GROQ_API_KEY` | Streamlit Cloud Secrets | Never commit to repo |
| Dataset cache | `data/cache/restaurants.parquet` | Committed for fast cold starts |

## Exit Criteria

- ✅ App loads in browser via public Streamlit Cloud URL
- ✅ Preference form accepts location, budget, cuisine, min rating
- ✅ Recommendations display with restaurant name, rating, cuisines, cost, and LLM explanation
- ✅ Fallback to rule-based top-5 if GROQ_API_KEY is absent or LLM call fails
- ✅ No secrets hardcoded anywhere in the repo
- ✅ Cold start completes within 60 seconds (dataset loaded from Parquet cache)

## Troubleshooting

### App won't load on Streamlit Cloud

1. Check the deployment logs in Streamlit Cloud dashboard
2. Ensure all dependencies are in `requirements_streamlit.txt`
3. Verify the entry file path is correct: `ui/phase2/streamlit_app_phase7.py`
4. Check that `data/cache/restaurants.parquet` is committed

### GROQ_API_KEY not working

1. Ensure the secret is added in Streamlit Cloud dashboard
2. Secret name must be exactly: `GROQ_API_KEY`
3. Restart the app after adding secrets

### Import errors

1. Ensure all pipeline code is committed to GitHub
2. Check that the project structure matches local setup
3. Verify `sys.path` configuration in `streamlit_app_phase7.py`

## Performance Optimization

- Dataset cached as Parquet (0.66 MB) for fast loading
- Shortlist capped at 20 restaurants to control LLM token usage
- LLM timeout set to 30 seconds
- Lazy loading of restaurant data on first request

## Security

- All secrets stored in Streamlit Cloud Secrets manager
- No API keys hardcoded in repository
- `.gitignore` excludes `.env` file
- CORS not needed for Streamlit deployment

## Future Enhancements

- Add user authentication
- Save user preferences
- Recommendation history
- Shareable preference URLs
- Dark mode toggle
- Mobile app (PWA)
