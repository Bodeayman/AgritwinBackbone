"""VLM Classifier sub-service: Gemini-based leaf disease classification.

Run locally:
    cd vlm-classifier
    uvicorn app.main:app --reload --port 8002

Run from repo root via compose (builds ./vlm-classifier/Dockerfile).

Env:
    GEMINI_API_KEY — Gemini API key (required for /predict)
    GEMINI_MODEL   — model name (default: gemini-3.6-flash)
    KB_JSON_PATH   — path to knowledge base JSON (default: ./knowledge_base.json)
"""

from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app.config import settings
from app.routes import router

# Ensure the vlm-classifier root is on sys.path so that
# ``import disease_classification_agent`` works when running
# with ``uvicorn app.main:app`` from the vlm-classifier directory.
_SERVICE_DIR = Path(__file__).resolve().parent.parent
if str(_SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(_SERVICE_DIR))

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle hook."""
    # Validate that knowledge base is loadable.
    try:
        from disease_classification_agent import load_knowledge_base  # type: ignore[import-untyped]

        kb = load_knowledge_base(settings.KB_JSON_PATH)
        logger.info(
            "[%s] knowledge base loaded: %d disease(s) from '%s'",
            settings.SERVICE_NAME,
            len(kb),
            settings.KB_JSON_PATH,
        )
    except Exception as exc:
        logger.warning(
            "[%s] knowledge base failed to load at startup: %s "
            "(the /predict endpoint will report 503 until this is fixed)",
            settings.SERVICE_NAME,
            exc,
        )

    if not settings.GEMINI_API_KEY:
        logger.warning(
            "[%s] GEMINI_API_KEY is not set. "
            "/predict will return 503 until a valid key is provided.",
            settings.SERVICE_NAME,
        )

    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="AgriTwin VLM Classifier",
        description=(
            "Vision-Language Model (Gemini) leaf disease classifier. "
            "Sub-service of the AgriTwin platform. Implements ChatLeafDisease "
            "Chain-of-Thought scoring against a maize disease knowledge base."
        ),
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(router)
    return app


app = create_app()
