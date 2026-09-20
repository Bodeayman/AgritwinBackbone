"""Pydantic request schemas for the HTTP API."""

from pydantic import BaseModel, Field

from app.config import settings


class ResegmentRequest(BaseModel):
    image_id: str
    score_thresh: float = settings.SCORE_THRESH
    mask_thresh: float = settings.MASK_THRESH


class ClassifyRequest(BaseModel):
    image_id: str
    leaf_id: int = -1  # -1 = whole image


class DiagnoseQuery(BaseModel):
    """Query params for POST /api/diagnose (parsed manually in routes)."""

    leaf_id: int = 0
    score_thresh: float = settings.SCORE_THRESH
    mask_thresh: float = settings.MASK_THRESH
    # Bigger-project integration: optionally report result to backbone.
    field_id: int | None = Field(
        default=None, description="Backbone field ID to report diagnosis for"
    )
    crop_type: str | None = None
    report: bool = Field(
        default=False,
        description="If true (and field_id given), POST result to backbone",
    )
