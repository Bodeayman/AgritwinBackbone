# Diagnosis Model

## Overview

The `Diagnosis` model represents disease and pest diagnosis results for fields. It stores detailed information including detected diseases, confidence scores, severity, treatment suggestions, and leaf boundary boxes for computer vision applications.

## File Location

`app/models/diagnosis.py`

## Table Schema

**Table Name:** `diagnoses`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique identifier |
| `field_id` | INTEGER | FOREIGN KEY (fields.id), NOT NULL | Field being diagnosed |
| `model_id` | INTEGER | FOREIGN KEY (ai_models.id), NULLABLE | AI model used |
| `imagery_id` | INTEGER | FOREIGN KEY (imagery.id), NULLABLE | Imagery analyzed |
| `crop_type` | VARCHAR(100) | NULLABLE | Type of crop diagnosed |
| `disease_or_pest` | VARCHAR(255) | NOT NULL | Disease or pest name |
| `severity` | FLOAT | NULLABLE | Severity score (0.0-1.0) |
| `confidence` | FLOAT | NULLABLE | Model confidence (0.0-1.0) |
| `latitude` | FLOAT | NULLABLE | Latitude of diagnosis location |
| `longitude` | FLOAT | NULLABLE | Longitude of diagnosis location |
| `status` | VARCHAR(50) | NOT NULL, DEFAULT 'processed' | Processing status |
| `diagnosed_at` | TIMESTAMP | NOT NULL | When diagnosis was made |
| `leaf_boundary_box` | JSON | NULLABLE | Leaf bounding box [x, y, w, h] |
| `detected_diseases` | JSON | NULLABLE | List of detected diseases |
| `disease_confidences` | JSON | NULLABLE | Confidence scores per disease |
| `explanation` | TEXT | NULLABLE | Diagnosis explanation |
| `treatment_suggestion` | TEXT | NULLABLE | Recommended treatment |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Record creation timestamp |

## Relationships

- **Belongs to:** `Field` via `field_id` (CASCADE on field deletion)
- **References:** `AIModel` via `model_id` (SET NULL on model deletion)
- **References:** `Imagery` via `imagery_id` (SET NULL on imagery deletion)

## Cascade Behavior

- When a Field is deleted, all associated Diagnoses are deleted (CASCADE)
- When an AIModel is deleted, `model_id` is set to NULL
- When Imagery is deleted, `imagery_id` is set to NULL

## Indexes

- `ix_diagnoses_field_diagnosed` - Composite index on (field_id, diagnosed_at)

## Usage Examples

### Creating a Diagnosis

```python
from app.models.diagnosis import Diagnosis
from datetime import datetime

diagnosis = Diagnosis(
    field_id=1,
    model_id=5,
    imagery_id=10,
    crop_type="Maize",
    disease_or_pest="Maize Lethal Necrosis",
    severity=0.75,
    confidence=0.89,
    latitude=37.7749,
    longitude=-122.4194,
    status="processed",
    diagnosed_at=datetime.utcnow(),
    leaf_boundary_box=[120, 45, 200, 180],
    detected_diseases=["Maize Lethal Necrosis", "Northern Corn Leaf Blight"],
    disease_confidences=[0.89, 0.12],
    explanation="Early signs of MLN detected in northern section",
    treatment_suggestion="Apply resistant varieties and remove infected plants"
)
```

### Creating a Healthy Crop Diagnosis

```python
diagnosis = Diagnosis(
    field_id=1,
    crop_type="Wheat",
    disease_or_pest="Healthy",
    severity=0.0,
    confidence=0.99,
    status="processed",
    diagnosed_at=datetime.utcnow(),
    leaf_boundary_box=[85, 32, 150, 160],
    detected_diseases=["Healthy"],
    disease_confidences=[0.99],
    explanation="No signs of disease detected",
    treatment_suggestion="Continue regular monitoring"
)
```

## Related Services

- `DiagnosisService` - Diagnosis record management and queries

## Related API Endpoints

### Farmer Endpoints (JWT Auth)
- `GET /api/v1/diagnoses` - List diagnoses
- `GET /api/v1/diagnoses/{id}` - Get diagnosis details

### Internal Endpoints (API Key Auth)
- `POST /api/fields/{field_id}/diagnoses` - Ingest diagnosis results
- `GET /api/fields/{field_id}/diagnoses` - Get field diagnoses

## Status Values

- **pending** - Awaiting processing
- **processing** - Currently being processed
- **processed** - Successfully processed
- **failed** - Processing failed
- **ready** - Ready for review

## Leaf Boundary Box Format

JSON array representing bounding box in image coordinates:
```json
[120, 45, 200, 180]
```
- x: Left coordinate
- y: Top coordinate
- w: Width
- h: Height

## Detected Diseases Format

JSON array of disease names:
```json
["Maize Lethal Necrosis", "Northern Corn Leaf Blight", "Healthy"]
```

## Disease Confidences Format

JSON array of confidence scores corresponding to detected diseases:
```json
[0.89, 0.12, 0.99]
```

## Common Diseases

- **Maize Lethal Necrosis** - Viral disease affecting maize
- **Northern Corn Leaf Blight** - Fungal disease
- **Southern Corn Leaf Blight** - Fungal disease
- **Wheat Rust** - Fungal disease affecting wheat
- **Healthy** - No disease detected

## Severity Scale

- **0.0 - 0.2** - Minimal/No impact
- **0.2 - 0.4** - Low severity
- **0.4 - 0.6** - Moderate severity
- **0.6 - 0.8** - High severity
- **0.8 - 1.0** - Critical severity

## Notes

- Diagnoses are historical records, never overwritten
- Multiple diagnoses can exist per field over time
- Confidence scores range from 0.0 to 1.0
- Leaf boundary boxes are for computer vision debugging
- Treatment suggestions are AI-generated recommendations
- All timestamp fields use UTC timezone
- Status tracking enables async processing workflows
