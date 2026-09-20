"""Model construction + lazy singleton loading.

Importing this module must NOT load weights (keeps `import app.main`
cheap and lets /health answer even when weights are missing).
Call `get_segmenter()` / `get_classifier()` inside request handlers
or from the app lifespan handler to trigger loading.
"""

import threading
from pathlib import Path

import torch
import torchvision
from torchvision.models.detection import maskrcnn_resnet50_fpn
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor

from app.config import settings

_lock = threading.Lock()
_segmenter = None
_classifier = None
_segmenter_error: Exception | None = None
_classifier_error: Exception | None = None


def get_device() -> str:
    if settings.DEVICE in ("cpu", "cuda"):
        if settings.DEVICE == "cuda" and not torch.cuda.is_available():
            return "cpu"
        return settings.DEVICE
    return "cuda" if torch.cuda.is_available() else "cpu"


def build_segmenter_arch():
    m = maskrcnn_resnet50_fpn(weights=None)
    m.roi_heads.box_predictor = FastRCNNPredictor(
        m.roi_heads.box_predictor.cls_score.in_features, 2
    )
    m.roi_heads.mask_predictor = MaskRCNNPredictor(
        m.roi_heads.mask_predictor.conv5_mask.in_channels, 256, 2
    )
    return m


def build_classifier_arch(num_classes: int):
    m = torchvision.models.resnet50(weights=None)
    m.fc = torch.nn.Linear(m.fc.in_features, num_classes)
    return m


def _load_state_dict(path: str):
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(
            f"Weights file not found: {p}. "
            f"Set SEGMENTER_PATH/CLASSIFIER_PATH env or place "
            f"'segmenter.pth' and 'classifier.pt' next to app/config.py."
        )
    return torch.load(str(p), map_location=get_device())


def get_segmenter():
    """Return loaded segmenter (loads once, thread-safe)."""
    global _segmenter, _segmenter_error
    if _segmenter is not None:
        return _segmenter
    with _lock:
        if _segmenter is not None:
            return _segmenter
        try:
            m = build_segmenter_arch()
            m.load_state_dict(_load_state_dict(settings.SEGMENTER_PATH))
            _segmenter = m.to(get_device()).eval()
            _segmenter_error = None
        except Exception as e:  # keep error for /ready diagnostics
            _segmenter_error = e
            raise
        return _segmenter


def get_classifier():
    """Return loaded classifier (loads once, thread-safe)."""
    global _classifier, _classifier_error
    if _classifier is not None:
        return _classifier
    with _lock:
        if _classifier is not None:
            return _classifier
        try:
            m = build_classifier_arch(len(settings.CLASSES))
            m.load_state_dict(_load_state_dict(settings.CLASSIFIER_PATH))
            _classifier = m.to(get_device()).eval()
            _classifier_error = None
        except Exception as e:
            _classifier_error = e
            raise
        return _classifier


def preload_models() -> dict:
    """Eagerly load both models; returns status dict (used by lifespan)."""
    status = {"segmenter": "ok", "classifier": "ok"}
    try:
        get_segmenter()
    except Exception as e:
        status["segmenter"] = f"{type(e).__name__}: {e}"
    try:
        get_classifier()
    except Exception as e:
        status["classifier"] = f"{type(e).__name__}: {e}"
    return status


def readiness() -> dict:
    """Lightweight readiness probe (does not force-load missing models)."""
    return {
        "segmenter_loaded": _segmenter is not None,
        "classifier_loaded": _classifier is not None,
        "segmenter_error": str(_segmenter_error) if _segmenter_error else None,
        "classifier_error": str(_classifier_error) if _classifier_error else None,
        "device": get_device(),
    }
