"""HTTP routes: health probe + disease classification API."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.config import settings
from app.schemas import ErrorResponse, HealthResponse, PredictionResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# Image MIME types the classifier can handle (same set as _guess_mime_type
# in disease_classification_agent.py).
ALLOWED_MIME_TYPES: set[str] = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/bmp",
    "image/gif",
}

# Also accept by file extension when the browser sends a generic MIME type.
ALLOWED_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}


def _mime_from_filename(filename: str | None) -> str | None:
    """Guess MIME type from the upload filename extension."""
    if not filename:
        return None
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
        "bmp": "image/bmp",
        "gif": "image/gif",
    }.get(ext)


# ---------------------------------------------------------------- probes
@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Liveness probe",
)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service=settings.SERVICE_NAME)


# ---------------------------------------------------------------- predict
@router.post(
    "/predict",
    response_model=PredictionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid image upload"},
        503: {"model": ErrorResponse, "description": "Classifier unavailable"},
    },
    tags=["Diagnosis"],
    summary="Classify a leaf disease image",
    description=(
        "Upload a leaf image as multipart/form-data. The image is sent to "
        "the Gemini VLM which scores it against the knowledge base of maize "
        "diseases and returns per-disease scores."
    ),
)
async def predict(
    image: Annotated[UploadFile, File(description="Leaf image to classify")],
) -> PredictionResponse:
    # --- validate content type ---
    content_type = image.content_type or ""
    mime_type = (
        content_type if content_type in ALLOWED_MIME_TYPES
        else _mime_from_filename(image.filename)
    )
    if mime_type is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unsupported file type '{content_type}'. "
                f"Accepted types: {', '.join(sorted(ALLOWED_MIME_TYPES))}."
            ),
        )

    # --- read & validate size ---
    max_bytes = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
    image_bytes = await image.read()

    if len(image_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    if len(image_bytes) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Image too large ({len(image_bytes) / 1024 / 1024:.1f} MB). "
                f"Maximum allowed size is {settings.MAX_IMAGE_SIZE_MB} MB."
            ),
        )

    # --- classify ---
    # Import here so /health works even if the classifier has import issues.
    try:
        import disease_classification_agent as dca  # type: ignore[import-untyped]

        classify_image_bytes = dca.classify_image_bytes
        load_knowledge_base = dca.load_knowledge_base
    except ImportError as exc:
        logger.exception("Failed to import disease_classification_agent")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Classifier module unavailable: {exc}",
        )

    try:
        kb_records = load_knowledge_base(settings.KB_JSON_PATH)
    except (FileNotFoundError, ValueError) as exc:
        logger.error("Knowledge base error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Knowledge base unavailable: {exc}",
        )

    try:
        result = classify_image_bytes(
            image_bytes=image_bytes,
            mime_type=mime_type,
            kb_records=kb_records,
            api_key=settings.GEMINI_API_KEY,
            model=settings.GEMINI_MODEL,
            base_url=settings.GEMINI_BASE_URL,
        )
    except RuntimeError as exc:
        error_msg = str(exc)
        # Never leak the API key in error responses.
        if "API key" in error_msg.lower() or "key" in error_msg.lower():
            error_msg = "Classifier configuration error. Check server logs."
        logger.error("Classification failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=error_msg,
        )
    except Exception as exc:
        logger.exception("Unexpected classification error")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Classification failed due to an internal error.",
        )

    return PredictionResponse(
        disease_name=result.get("disease_name"),
        max_score=result.get("max_score"),
        scores=result.get("scores", {}),
        raw_output=result.get("_raw_output"),
        parse_error=result.get("_parse_error"),
        missing_scores=result.get("_missing_scores"),
    )
