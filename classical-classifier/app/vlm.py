"""Client for requesting a VLM confirmation from the vlm-classifier service.

The backend diagnosis is produced locally (Mask R-CNN + ResNet-50). When
`VLM_URL` is configured, the cropped leaf is sent to the VLM /predict
endpoint (Gemini-backed) for a second opinion. Failures never interrupt
the local diagnosis — a failed VLM call just adds `ok=False` to the result.
"""

import io

import httpx
from PIL import Image

from app.config import settings


def _crop_to_jpeg(img: Image.Image, quality: int = 92) -> bytes:
    buf = io.BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=quality)
    return buf.getvalue()


async def confirm_with_vlm(img: Image.Image) -> dict:
    """POST the leaf crop to the VLM /predict. Returns a dict, never raises.

    On success the dict carries VLM-agnostic fields plus the VLM's own
    (`disease_name`, `max_score`, `scores`). On failure only `{ok, info}`.
    """
    base = settings.VLM_URL.rstrip("/")
    if not base:
        return {
            "ok": False,
            "info": "VLM_URL not configured, skipping VLM confirmation",
        }
    url = f"{base}/predict"
    files = {
        "image": ("leaf.jpg", _crop_to_jpeg(img), "image/jpeg"),
    }
    try:
        async with httpx.AsyncClient(timeout=settings.VLM_TIMEOUT) as client:
            resp = await client.post(url, files=files)
    except Exception as e:
        return {"ok": False, "info": f"{type(e).__name__}: {e}"}
    if resp.status_code != 200:
        return {
            "ok": False,
            "info": f"VLM rejected ({resp.status_code}): {resp.text[:300]}",
        }
    data = resp.json()
    return {
        "ok": True,
        "info": "vlm confirmed",
        "disease_name": data.get("disease_name"),
        "max_score": data.get("max_score"),
        "scores": data.get("scores", {}),
        "raw_output": data.get("raw_output"),
        "parse_error": data.get("parse_error"),
        "missing_scores": data.get("missing_scores"),
    }