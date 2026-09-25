"""HTTP routes: health probes + segment/classify/diagnose API."""

import io

from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image

from app import backbone as backbone_client
from app import pipeline
from app.config import settings
from app.models import get_classifier, get_device, get_segmenter, readiness
from app.schemas import ClassifyRequest, ResegmentRequest
from app.store import store

router = APIRouter()


def _loaded_models():
    """Load (or reuse) both models; map weight problems to 503."""
    try:
        segmenter = get_segmenter()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Segmenter unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Segmenter failed: {e}")
    try:
        classifier = get_classifier()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Classifier unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Classifier failed: {e}")
    return segmenter, classifier, get_device()


async def _read_image(file: UploadFile) -> Image.Image:
    try:
        return Image.open(io.BytesIO(await file.read())).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")


# ---------------------------------------------------------------- probes
@router.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": settings.SERVICE_NAME}


@router.get("/ready", tags=["Health"])
def ready():
    r = readiness()
    ready_flag = r["segmenter_loaded"] and r["classifier_loaded"]
    return {"ready": ready_flag, **r}


# ---------------------------------------------------------------- API
@router.post("/api/segment", tags=["Diagnosis"])
async def api_segment(
    file: UploadFile = File(...),
    score_thresh: float = settings.SCORE_THRESH,
    mask_thresh: float = settings.MASK_THRESH,
):
    img = await _read_image(file)
    segmenter, _, device = _loaded_models()
    score_thresh, mask_thresh = pipeline.clamp_thresh(score_thresh, mask_thresh)
    leaves = pipeline.segment_leaves(img, segmenter, device, score_thresh, mask_thresh)
    image_id = store.save(img, leaves)
    return {
        "image_id": image_id,
        "width": img.width,
        "height": img.height,
        "image": pipeline.encode_jpg(img),
        "score_thresh": score_thresh,
        "mask_thresh": mask_thresh,
        "leaves": pipeline.serialize_leaves(img, leaves),
    }


@router.post("/api/resegment", tags=["Diagnosis"])
def api_resegment(req: ResegmentRequest):
    entry = store.get(req.image_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Image expired, upload again")
    segmenter, _, device = _loaded_models()
    score_thresh, mask_thresh = pipeline.clamp_thresh(
        req.score_thresh, req.mask_thresh
    )
    leaves = pipeline.segment_leaves(
        entry["image"], segmenter, device, score_thresh, mask_thresh
    )
    store.update_leaves(req.image_id, leaves)
    return {
        "image_id": req.image_id,
        "score_thresh": score_thresh,
        "mask_thresh": mask_thresh,
        "leaves": pipeline.serialize_leaves(entry["image"], leaves),
    }


@router.post("/api/classify", tags=["Diagnosis"])
def api_classify(req: ClassifyRequest):
    entry = store.get(req.image_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Image expired, upload again")
    _, classifier, device = _loaded_models()
    img, leaves = entry["image"], entry["leaves"]
    if req.leaf_id == -1:
        crop = img
    else:
        if not 0 <= req.leaf_id < len(leaves):
            raise HTTPException(status_code=400, detail="Invalid leaf_id")
        crop = pipeline.masked_crop(
            img, leaves[req.leaf_id]["mask"], leaves[req.leaf_id]["bbox"]
        )
    disease, confidence, probs, canvas, overlay = pipeline.predict_disease(
        crop, classifier, device
    )
    return {
        "disease": disease,
        "confidence": confidence,
        "probs": probs,
        "model_view": pipeline.encode_jpg(canvas),
        "gradcam": pipeline.encode_jpg(overlay),
    }


@router.post("/api/diagnose", tags=["Diagnosis"])
async def api_diagnose(
    file: UploadFile = File(...),
    leaf_id: int = 0,
    score_thresh: float = settings.SCORE_THRESH,
    mask_thresh: float = settings.MASK_THRESH,
    field_id: int | None = None,
    crop_type: str | None = None,
    report: bool = True,
):
    """One-shot: photo in -> leaves + disease + Grad-CAM out.

    If `field_id` is given, the result is POSTed to the backbone
    internal API (`BACKEND_URL` + `INTERN_API_KEY` env) automatically.
    """
    img = await _read_image(file)
    segmenter, classifier, device = _loaded_models()
    try:
        out = pipeline.diagnose_photo(
            img, segmenter, classifier, device, leaf_id, score_thresh, mask_thresh
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    resp = {
        "disease": out["disease"],
        "confidence": out["confidence"],
        "probs": out["probs"],
        "leaf_id": out["leaf_id"],
        "bbox": out["bbox"],
        "leaves": pipeline.serialize_leaves(img, out["leaves"]),
        "model_view": pipeline.encode_jpg(out["model_view"]),
        "gradcam": pipeline.encode_jpg(out["gradcam"]),
    }
    if report and field_id is not None:
        payload = backbone_client.build_diagnosis_payload(
            field_id, out["disease"], out["confidence"], out["probs"],
            out["bbox"], crop_type,
        )
        ok, info = await backbone_client.report_diagnosis(payload)
        resp["backbone_report"] = {"ok": ok, "info": info}
    return resp
