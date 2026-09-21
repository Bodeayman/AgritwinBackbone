"""Pydantic response schemas for the HTTP API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., examples=["ok"])
    service: str = Field(..., examples=["vlm-classifier"])


class PredictionResponse(BaseModel):
    """Classification result returned by the VLM disease classifier."""

    disease_name: str | None = Field(
        ...,
        description="Name of the top-scoring disease, or null if parsing failed.",
    )
    max_score: float | None = Field(
        ...,
        description="Score of the top-scoring disease, or null if parsing failed.",
    )
    scores: dict[str, float] = Field(
        default_factory=dict,
        description="Per-disease scores assigned by the VLM.",
    )
    raw_output: str | None = Field(
        default=None,
        description="Raw text output from the VLM (for debugging).",
    )
    parse_error: str | None = Field(
        default=None,
        description="Parsing error message, if the VLM output could not be fully parsed.",
    )
    missing_scores: list[str] | None = Field(
        default=None,
        description="Disease names for which no score could be extracted.",
    )


class ErrorResponse(BaseModel):
    detail: str
