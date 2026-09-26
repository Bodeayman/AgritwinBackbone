# VLM Classifier

Vision-Language Model (Gemini) leaf disease classifier. Implements the **ChatLeafDisease** chain-of-thought scoring approach against a maize disease knowledge base.

## How it works

When `POST /predict` receives an image, `disease_classification_agent.py`:

1. Builds a user message with the disease knowledge base (disease names + descriptions, ordered by name for stable scoring).
2. Sends the image + prompt to Gemini (`GEMINI_API_KEY`, default model `gemini-3.6-flash`).
3. Asks for a structured Chain-of-Thought output: reasoning + a per-disease score.
4. Parses the response into `{disease_name, max_score, scores, ...}`.

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness (`{"status":"ok","service":"vlm-classifier"}`) |
| POST | `/predict` | Multipart `image` upload → per-disease scores |

`/predict` returns:
- `disease_name` — highest-scoring disease
- `max_score` — its confidence
- `scores` — full per-disease score map
- `raw_output`, `parse_error`, `missing_scores` — diagnostics

Errors: `400` (bad/unreadable image), `503` (classifier/KB/config unavailable — API key is never leaked in responses).

## Knowledge base

- `knowledge_base.json` — compiled reference list baked into the image.
- `Disease Knowledge Base/MAIZE_0xx.json` — raw + `_standardized.json` source data.
- `KB_JSON_PATH` overrides the path at runtime.

## Env

| Var | Purpose |
|-----|---------|
| `GEMINI_API_KEY` | Gemini API key (required for `/predict`) |
| `GEMINI_MODEL` | Model name (default `gemini-3.6-flash`) |
| `GEMINI_BASE_URL` | API base URL |
| `GEMINI_TIMEOUT` | HTTP timeout (default 120s) |
| `KB_JSON_PATH` | Knowledge base path |

## Role in the system

The VLM **confirms** the classical classifier's diagnosis. The chain is:

`backbone (8000) ← classical-classifier (8001) ← vlm-classifier (8002)`

`/api/diagnose` on the classical classifier sends the cropped leaf here; the VLM result is returned as `vlm_confirmation`. Both the classical service and this one report results to the backbone; the VLM itself is only called by the classical classifier. If the VLM is down or keyless, classical still completes using its local ResNet-50.

## Tests

`tests/test_disease_classification_agent.py` — 11 offline tests (KB loading, user-message building, MIME guessing, CoT output parsing). No live Gemini needed.

Run: `cd vlm-classifier && pip install -r requirements.txt && python -m pytest tests/ -q`