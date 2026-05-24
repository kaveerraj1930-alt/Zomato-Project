"""FastAPI application factory with lifespan and CORS configuration."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from backend.app.routers import metadata, recommendations
from backend.app.services.recommender import RecommenderService
from phase6.logging.config import configure_logging
from phase6.logging.middleware import RequestLoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context: pre-load catalog on startup."""
    # Startup: warm up the recommender service (load dataset into memory)
    recommender = RecommenderService()
    try:
        catalog = recommender.load_catalog()
        print(f"[startup] Loaded {len(catalog):,} restaurants into catalog.")
    except Exception as exc:
        print(f"[startup] Warning: could not preload catalog: {exc}")

    yield

    # Shutdown: nothing to clean up
    print("[shutdown] Backend shutting down.")


def create_app() -> FastAPI:
    """Factory function to create and configure the FastAPI application."""
    app = FastAPI(
        title="Zomato Recommendation API",
        description="AI-powered restaurant recommendation backend (Phase 5).",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS — allow frontend origin(s)
    cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in cors_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Configure structured logging
    configure_logging()

    # Include routers
    app.include_router(recommendations.router)
    app.include_router(metadata.router)

    # Add request logging middleware (latency tracking)
    app.add_middleware(RequestLoggingMiddleware)

    # Root redirect to docs
    @app.get("/", include_in_schema=False)
    async def root() -> RedirectResponse:
        return RedirectResponse(url="/docs")

    return app


app = create_app()
