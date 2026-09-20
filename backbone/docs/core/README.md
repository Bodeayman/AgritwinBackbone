# Core Module Documentation

This directory contains documentation for core infrastructure components in the AgriTwin system.

## Core Module Overview

The core module provides infrastructure services including configuration management, database connectivity, security utilities, storage operations, and validation helpers.

## Available Modules

### Configuration
- [Config](./Config.md) - Application configuration management

### Database
- [Database](./Database.md) - Database engine and session management

### Security
- `security.py` - JWT token generation and password hashing

### Storage
- `storage.py` - MinIO/S3 object storage operations
- `local_storage.py` - Local disk storage fallback

### Validation
- `validation.py` - Custom validators and validation logic

## Module Descriptions

### Config Module

**File:** `app/core/config.py`

Manages application configuration using Pydantic Settings:
- Loads settings from environment variables
- Provides type-safe configuration access
- Includes JWT, database, storage, and CORS settings

**Key Functions:**
- `settings` - Global Settings instance
- `get_settings()` - Dependency injection for settings
- `get_database_url()` - Processed database URL

### Database Module

**File:** `app/core/database.py`

Manages SQLAlchemy database operations:
- Database engine configuration
- Session factory creation
- Dependency injection for database sessions

**Key Functions:**
- `engine` - SQLAlchemy engine
- `SessionLocal` - Session factory
- `get_db()` - Dependency injection generator

### Security Module

**File:** `app/core/security.py`

Provides security utilities:
- Password hashing with pbkdf2_sha256
- Password verification
- JWT token generation
- JWT token decoding

**Key Functions:**
- `verify_password(plain_password, hashed_password)` - Verify password
- `get_password_hash(password)` - Hash password
- `create_access_token(data, expires_delta)` - Generate JWT
- `decode_access_token(token)` - Decode JWT

### Storage Module

**File:** `app/core/storage.py`

Manages MinIO/S3 object storage:
- MinIO client initialization
- Bucket creation on startup
- File upload, download, and delete operations
- Pre-signed URL generation

**Key Classes:**
- `minio_client` - Global MinIO client
- `StorageService` - Storage operations class
- `init_storage()` - Initialize storage buckets
- `get_storage()` - Dependency injection generator

### Local Storage Module

**File:** `app/core/local_storage.py`

Provides local disk storage fallback:
- File upload to local disk
- File download from local disk
- File deletion from local disk

**Key Classes:**
- `LocalDiskImageStorage` - Local storage operations
- `get_local_image_storage()` - Dependency injection

### Validation Module

**File:** `app/core/validation.py`

Provides custom validators:
- Field boundary validation
- Geometry validation
- Business rule validation

## Dependency Injection

Core modules provide dependency injection for use in API endpoints:

```python
from app.core.config import get_settings
from app.core.database import get_db
from app.core.storage import get_storage

@router.get("/endpoint")
def endpoint(
    db: Session = Depends(get_db),
    storage: StorageService = Depends(get_storage),
    settings: Settings = Depends(get_settings)
):
    ...
```

## Security Best Practices

### Password Management
- Never store plain text passwords
- Use pbkdf2_sha256 for hashing
- Hashing is one-way (cannot decrypt)

### JWT Tokens
- Use strong secret keys
- Set appropriate expiration times
- Include user ID in token payload
- Validate tokens on each request

### Storage Security
- Use pre-signed URLs for temporary access
- Set appropriate bucket policies
- Use HTTPS in production
- Validate file types on upload

## Environment Variables

Required environment variables:
- `DATABASE_URL` - Database connection string
- `JWT_SECRET_KEY` - JWT signing secret
- `MINIO_ACCESS_KEY` - MinIO access key
- `MINIO_SECRET_KEY` - MinIO secret key

Optional environment variables:
- `JWT_ALGORITHM` - JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration (default: 10080)
- `MINIO_ENDPOINT` - MinIO server address (default: localhost:9000)
- `BACKEND_CORS_ORIGINS` - CORS origins (default: *)

## File Locations

All core modules are located in: `app/core/`

- `config.py` - Configuration management
- `database.py` - Database engine and sessions
- `security.py` - Security utilities
- `storage.py` - MinIO/S3 storage
- `local_storage.py` - Local disk storage
- `validation.py` - Custom validators

## Notes

- Core modules provide infrastructure services
- Use dependency injection for testability
- Keep secrets in environment variables
- Use strong cryptographic algorithms
- Validate all inputs at the boundaries
