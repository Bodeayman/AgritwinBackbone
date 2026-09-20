# SatelliteObservation Model

## Overview

The `SatelliteObservation` model represents satellite data observations for fields. It links satellite imagery and platforms to specific fields, capturing multi-spectral data, vegetation indices, and observation metadata for agricultural monitoring.

## File Location

`app/models/satellite_observation.py`

## Table Schema

**Table Name:** `satellite_observations`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique identifier |
| `field_id` | INTEGER | FOREIGN KEY (fields.id), NOT NULL | Observed field |
| `satellite_id` | INTEGER | FOREIGN KEY (satellites.id), NULLABLE | Satellite platform |
| `imagery_id` | INTEGER | FOREIGN KEY (imagery.id), NULLABLE | Associated imagery |
| `model_id` | INTEGER | FOREIGN KEY (ai_models.id), NULLABLE | Processing model |
| `observation_date` | DATE | NOT NULL | Date of observation |
| `cloud_cover_percent` | FLOAT | NULLABLE | Cloud coverage percentage |
| `ndvi` | FLOAT | NULLABLE | Normalized Difference Vegetation Index |
| `ndwi` | FLOAT | NULLABLE | Normalized Difference Water Index |
| `evi` | FLOAT | NULLABLE | Enhanced Vegetation Index |
| `spectral_data` | JSON | NULLABLE | Raw spectral band values |
| `additional_indices` | JSON | NULLABLE | Custom vegetation indices |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Record creation timestamp |

## Relationships

- **Belongs to:** `Field` via `field_id` (CASCADE on field deletion)
- **References:** `Satellite` via `satellite_id` (SET NULL on satellite deletion)
- **References:** `Imagery` via `imagery_id` (SET NULL on imagery deletion)
- **References:** `AIModel` via `model_id` (SET NULL on model deletion)

## Cascade Behavior

- When a Field is deleted, all associated SatelliteObservations are deleted (CASCADE)
- When a Satellite is deleted, `satellite_id` is set to NULL
- When Imagery is deleted, `imagery_id` is set to NULL
- When an AIModel is deleted, `model_id` is set to NULL

## Usage Examples

### Creating a Satellite Observation

```python
from app.models.satellite_observation import SatelliteObservation
from datetime import date

observation = SatelliteObservation(
    field_id=1,
    satellite_id=2,
    imagery_id=10,
    model_id=5,
    observation_date=date(2024, 1, 15),
    cloud_cover_percent=15.5,
    ndvi=0.75,
    ndwi=0.32,
    evi=0.68,
    spectral_data={
        "red": 0.15,
        "green": 0.25,
        "blue": 0.12,
        "nir": 0.65
    },
    additional_indices={
        "gndvi": 0.72,
        "savi": 0.58
    }
)
```

## Related Services

- `SatelliteObservationService` - Observation record management and queries

## Related API Endpoints

### Farmer Endpoints (JWT Auth)
- `GET /api/v1/satellite-observations` - List observations
- `GET /api/v1/satellite-observations/{id}` - Get observation details

### Internal Endpoints (API Key Auth)
- `POST /api/fields/{field_id}/satellite-observations` - Ingest satellite data
- `GET /api/fields/{field_id}/satellite-observations` - Get field observations

## Vegetation Indices

### NDVI (Normalized Difference Vegetation Index)
- Range: -1.0 to 1.0
- Formula: (NIR - Red) / (NIR + Red)
- Interpretation:
  - < 0.1: Barren/Urban
  - 0.2-0.5: Sparse vegetation
  - 0.6-0.9: Dense vegetation
  - > 0.9: Dense/canopy

### NDWI (Normalized Difference Water Index)
- Range: -1.0 to 1.0
- Formula: (Green - NIR) / (Green + NIR)
- Interpretation:
  - Positive: Water bodies
  - Negative: Vegetation/Soil

### EVI (Enhanced Vegetation Index)
- Range: -1.0 to 1.0
- Formula: 2.5 * ((NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1))
- Improves sensitivity in high-biomass regions

## Spectral Data Format

JSON object with band reflectance values:
```json
{
  "red": 0.15,
  "green": 0.25,
  "blue": 0.12,
  "nir": 0.65,
  "swir1": 0.35,
  "swir2": 0.28
}
```

## Additional Indices Format

JSON object with custom indices:
```json
{
  "gndvi": 0.72,
  "savi": 0.58,
  "osavi": 0.65,
  "msavi2": 0.45
}
```

## Cloud Cover Interpretation

- **0-10%** - Clear
- **10-30%** - Mostly clear
- **30-50%** - Partly cloudy
- **50-70%** - Mostly cloudy
- **70-100%** - Cloudy (data may be unreliable)

## Notes

- Observations are historical records for trend analysis
- Multiple observations can exist per field over time
- Vegetation indices enable crop health monitoring
- Cloud cover affects data quality
- Spectral data enables custom index calculation
- All timestamp fields use UTC timezone
- Used in conjunction with imagery for visual analysis
