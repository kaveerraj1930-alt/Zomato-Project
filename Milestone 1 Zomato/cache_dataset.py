"""Script to pre-cache the restaurant dataset as Parquet for Streamlit Cloud deployment.

This script loads the dataset from Hugging Face and saves it as a Parquet file
in the data/cache directory. This is required for Phase 7 Streamlit Cloud deployment
to avoid re-downloading the dataset on every cold start.
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from data import get_restaurants
import pandas as pd

def main():
    """Load and cache the dataset as Parquet."""
    print("Loading restaurant dataset from Hugging Face...")
    
    # Load restaurants using the existing data pipeline
    restaurants = get_restaurants()
    
    print(f"Loaded {len(restaurants)} restaurants")
    
    # Convert to DataFrame
    df = pd.DataFrame([
        {
            "id": r.id,
            "name": r.name,
            "location": r.location,
            "cuisines": r.cuisines,
            "cost_for_two": r.cost_for_two,
            "rating": r.rating,
        }
        for r in restaurants
    ])
    
    # Ensure cache directory exists
    cache_dir = os.path.join(project_root, "data", "cache")
    os.makedirs(cache_dir, exist_ok=True)
    
    # Save as Parquet
    cache_path = os.path.join(cache_dir, "restaurants.parquet")
    df.to_parquet(cache_path, index=False)
    
    print(f"Dataset cached to: {cache_path}")
    print(f"File size: {os.path.getsize(cache_path) / (1024 * 1024):.2f} MB")
    print("\nDataset is now ready for Streamlit Cloud deployment.")

if __name__ == "__main__":
    main()
