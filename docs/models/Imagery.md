# Imagery Model

## Overview

The `Imagery` model is the centralized entity for image/file management across the AgriTwin system. It provides consistent representation of images associated with fields and other entities, supporting multiple image types including ground photos, drone imagery, and satellite imagery.

## File Location

`app/models/imagery.py`

## Table Schema

**Table Name:** `imagery`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique identifier |
| `field_id` | INTEGER | FOREIGN KEY (fields.id), NULLABLE, INDEX | Associated field |
| `storage_path` | VARCHAR(512) | NOT NULL | Path/key in storage system |
| `storage_type` | VARCHAR(50) | NOT NULL, DEFAULT 'local' | Storage type (local, minio, s3) |
| `storage_bucket` | VARCHAR(255) | NULLABLE | Bucket/container name |
| `file_name` | VARCHAR(255) | NOT NULL | Original filename |
| `file_extension` | VARCHAR(50) | NOT NULL | File extension (jpg, png, tif) |
| `file_size_bytes` | FLOAT | NULLABLE | File size in bytes |
| `mime_type` | VARCHAR(100) | NULLABLE | MIME type (image/jpeg) |
| `image_type` | VARCHAR(50) | NOT NULL, DEFAULT 'ground_photo' | Image type |
| `capture_time` | TIMESTAMP | NULLABLE | When image was captured |
| `resolution_m` | FLOAT | NULLABLE | Spatial resolution in meters |
| `spectral_bands` | JSON | NULLABLE | Spectral band information |
| `width_pixels` | FLOAT | NULLABLE | Image width in pixels |
| `height_pixels` | FLOAT | NULLABLE | Image height in pixels |
| `source` | VARCHAR(255) | NULLABLE | Image source (drone_id, satellite) |
| `additional_metadata` | JSON | NULLABLE | Custom metadata |
| `uploaded_at` | TIMESTAMP | DEFAULT NOW() | Upload timestamp |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Creation timestamp |

## Relationships

- **Belongs to:** `Field` via `field_id` (SET NULL on field deletion)
- **Referenced by:** `SatelliteObservation`, `Diagnosis` via `imagery_id`

## Cascade Behavior

- When a Field is deleted, `field_id` is set to NULL (imagery is preserved)
- When Imagery is deleted, satellite_observations and diagnoses referencing it have `imagery_id` set to NULL

## Indexes

- `field_id` - Indexed for efficient field lookup
- `ix_imagery_field_type_capture` - Composite index for field imagery queries
- `ix_imagery_type_created` - Composite index for type-based queries

## Usage Examples

### Creating Imagery Record

```python
from app.models.imagery import Imagery

imagery = Imagery(
    field_id=1,
    storage_path="fields/1/imagery/uuid/image.jpg",
    storage_type="minio",
    storage_bucket="agritwin-bucket",
    file_name="field_photo_001.jpg",
    file_extension="jpg",
    file_size_bytes=2048576,
    mime_type="image/jpeg",
    image_type="ground_photo",
    capture_time="2024-01-15T10:30:00Z",
    width_pixels=4096,
    height_pixels=3072
)
```

### Uploading Image to Storage

```python
from app.core.storage import StorageService

storage = StorageService()
object_name = storage.upload_file(
    object_name="fields/1/imagery/image.jpg",
    data=image_bytes,
    length=len(image_bytes),
    content_type="image/jpeg"
)
```

### Getting Download URL

```python
from app.core.storage import StorageService

storage = StorageService()
url = storage.get_download_url(
    object_name="fields/1/imagery/image.jpg",
    expires_delta_hours=24
)
```

## Related Services

- `ImageryService` - Imagery record management
- `StorageService` - MinIO/S3 storage operations

## Related API Endpoints

### Farmer Endpoints (JWT Auth)
- `GET /api/v1/imagery` - List imagery records
- `POST /api/v1/imagery` - Create imagery record
- `GET /api/v1/imagery/{id}` - Get imagery details
- `GET /api/v1/imagery/field/{field_id}` - List imagery for field

### Internal Endpoints (API Key Auth)
- `POST /api/imagery` - Create imagery record
- `GET /api/imagery` - List imagery records
- `GET /api/imagery/{id}` - Get imagery by ID
- `GET /api/imagery/field/{field_id}` - List imagery for field

## Image Types

- **ground_photo** - Photos taken on the ground (field level)
- **drone** - Aerial imagery from drones/UAVs
- **satellite** - Satellite imagery from platforms
- **aircraft** - Aerial imagery from manned aircraft
- **other** - Custom imagery types

## Storage Types

- **local** - Local disk storage
- **minio** - MinIO S3-compatible storage
- **s3** - AWS S3 or compatible storage
- **azure** - Azure Blob Storage
- **gcs** - Google Cloud Storage

## Spectral Bands

Stored in `spectral_bands` JSON field:
```json
{
  "bands": [
    {"name": "red", "wavelength_nm": 665, "description": "Red band"},
    {"name": "green", "wavelength_nm": 560, "description": "Green band"},
    {"name": "blue", "wavelength_nm": 490, "description": "Blue band"},
    {"name": "nir", "wavelength_nm": 842, "description": "Near-infrared"}
  ]
}
```

## Additional Metadata

Stored in `additional_metadata` JSON field for custom information:
```json
{
  "camera_model": "DJI Phantom 4",
  "altitude_m": 120,
  "gimbal_angle": -45,
  "gps_coordinates": {"lat": 37.7749, "lng": -122.4194}
}
```

## Notes

- Images are stored in MinIO (S3-compatible) or local disk
- `storage_path` contains the object key or file path
- Use `StorageService` to upload, download, and delete images
- Pre-signed URLs are generated for secure access
- File size validation should be done at upload time
- All timestamp fields use UTC timezone
- Image metadata helps with analysis and processing
