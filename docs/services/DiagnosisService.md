# DiagnosisService

## Overview

The `DiagnosisService` handles business logic for disease and pest diagnosis operations. It manages diagnosis record creation, retrieval by field, and historical queries for field health monitoring.

## File Location

`app/services/diagnosis_service.py`

## Responsibilities

- Create diagnosis records
- Retrieve diagnoses by ID
- List diagnoses by field with date filtering
- Delete diagnosis records
- Business logic for diagnosis operations

## Methods

### `create(diag_in: DiagnosisCreate) -> DiagnosisOut`

Creates a new diagnosis record.

**Parameters:**
- `diag_in` - DiagnosisCreate schema with diagnosis data

**Returns:** Created diagnosis as DiagnosisOut schema

**Example:**
```python
from app.services.diagnosis_service import DiagnosisService
from app.schemas.diagnosis import DiagnosisCreate
from datetime import datetime

service = DiagnosisService(db)
diagnosis = service.create(
    DiagnosisCreate(
        field_id=1,
        model_id=5,
        imagery_id=10,
        crop_type="Maize",
        disease_or_pest="Maize Lethal Necrosis",
        severity=0.75,
        confidence=0.89,
        diagnosed_at=datetime.utcnow(),
        leaf_boundary_box=[120, 45, 200, 180],
        detected_diseases=["Maize Lethal Necrosis"],
        disease_confidences=[0.89]
    )
)
```

### `get(diag_id: int) -> DiagnosisOut | None`

Retrieves a diagnosis by ID.

**Parameters:**
- `diag_id` - Diagnosis primary key

**Returns:** Diagnosis as DiagnosisOut schema, or None if not found

**Example:**
```python
diagnosis = service.get(diag_id=1)
```

### `list_by_field(field_id: int, from_dt: datetime | None = None, to_dt: datetime | None = None, skip: int = 0, limit: int = 100) -> List[DiagnosisOut]`

Lists diagnoses for a field with optional date filtering.

**Parameters:**
- `field_id` - Field primary key
- `from_dt` - Optional start date for filtering
- `to_dt` - Optional end date for filtering
- `skip` - Number of records to skip (pagination)
- `limit` - Maximum records to return

**Returns:** List of diagnoses as DiagnosisOut schemas

**Example:**
```python
from datetime import datetime, timedelta

# Get all diagnoses for field
diagnoses = service.list_by_field(field_id=1)

# Get diagnoses from last 30 days
from_date = datetime.utcnow() - timedelta(days=30)
diagnoses = service.list_by_field(field_id=1, from_dt=from_date)
```

### `delete(diag_id: int) -> bool`

Deletes a diagnosis record.

**Parameters:**
- `diag_id` - Diagnosis primary key

**Returns:** True if deleted, False if not found

**Note:** Diagnoses are historical records; consider soft delete or archiving.

**Example:**
```python
deleted = service.delete(diag_id=1)
```

## Dependencies

- `DiagnosisRepository` - Data access for Diagnosis entities
- `FieldRepository` - Data access for Field entities (for validation)

## Related API Endpoints

### Farmer Endpoints (JWT Auth)
- `GET /api/v1/diagnoses` - List diagnoses
- `GET /api/v1/diagnoses/{id}` - Get diagnosis details

### Internal Endpoints (API Key Auth)
- `POST /api/fields/{field_id}/diagnoses` - Ingest diagnosis results
- `GET /api/fields/{field_id}/diagnoses` - Get field diagnoses

## Business Logic

### Diagnosis Creation
- Validates that the field exists
- Stores detailed disease information
- Supports multiple detected diseases with confidence scores
- Includes leaf boundary boxes for computer vision debugging

### Historical Queries
- Supports date range filtering
- Useful for trend analysis
- Pagination for large result sets

### Status Tracking
- Supports async processing workflows
- Status values: pending, processing, processed, failed, ready

## Diagnosis Data Structure

### Infected Crop Example
```json
{
  "crop_type": "Maize",
  "disease_or_pest": "Maize Lethal Necrosis",
  "severity": 0.75,
  "confidence": 0.89,
  "leaf_boundary_box": [120, 45, 200, 180],
  "detected_diseases": ["Maize Lethal Necrosis", "Northern Corn Leaf Blight"],
  "disease_confidences": [0.89, 0.12],
  "status": "processed"
}
```

### Healthy Crop Example
```json
{
  "crop_type": "Wheat",
  "disease_or_pest": "Healthy",
  "severity": 0.0,
  "confidence": 0.99,
  "leaf_boundary_box": [85, 32, 150, 160],
  "detected_diseases": ["Healthy"],
  "disease_confidences": [0.99],
  "status": "processed"
}
```

## Error Handling

- **404 Not Found** - Diagnosis or field not found
- **422 Validation Error** - Invalid input data
- **500 Internal Server Error** - Database errors

## Notes

- Diagnoses are historical records, never overwritten
- Multiple diagnoses can exist per field over time
- Confidence scores indicate model reliability
- Treatment suggestions are AI-generated recommendations
- All timestamp fields use UTC timezone
- Used in conjunction with imagery for visual analysis
