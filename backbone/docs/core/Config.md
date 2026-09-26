# Config Module

## Overview

The Config module manages application configuration using Pydantic Settings. It loads configuration from environment variables and provides type-safe access to settings throughout the application.

## File Location

`app/core/config.py`

## Configuration Categories

### Project Settings
- `PROJECT_NAME` - Application name (default: "AgriTwin Backend")
- `API_V1_STR` - API v1 prefix (default: "/api/v1")

### JWT Authentication
- `JWT_SECRET_KEY` - JWT signing secret (CRITICAL: change in production)
- `JWT_ALGORITHM` - JWT algorithm (default: "HS256")
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration in minutes (default: 10080 = 7 days)

### Internal Module API Keys
- `INTERN_2_API_KEY` - Intern 2 module API key
- `INTERN_3_API_KEY` - Intern 3 module API key
- `INTERN_4A_API_KEY` - Intern 4a module API key
- `INTERN_4B_API_KEY` - Intern 4b module API key
- `INTERN_5_API_KEY` - Intern 5 module API key
- `INTERN_7_API_KEY` - Intern 7 module API key
- `INTERN_8_API_KEY` - Intern 8 module API key

### Database
- `DATABASE_URL` - PostgreSQL connection string

### MinIO/S3 Storage
- `MINIO_ENDPOINT` - MinIO server address (default: "localhost:9000")
- `MINIO_ACCESS_KEY` - MinIO access key (default: "minioadmin")
- `MINIO_SECRET_KEY` - MinIO secret key (default: "YOUR_MINIO_SECRET_KEY")
- `MINIO_SECURE` - Use HTTPS (default: False)
- `MINIO_BUCKET_NAME` - Default bucket name (default: "agritwin-bucket")

### CORS
- `BACKEND_CORS_ORIGINS` - Allowed CORS origins (default: ["*"])

### Message Queue
- `RABBITMQ_URL` - RabbitMQ connection string (default: "amqp://guest:guest@localhost/")

### Storage
- `TEMP_IMAGE_STORAGE_PATH` - Temporary image storage path (default: "./storage/images")

## Usage

### Accessing Settings

```python
from app.core.config import settings

# Access any setting
project_name = settings.PROJECT_NAME
jwt_secret = settings.JWT_SECRET_KEY
database_url = settings.DATABASE_URL
```

### Database URL Helper

```python
from app.core.config import get_database_url

# Get properly formatted database URL
db_url = get_database_url()
```

### Dependency Injection

```python
from app.core.config import get_settings

def some_endpoint(settings: Settings = Depends(get_settings)):
    return {"project": settings.PROJECT_NAME}
```

## Environment Variables

Configuration is loaded from:
1. Environment variables
2. `.env` file (if present)
3. Default values in Settings class

**Priority:** Environment variables > .env file > defaults

## Environment File

The `.env` file should contain:
```env
PROJECT_NAME=AgriTwin Backend
API_V1_STR=/api/v1

DATABASE_URL=postgresql://user:password@localhost:5432/agritwin

JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=YOUR_MINIO_SECRET_KEY
MINIO_SECURE=False
MINIO_BUCKET_NAME=agritwin-bucket

BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

## Security Notes

### Critical Security Issues

The following settings have weak defaults and MUST be changed in production:

1. **JWT_SECRET_KEY** - Default is weak, use strong random string
2. **INTERN_*_API_KEY** - All have weak defaults, use strong random strings
3. **MINIO_SECRET_KEY** - Default is weak, use strong password
4. **DATABASE_URL** - Should use environment variable, not hardcode

### Recommendations

- Use environment variables for all secrets
- Never commit `.env` file to version control
- Use secrets manager in production (AWS Secrets Manager, HashiCorp Vault)
- Rotate secrets regularly
- Use different secrets for different environments

## Pydantic Settings Configuration

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )
```

- `env_file=".env"` - Load from .env file
- `env_ignore_empty=True` - Ignore empty environment variables
- `extra="ignore"` - Ignore extra fields not defined in class

## Notes

- All settings are type-safe
- Validation happens at startup
- Missing required settings will cause startup failure
- Use `.env.example` as template for new developers
- Database URL is processed to handle double percent encoding
