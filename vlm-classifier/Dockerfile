# Pseudo/placeholder Dockerfile for the vlm-classifier service.
#
# The real VLM classifier is not implemented yet. This stub
# exists so `docker compose build/start vlm-classifier` works and the
# service answers health checks on port 8000 until the real one lands.
# It intentionally mirrors the shape of the sibling Dockerfiles
# (backbone, classical-classifier): slim Python base, EXPOSE 8000,
# container listens on 0.0.0.0:8000.
#
# Replace this whole file with the real multi-stage build (pip install
# requirements + COPY app/ + uvicorn) when the VLM service is added.

FROM python:3.11-slim AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

# Stdlib-only stub: GET /health -> {"status":"ok","service":"vlm-classifier-stub"},
# everything else -> 404. No dependencies to install.
COPY app.py .
CMD ["python", "app.py"]
