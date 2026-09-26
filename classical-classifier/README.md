# Classical Classifier

Classical ML classifier sub-service: **leaf segmentation + disease classification + Grad-CAM**.

## Pipeline (`app/pipeline.py`)

1. **Segmentation** — Mask R-CNN (`maskrcnn_resnet50_fpn`) detects leaves → `[{bbox, score, mask}]`, sorted by score.
2. **Crop** — user-selected leaf (`leaf_id`) is masked and cropped; `leaf_id=-1` uses the whole image.
3. **Classification** — ResNet-50 predicts the disease across `settings.CLASSES` and produces a Grad-CAM heatmap overlay.
4. **VLM confirmation** — the cropped leaf is POSTed to the `VLM_URL` service (`vlm-classifier`, port 8002). Gemini's answer comes back as `vlm_confirmation`. Non-blocking: failures return `ok=false` and never interrupt the local diagnosis.
5. **Backbone report** — when `report=true` and `field_id` is given, the diagnosis is POSTed to `BACKEND_URL/api/fields/{field_id}/diagnoses` with `X-API-Key: INTERN_API_KEY`. Non-blocking as well.

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness |
| GET | `/ready` | Readiness incl. model load state |
| POST | `/api/diagnose` | One-shot: photo in → leaves + disease + Grad-CAM out |
| POST | `/api/classify` | Classify (whole image) |
| POST | `/api/segment` | Detect leaves only |
| POST | `/api/resegment` | Mask R-CNN resegmentation |

## Models & Weights

- Architecture is built from torchvision with random init; the trained weights come from `segmenter.pth` (Mask R-CNN, 2 classes) and `classifier.pt` (ResNet-50, `len(CLASSES)` classes).
- `SEGMENTER_PATH` / `CLASSIFIER_PATH` default to files next to `app/config.py`; in compose they point to the `/weights` volume (mounted `:ro`).
- On EC2 the weights live in a named Docker volume `agritwin_classical_weights`, seeded at deploy time by streaming a tar over stdin (the snap docker daemon cannot reach host paths under `/opt` or `/home/<user>`).
- Models are lazy-loaded singletons (`app/models.py`); `/health` works even when weights are missing.

## Env

| Var | Purpose |
|-----|---------|
| `SEGMENTER_PATH` / `CLASSIFIER_PATH` | Weight file paths |
| `BACKEND_URL` | Backbone base URL for reporting |
| `INTERN_API_KEY` | `X-API-Key` header sent to backbone |
| `VLM_URL` | Base URL of vlm-classifier to ask for confirmation |
| `VLM_TIMEOUT` | HTTP timeout for the VLM call (s) |
| `DEVICE` | `cpu` / `cuda` |
| `SCORE_THRESH` / `MASK_THRESH` | Detection thresholds |
| `IMG_SIZE` / `MEAN` / `STD` | Classification preprocess params |
| `CLASSES` | Class labels (JSON list) |

## Tests

`tests/test_vlm_client.py` — offline tests for the VLM confirmation client (unset URL, success parsing, non-200, network error).

Run: `cd classical-classifier && pip install -r requirements.txt && python -m pytest tests/ -q`