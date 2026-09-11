from typing import List
import json
import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    PROJECT_NAME: str = "AgriTwin Backend"
    API_V1_STR: str = "/api/v1"

    # JWT Settings
    JWT_SECRET_KEY: str = "agritwin_jwt_secret_key_change_in_production_12345"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # Internal Module API Keys
    INTERN_2_API_KEY: str = "secret-intern-2-key"
    INTERN_3_API_KEY: str = "secret-intern-3-key"
    INTERN_4A_API_KEY: str = "secret-intern-4a-key"
    INTERN_4B_API_KEY: str = "secret-intern-4b-key"
    INTERN_5_API_KEY: str = "secret-intern-5-key"
    INTERN_7_API_KEY: str = "secret-intern-7-key"
    INTERN_8_API_KEY: str = "secret-intern-8-key"

    # Temporary Disk Storage Path
    TEMP_IMAGE_STORAGE_PATH: str = "./storage/images"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # MinIO / S3 Storage
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadminpassword"
    MINIO_SECURE: bool = False
    MINIO_BUCKET_NAME: str = "agritwin-bucket"

    # CORS Origins (JSON list or comma-separated string or *). Stored as raw string
    # so pydantic-settings never attempts to json.loads() it from the environment.
    BACKEND_CORS_ORIGINS: str = "*"
    RABBITMQ_URL: str = "amqp://guest:guest@localhost/"

    @property
    def cors_origins(self) -> List[str]:
        s = (self.BACKEND_CORS_ORIGINS or "*").strip()
        if not s or s == "*":
            return ["*"]
        if s.startswith("["):
            try:
                parsed = json.loads(s)
                return parsed if isinstance(parsed, list) else [str(parsed)]
            except json.JSONDecodeError:
                pass
        return [o.strip() for o in s.split(",") if o.strip()]


settings = Settings()

def get_settings() -> Settings:
    """Return the global Settings instance for dependency injection."""
    return settings

def get_database_url() -> str:
    """Return the database URL suitable for SQLAlchemy (single %)."""
    raw_url = settings.DATABASE_URL
    url = raw_url.replace("%%", "%")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url
