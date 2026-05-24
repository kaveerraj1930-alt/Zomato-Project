# Phase 6: Hardening & Delivery

This folder contains all Phase 6 artifacts for making the system reliable, testable, and demo-ready.

## Folder Structure

```
phase6/
├── tests/                          # Automated test suite
│   ├── test_filters.py             # Unit tests for filter pipeline
│   ├── test_hallucination_check.py # Tests for hallucination checker
│   ├── test_backend_api.py         # FastAPI endpoint tests
│   ├── test_recommendation_engine_mock.py  # Mock LLM integration tests
│   └── test_end_to_end.py          # Full pipeline E2E tests
├── logging/                        # Logging & observability
│   ├── config.py                   # Structured logging configuration
│   └── middleware.py               # FastAPI request logging middleware
├── deployment/                     # Deployment validation
│   ├── health_check.py             # Standalone health check script
│   └── validate_stack.py           # Full stack validation script
└── README.md                       # This file
```

## Running Tests

Run all Phase 6 tests (no LLM API key needed — uses mocks and fallback):

```bash
# From project root
python -m pytest phase6/tests/ -v

# Or run specific test files
python -m pytest phase6/tests/test_filters.py -v
python -m pytest phase6/tests/test_backend_api.py -v
```

Run the entire project test suite (Phase 0-6):

```bash
python -m pytest -v
```

## Logging

The backend automatically uses structured logging via `phase6/logging/`:

- **config.py**: Configures `asctime | LEVEL | logger_name | message` format.
- **middleware.py**: `RequestLoggingMiddleware` logs every request with method, path, status, and latency in ms. Also adds `X-Response-Time-Ms` response header.

Log output example:
```
2025-05-19 10:30:00 | INFO     | zomato.api | POST /api/v1/recommendations → 200 (1523.4 ms)
```

## Deployment Validation

### Health Check
```bash
python -m phase6.deployment.health_check
# Or with custom URL:
python -m phase6.deployment.health_check --url http://localhost:8000/api/v1/health
```

### Full Stack Validation
```bash
python -m phase6.deployment.validate_stack
```
This checks:
1. Backend health, locations, cuisines endpoints
2. Frontend serving HTML
3. Recommendation endpoint returning valid results

### Docker Compose
```bash
docker-compose up --build

# In another terminal, validate the stack:
python -m phase6.deployment.validate_stack
```

## Security Checklist

- All secrets in `.env` file (not committed to repo)
- `GROQ_API_KEY` read from environment, never hardcoded
- `.gitignore` excludes `.env`
- CORS configured to allow only the frontend origin

## Exit Criteria

- [x] Automated test suite for filter logic
- [x] Mock LLM integration tests
- [x] Backend API endpoint tests
- [x] End-to-end pipeline tests
- [x] Structured request/response logging with latency tracking
- [x] Health check and stack validation scripts
- [x] Secrets in env only, no keys in repo
- [x] Dataset cached to avoid re-download
- [x] Prompt size capped (shortlist_cap=20)
