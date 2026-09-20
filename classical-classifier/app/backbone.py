"""Client for reporting diagnosis results to the backbone service.

Payload matches backbone's internal `DiagnosisCreate` schema
(`POST /api/fields/{field_id}/diagnoses`). Failures never raise —
they are returned as (ok=False, info) so classification still succeeds
even when backbone is unreachable.
"""

from datetime import datetime, timezone

import httpx

from app.config import settings


def build_diagnosis_payload(
    field_id: int,
    disease: str,
    confidence: float,
    probs: dict,
    bbox: list | None,
    crop_type: str | None = None,
) -> dict:
    ordered = sorted(probs.items(), key=lambda kv: kv[1], reverse=True)
    return {
        "field_id": field_id,
        "model_name": settings.MODEL_NAME,
        "model_version": settings.MODEL_VERSION,
        "crop_type": crop_type,
        "disease_or_pest": disease,
        "severity": None,
        "confidence": confidence,
        "status": "processed",
        "diagnosed_at": datetime.now(timezone.utc).isoformat(),
        "leaf_boundary_box": bbox,
        "detected_diseases": [name for name, _ in ordered],
        "disease_confidences": [float(p) for _, p in ordered],
        "explanation": (
            f"Classical classifier ({settings.MODEL_NAME} {settings.MODEL_VERSION}) "
            f"predicted '{disease}' with confidence {confidence:.2f}."
        ),
    }


async def report_diagnosis(payload: dict) -> tuple[bool, str]:
    """POST payload to backbone. Returns (ok, info). Never raises."""
    base = settings.BACKEND_URL.rstrip("/")
    if not base:
        return False, "BACKEND_URL not configured, skipping backbone report"
    url = f"{base}/api/fields/{payload['field_id']}/diagnoses"
    headers = (
        {"X-API-Key": settings.INTERN_API_KEY} if settings.INTERN_API_KEY else {}
    )
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code in (200, 201):
            return True, f"reported, backbone id={resp.json().get('id')}"
        return False, f"backbone rejected ({resp.status_code}): {resp.text[:300]}"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"
