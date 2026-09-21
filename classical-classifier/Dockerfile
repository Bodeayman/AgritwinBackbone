FROM python:3.11-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


FROM python:3.11-slim AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/root/.local/bin:$PATH

COPY --from=builder /root/.local /root/.local

# Weights (*.pt/*.pth) are shipped with the build context; at runtime they
# can also be mounted or overridden via SEGMENTER_PATH / CLASSIFIER_PATH.
COPY app/ ./app/
COPY requirements.txt .

EXPOSE 8000

# Compose maps host 8001 -> container 8000.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
