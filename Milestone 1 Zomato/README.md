# AI-Powered Restaurant Recommendation System (Zomato)

Milestone project: structured Zomato data + LLM for personalized restaurant recommendations.

See [Problemstatement.md](./Problemstatement.md), [ARCHITECTURE.md](./ARCHITECTURE.md), and [EDGE_CASES.md](./EDGE_CASES.md).

## Phase 0 — Foundation

- Project layout, config, shared schemas, Streamlit web UI, pipeline entry point

## Phase 1 — Data ingestion

Implemented in **`data/`** — see `python -m data`.

## Phase 2 — User input

Implemented in **`ui/phase2/`**:

| Module | Role |
|--------|------|
| `ui/phase2/validator.py` | Required fields, budget enum, rating range |
| `ui/phase2/preferences_form.py` | Form/CLI → `UserPreferences` |
| `ui/phase2/streamlit_app.py` | Web form (primary input) |
| `ui/phase2/cli.py` | CLI (`python -m ui --cli`) |

### Phase 1 modules (`data/phase1/`)

| Module | Role |
|--------|------|
| `data/phase1/loader.py` | Download from Hugging Face |
| `data/phase1/preprocess.py` | Clean, normalize, validate |
| `data/phase1/repository.py` | `load_restaurants()` / `get_restaurants()` |
| `data/cache/` | Parquet cache (`restaurants.parquet`) |

## Setup

```bash
cd "Milestone 1 Zomato"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` when you enable the LLM in later phases (`OPENAI_API_KEY`).

## Run

**Load dataset (first run downloads ~575 MB from Hugging Face):**

```bash
python -m data
python -m data --refresh
python -m data --city Delhi --min-rating 4.5
```

**Web UI (recommended):**

```bash
python -m ui
```

**CLI preferences (Phase 2):**

```bash
python -m ui --cli
python -m ui --cli --json --location Btm --budget Medium --cuisine Italian
```

Or:

```bash
streamlit run ui/phase2/streamlit_app.py
```

**CLI smoke test:**

```bash
python -m app
```

## Test

```bash
pip install pytest
pytest tests/ -v
```

## Project structure

```text
app/                 # Application entry (python -m app)
config/              # Settings loader (.env)
models/              # Shared dataclasses / enums
services/            # Pipeline orchestration
data/
  phase1/            # Phase 1: ingestion, preprocess, query
  cache/             # Processed parquet cache
ui/
  phase0/            # Phase 0: web shell entry
  phase2/            # Phase 2: validation, Streamlit, CLI
filters/             # Phase 3 (upcoming)
llm/                 # Phase 3–4 (upcoming)
tests/
  phase0/            # Foundation tests
  phase1/            # Data ingestion tests
  phase2/            # User input tests
```

Public imports stay stable: `from data import get_restaurants`, `from ui import build_preferences`.
