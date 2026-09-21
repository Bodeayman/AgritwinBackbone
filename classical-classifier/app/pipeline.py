"""Pure ML pipeline: segmentation -> crop -> classification + Grad-CAM.

Functions receive loaded models explicitly (no module globals) so they
are easy to test and reuse. Image-encoding helpers live here too.
"""

import base64
import io

import numpy as np
import torch
from PIL import Image
from torchvision.transforms.functional import normalize, to_tensor

from app.config import settings


# ---------------------------------------------------------------- encoding
def encode_jpg(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()


def clamp_thresh(score_thresh: float, mask_thresh: float):
    return (
        min(1.0, max(0.0, score_thresh)),
        min(1.0, max(0.0, mask_thresh)),
    )


# ---------------------------------------------------------------- segmentation
def segment_leaves(
    img: Image.Image,
    segmenter,
    device: str,
    score_thresh: float = settings.SCORE_THRESH,
    mask_thresh: float = settings.MASK_THRESH,
):
    """Return list of {bbox [x1,y1,x2,y2], score, mask (bool HxW)}."""
    with torch.no_grad():
        out = segmenter([to_tensor(img).to(device)])[0]
    keep = (out["scores"] >= score_thresh) & (out["labels"] == 1)
    boxes = out["boxes"][keep].cpu()
    scores = out["scores"][keep].cpu()
    masks = (out["masks"][keep, 0] > mask_thresh).cpu().numpy()
    w, h = img.size
    leaves = []
    for box, score, mask in zip(boxes, scores, masks):
        x1, y1, x2, y2 = [max(0, int(v)) for v in box.tolist()]
        x2, y2 = min(w, x2), min(h, y2)
        if x2 <= x1 or y2 <= y1 or not mask.any():
            continue
        leaves.append({"bbox": [x1, y1, x2, y2], "score": float(score), "mask": mask})
    leaves.sort(key=lambda leaf: leaf["score"], reverse=True)
    return leaves


def masked_crop(img: Image.Image, mask: np.ndarray | None, bbox: list | None):
    arr = np.array(img)
    if mask is not None:
        arr = arr * mask[:, :, None]
    if bbox is not None:
        x1, y1, x2, y2 = bbox
        arr = arr[y1:y2, x1:x2]
    return Image.fromarray(arr)


def thumb(img: Image.Image, mask, bbox, size: int = 256) -> str:
    crop = masked_crop(img, mask, bbox)
    crop.thumbnail((size, size))
    return encode_jpg(crop)


def serialize_leaves(img: Image.Image, leaves: list) -> list:
    return [
        {
            "id": i,
            "bbox": leaf["bbox"],
            "score": round(leaf["score"], 3),
            "thumb": thumb(img, leaf["mask"], leaf["bbox"]),
        }
        for i, leaf in enumerate(leaves)
    ]


# ---------------------------------------------------------------- classification
def classify_transform(img: Image.Image):
    """Longest side -> 224, pad to 224x224, ImageNet normalize.

    Returns (tensor, canvas) where canvas is the 224x224 PIL image the
    model actually sees.
    """
    size = settings.IMG_SIZE
    w, h = img.size
    s = size / max(w, h)
    img = img.resize((round(w * s), round(h * s)))
    canvas = Image.new("RGB", (size, size))
    canvas.paste(img, ((size - img.width) // 2, (size - img.height) // 2))
    return normalize(to_tensor(canvas), settings.MEAN, settings.STD), canvas


def _jet(x: np.ndarray) -> np.ndarray:
    """Jet colormap for a [0,1] array -> uint8 RGB (no extra deps)."""
    x = np.clip(x, 0, 1)
    r = np.clip(1.5 - np.abs(4 * x - 3), 0, 1)
    g = np.clip(1.5 - np.abs(4 * x - 2), 0, 1)
    b = np.clip(1.5 - np.abs(4 * x - 1), 0, 1)
    return (np.stack([r, g, b], axis=-1) * 255).astype(np.uint8)


def gradcam_predict(x: torch.Tensor, canvas: Image.Image, classifier, device: str):
    """Single forward pass: softmax probs + Grad-CAM overlay on canvas."""
    size = settings.IMG_SIZE
    feats, grads = {}, {}

    def _save_act(m, i, o):
        feats["a"] = o

    def _save_grad(m, gi, go):
        grads["g"] = go[0]

    fh = classifier.layer4.register_forward_hook(_save_act)
    bh = classifier.layer4.register_full_backward_hook(_save_grad)
    try:
        classifier.zero_grad()
        logits = classifier(x.unsqueeze(0).to(device))
        probs = torch.softmax(logits, 1)[0]
        best = int(probs.argmax())
        logits[0, best].backward()
    finally:
        fh.remove()
        bh.remove()
    activ = feats["a"][0].detach()  # C,h,w
    grad = grads["g"][0].detach()  # C,h,w
    cam = (grad.mean(dim=(1, 2))[:, None, None] * activ).sum(0).clamp(min=0)
    cam = cam / (cam.max() + 1e-8)
    heat = (
        np.array(
            Image.fromarray((cam.cpu().numpy() * 255).astype(np.uint8)).resize(
                (size, size), Image.BILINEAR
            )
        )
        / 255.0
    )
    base = np.array(canvas).astype(np.float32)
    overlay = Image.fromarray(
        (0.55 * base + 0.45 * _jet(heat).astype(np.float32)).clip(0, 255).astype(np.uint8)
    )
    return probs.cpu().tolist(), overlay


def predict_disease(crop: Image.Image, classifier, device: str):
    """Classify one leaf crop (or whole image).

    Returns (disease, confidence, probs dict, model_view PIL, gradcam PIL).
    """
    x, canvas = classify_transform(crop)
    with torch.enable_grad():
        probs, overlay = gradcam_predict(x, canvas, classifier, device)
    best = int(np.argmax(probs))
    return (
        settings.CLASSES[best],
        round(probs[best], 4),
        {c: round(p, 4) for c, p in zip(settings.CLASSES, probs)},
        canvas,
        overlay,
    )


def diagnose_photo(
    img,
    segmenter,
    classifier,
    device: str,
    leaf_id: int = 0,
    score_thresh: float = settings.SCORE_THRESH,
    mask_thresh: float = settings.MASK_THRESH,
):
    """Full pipeline: photo -> leaves + disease + Grad-CAM.

    Args:
        img: PIL image, raw image bytes, or file path.
        leaf_id: which detected leaf to diagnose (0 = highest score);
                 -1 = skip selection, classify the whole image.
    """
    if isinstance(img, (bytes, bytearray)):
        img = Image.open(io.BytesIO(img)).convert("RGB")
    elif isinstance(img, str):
        img = Image.open(img).convert("RGB")
    score_thresh, mask_thresh = clamp_thresh(score_thresh, mask_thresh)
    leaves = segment_leaves(img, segmenter, device, score_thresh, mask_thresh)
    if leaf_id == -1:
        crop, bbox = img, None
    else:
        if not leaves:
            raise ValueError("No leaves detected; use leaf_id=-1 for whole image")
        if not 0 <= leaf_id < len(leaves):
            raise ValueError(f"Invalid leaf_id {leaf_id} ({len(leaves)} leaves found)")
        crop = masked_crop(img, leaves[leaf_id]["mask"], leaves[leaf_id]["bbox"])
        bbox = leaves[leaf_id]["bbox"]
    disease, confidence, probs, canvas, overlay = predict_disease(
        crop, classifier, device
    )
    return {
        "leaves": leaves,
        "leaf_id": leaf_id,
        "bbox": bbox,
        "disease": disease,
        "confidence": confidence,
        "probs": probs,
        "model_view": canvas,
        "gradcam": overlay,
    }
