# AgriTwin Monorepo

Agricultural management system with disease detection, crop mix optimization, and yield prediction.

## Services

- **backbone/**: Main AgriTwin backend API (FastAPI + PostgreSQL + MinIO + RabbitMQ)
- **classical-classifier/**: Classical ML classifier — Mask R-CNN leaf segmentation + ResNet-50 disease classification + Grad-CAM (port 8001)
- **vlm-classifier/**: Vision-Language Model (Gemini) leaf disease classifier using ChatLeafDisease chain-of-thought scoring against a maize knowledge base (port 8002)

## Diagnosis Chain

```
 Client ──photo──> classical-classifier ──crop──> vlm-classifier (Gemini confirm)
                        │  │                            │
                        │  └── POST /api/diagnose        │
                        │                                 
                        └── report ──> backbone (/api/fields/{id}/diagnoses)
```

1. `POST /api/diagnose` on **classical-classifier** (port 8001) runs the local pipeline: Mask R-CNN segments the leaves, one leaf is cropped, ResNet-50 predicts the disease (with Grad-CAM), all locally.
2. Classical then asks the **vlm-classifier** (port 8002) for a confirmation on the same cropped leaf; the Gemini result is returned as `vlm_confirmation`. This step is non-blocking — VLM failures never interrupt the local diagnosis.
3. When `report=true` and a `field_id` is supplied, classical POSTs the diagnosis to the **backbone** internal API (`POST /api/fields/{field_id}/diagnoses`) using `X-API-Key`.

Each failure domain (local models, VLM, backbone) is isolated — a broken VLM or unreachable backbone does not prevent a diagnosis from completing.

## Deployment (EC2 via GitHub Actions)

Pushes to `main`/`master` trigger `.github/workflows/deploy.yml`, which:
1. Runs tests (backbone + VLM classifier) in CI.
2. Builds all 3 service images and ships them to the EC2 host (`DEPLOY_DIR = /opt/agritwin-backend`).
3. Loads the images and runs `docker compose -f docker-compose.prod.yml up`.

### Required GitHub secrets

| Secret | Used for |
|--------|----------|
| `EC2_HOST`, `EC2_USERNAME`, `EC2_SSH_KEY` | SSH into the host |
| `GEMINI_API_KEY` | Enables the VLM `/predict` endpoint |
| `GEMINI_MODEL` | VLM model name (default `gemini-3.6-flash`) |

`GEMINI_API_KEY`/`GEMINI_MODEL` are forwarded into the compose environment so `${GEMINI_API_KEY:-}` interpolation works on the server.

### Classical weights (the tricky part)

The EC2 host runs **snap docker**, whose daemon and CLI **cannot access host paths** under `/opt` or `/home/<user>` (snap confinement). This breaks bind mounts **and** `docker cp`. The working approach:

- The classical weights volume is a **named volume** `agritwin_classical_weights` (declared `external: true` in the prod compose).
- At deploy time the workflow seeds it by streaming a tar over stdin:
  ```bash
  tar -C "$DEPLOY_DIR/weights" -czf - . | docker run --rm -i \
    -v agritwin_classical_weights:/weights alpine:3.20 sh -c 'tar -xzf - -C /weights'
  ```
- `classical-classifier` mounts that volume `:ro` at `/weights` (`SEGMENTER_PATH=/weights/segmenter.pth`, `CLASSIFIER_PATH=/weights/classifier.pt`).

### Updating weights on the server

```bash
scp segmenter.pth classifier.pt ubuntu@<EC2_HOST>:/opt/agritwin-backend/weights/
```

### Deployment health checks

Workflow verifies all 3 services after boot:
- `http://localhost:8000/` → backbone
- `http://localhost:8001/health` → classical-classifier
- `http://localhost:8002/health` → vlm-classifier

On failure the workflow rolls back to the previously deployed images.

## Quick Start

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f backbone
```

## Service Ports

- **backbone**: http://localhost:8000
- **classical-classifier**: http://localhost:8001
- **vlm-classifier**: http://localhost:8002
- **PostgreSQL**: localhost:5432
- **MinIO**: localhost:9000 (API), localhost:9001 (Console)
- **RabbitMQ**: localhost:5672 (AMQP), localhost:15672 (Management)

## Development

Each service can be developed independently. The backbone service contains the main AgriTwin application with all existing functionality.