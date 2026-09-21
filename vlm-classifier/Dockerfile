# VLM Classifier service — real Dockerfile
# Replaces the previous stub. Mirrors the structure of the sibling
# classical-classifier Dockerfile: slim Python base, pip install
# requirements, copy app code, uvicorn entrypoint on port 8000.

FROM python:3.11-slim AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install Python dependencies first (layer caching).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code.
COPY disease_classification_agent.py .
COPY knowledge_base.json .
COPY app/ app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
