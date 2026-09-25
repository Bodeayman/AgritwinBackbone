"""Central configuration for the vlm-classifier sub-service.

All values can be overridden via environment variables, e.g.:
    GEMINI_API_KEY=... GEMINI_MODEL=gemini-3.6-flash
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

SERVICE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ---- Gemini API ----
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.6-flash"
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/models"
    GEMINI_TIMEOUT: int = 120

    # ---- knowledge base ----
    KB_JSON_PATH: str = str(SERVICE_DIR / "knowledge_base.json")

    # ---- service ----
    SERVICE_NAME: str = "vlm-classifier"

    # ---- upload guard ----
    MAX_IMAGE_SIZE_MB: int = 10


settings = Settings()
