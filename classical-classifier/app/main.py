"""Classical classifier sub-service: leaf segmentation + disease classification.

Run locally:
    uvicorn app.main:app --reload --port 8001
Run from repo root via compose (builds ./classical-classifier/Dockerfile).

Env:
    SEGMENTER_PATH / CLASSIFIER_PATH — weight files (default: app/*.pth|*.pt)
    BACKEND_URL — backbone base URL for diagnosis reporting (optional)
    INTERN_API_KEY — X-API-Key sent to backbone (optional)
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.config import settings
from app.models import preload_models
from app.routes import router
from app.ui import HTML_PAGE


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Eager load so failures show up in container logs at startup;
    # routes still lazy-load, so /health works even if weights are missing.
    status = preload_models()
    print(f"[{settings.SERVICE_NAME}] model preload: {status}")
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="AgriTwin Classical Classifier",
        description=(
            "Leaf segmentation (Mask R-CNN) + disease classification "
            "(ResNet-50) + Grad-CAM. Sub-service of AgriTwin; optionally "
            "reports results to the backbone via POST /api/diagnose "
            "with field_id + report=true."
        ),
        lifespan=lifespan,
    )
    app.include_router(router)

    @app.get("/", response_class=HTMLResponse, tags=["UI"])
    def index():
        return HTML_PAGE

    return app


app = create_app()
