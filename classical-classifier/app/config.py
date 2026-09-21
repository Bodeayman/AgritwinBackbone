"""Central configuration for the classical-classifier sub-service.

All values can be overridden via environment variables, e.g.:
    SEGMENTER_PATH=/weights/segmenter.pth BACKEND_URL=http://backbone:8000
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

APP_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ---- model weights (resolved relative to app/ by default) ----
    SEGMENTER_PATH: str = str(APP_DIR / "segmenter.pth")
    CLASSIFIER_PATH: str = str(APP_DIR / "classifier.pt")

    # ---- inference defaults ----
    CLASSES: list[str] = [
        "Anthracnose",
        "Black Spot",
        "Canker",
        "Greening",
        "Healthy",
        "Root Rot",
    ]
    SCORE_THRESH: float = 0.5
    MASK_THRESH: float = 0.5
    IMG_SIZE: int = 224
    MEAN: list[float] = [0.485, 0.456, 0.406]
    STD: list[float] = [0.229, 0.224, 0.225]

    # ---- service ----
    SERVICE_NAME: str = "classical-classifier"
    # Empty = models load lazily on first request; set DEVICE=cpu/cuda to force.
    DEVICE: str = ""
    STORE_MAX_ITEMS: int = 50

    # ---- bigger-project integration ----
    # Base URL of the backbone API, e.g. http://backbone:8000 (compose) .
    BACKEND_URL: str = ""
    # API key sent as X-API-Key when reporting diagnoses to backbone.
    INTERN_API_KEY: str = ""
    MODEL_NAME: str = "classical-resnet50"
    MODEL_VERSION: str = "v1"


settings = Settings()
