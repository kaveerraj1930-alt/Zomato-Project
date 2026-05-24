# Problem Statement: AI-Powered Restaurant Recommendation System

Build an AI-powered restaurant recommendation service inspired by **Zomato**. The system should combine structured restaurant data with a **Large Language Model (LLM)** to deliver personalized, human-readable suggestions based on what the user cares about.

---

## Objective

Design and implement an application that:

- Accepts user preferences (location, budget, cuisine, ratings, and more)
- Uses a real-world restaurant dataset
- Uses an LLM to produce personalized, natural-language recommendations
- Presents results in a clear, actionable format

---

## System Workflow

### 1. Data Ingestion

- Load and preprocess the Zomato dataset from Hugging Face:  
  [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)
- Extract fields needed for matching and display, such as:
  - Restaurant name
  - Location
  - Cuisine
  - Cost
  - Rating

### 2. User Input

Collect preferences from the user, including:

| Preference | Examples |
|------------|----------|
| **Location** | Delhi, Bangalore |
| **Budget** | Low, medium, high |
| **Cuisine** | Italian, Chinese |
| **Minimum rating** | e.g. 4.0+ |
| **Other** | Family-friendly, quick service, etc. |

### 3. Integration Layer

- Filter and prepare restaurant records that match the user’s criteria
- Pass the structured shortlist into an LLM prompt
- Design a prompt that helps the model **reason**, **rank**, and **explain** choices—not only list names

### 4. Recommendation Engine

Use the LLM to:

- **Rank** restaurants by fit for the user’s preferences
- **Explain** why each option is a good match
- **Optionally** summarize the overall set of recommendations

### 5. Output Display

Show the top recommendations in a user-friendly layout. For each restaurant, include:

- Restaurant name
- Cuisine
- Rating
- Estimated cost
- AI-generated explanation of why it was recommended

---

## Success Criteria

A complete solution should demonstrate an end-to-end flow: **dataset → filtering → LLM reasoning → readable recommendations**, with outputs that are both **accurate** (grounded in real data) and **useful** (clear explanations the user can act on).
