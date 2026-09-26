# Internal Router

## Overview

The Internal router handles all internal module endpoints that use API key authentication. These endpoints are used by internship modules for data ingestion, model management, and field state queries.

## File Location

`app/api/internal_router.py`

## Authentication

All endpoints in this router require API key authentication via the `X-API-Key` header.

**Available API Keys:**
- `INTERN_2_API_KEY` - Intern 2 module
- `INTERN_3_API_KEY` - Intern 3 module
- `INTERN_4A_API_KEY` - Intern 4a module
- `INTERN_4B_API_KEY` - Intern 4b module
- `INTERN_5_API_KEY` - Intern 5 module
- `INTERN_7_API_KEY` - Intern 7 module
- `INTERN_8_API_KEY` - Intern 8 module

**Example:**
```bash
curl -X POST http://localhost:8000/api/fields/1/sensor-readings \
  -H "X-API-Key: YOUR_INTERN_4A_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"timestamp":"2024-01-15T10:30:00Z","soil_moisture":45.5}'
```

## Endpoint Categories

### AI Model Management

#### POST /api/models
Register or get an AI model by name and version.

**Request Body:**
```json
{
  "name": "disease_detector",
  "version": "1.0.0",
  "description": "Detects crop diseases",
  "model_type": "classification",
  "framework": "pytorch"
}
```

#### GET /api/models
List all registered AI models.

### Imagery Management

#### POST /api/imagery
Create a new imagery record.

#### GET /api/imagery
List all imagery records.

#### GET /api/imagery/{id}
Get imagery by ID.

#### GET /api/imagery/field/{field_id}
List imagery for a specific field.

### Satellite Management

#### POST /api/satellites
Create a new satellite record.

#### GET /api/satellites
List all satellite records.

#### GET /api/satellites/active
List only active satellites.

#### GET /api/satellites/{id}
Get satellite by ID.

#### GET /api/satellites/name/{name}
Get satellite by name.

### Data Ingestion

#### POST /api/fields/{field_id}/sensor-readings
Ingest sensor reading data for a field.

**Request Body:**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "soil_moisture_percent": 45.5,
  "soil_temperature_c": 18.3,
  "air_temperature_c": 22.1,
  "humidity_percent": 65.0
}
```

#### POST /api/fields/{field_id}/satellite-observations
Ingest satellite observation data for a field.

**Request Body:**
```json
{
  "satellite_id": 2,
  "imagery_id": 10,
  "observation_date": "2024-01-15",
  "ndvi": 0.75,
  "cloud_cover_percent": 15.5
}
```

#### POST /api/fields/{field_id}/diagnoses
Ingest disease diagnosis results for a field.

**Request Body:**
```json
{
  "model_id": 5,
  "imagery_id": 10,
  "crop_type": "Maize",
  "disease_or_pest": "Maize Lethal Necrosis",
  "severity": 0.75,
  "confidence": 0.89,
  "diagnosed_at": "2024-01-15T10:30:00Z",
  "leaf_boundary_box": [120, 45, 200, 180],
  "detected_diseases": ["Maize Lethal Necrosis"],
  "disease_confidences": [0.89]
}
```

#### POST /api/fields/{field_id}/irrigation-plans
Ingest irrigation plan for a field.

#### POST /api/fields/{field_id}/yield-predictions
Ingest yield prediction for a field.

#### POST /api/fields/{field_id}/crop-mix-recommendations
Ingest crop mix recommendation for a field.

### Field Data Queries

#### GET /api/fields/{field_id}
Get field details.

#### GET /api/fields/{field_id}/boundary
Get field boundary polygon and area.

#### GET /api/fields/{field_id}/state
Get aggregate field state (latest readings, observations, diagnoses, plans, predictions).

**Response Example:**
```json
{
  "field": {
    "id": 1,
    "name": "North Field",
    "farm_id": 1
  },
  "boundary": {
    "id": 1,
    "polygon": "...",
    "area_hectares": 25.5
  },
  "latest_sensor_reading": {
    "id": 100,
    "soil_moisture_percent": 45.5,
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "latest_satellite_observation": {
    "id": 50,
    "ndvi": 0.75,
    "observation_date": "2024-01-15"
  },
  "latest_diagnosis": {
    "id": 25,
    "disease_or_pest": "Healthy",
    "confidence": 0.99
  },
  "latest_irrigation_plan": {
    "id": 10,
    "water_amount_mm": 25.5,
    "plan_date": "2024-01-15"
  },
  "latest_yield_prediction": {
    "id": 15,
    "predicted_yield_tons_per_hectare": 8.5,
    "prediction_date": "2024-01-15"
  },
  "latest_crop_mix_recommendation": {
    "id": 5,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

#### GET /api/fields/{field_id}/sensor-readings
Get field sensor readings with optional date filtering.

**Query Parameters:**
- `from` - Start date (ISO format)
- `to` - End date (ISO format)
- `latest` - Set to `true` to get only the latest reading
- `skip` - Pagination offset
- `limit` - Maximum records

#### GET /api/fields/{field_id}/satellite-observations
Get field satellite observations with optional date filtering.

#### GET /api/fields/{field_id}/diagnoses
Get field diagnoses with optional date filtering.

#### GET /api/fields/{field_id}/irrigation-plans
Get field irrigation plans with optional date filtering.

#### GET /api/fields/{field_id}/yield-predictions
Get field yield predictions with optional date filtering.

#### GET /api/fields/{field_id}/crop-mix-recommendations
Get field crop mix recommendations.

### Farm Queries

#### GET /api/farms/{farm_id}/fields
List all fields for a farm.

#### GET /api/farms/{farm_id}/crop-mixes/latest
Get latest crop mix recommendation for each field in a farm.

## Helper Functions

### `_assert_field_exists(field_id: int, field_svc: FieldService)`
Validates that a field exists. Raises 404 if not found.

### `_assert_farm_exists(farm_id: int, farm_svc: FarmService)`
Validates that a farm exists. Raises 404 if not found.

## Model Resolution

Ingestion endpoints support model resolution by name/version:

```python
# Can provide either model_id directly
{
  "model_id": 5
}

# Or model name and version
{
  "model_name": "disease_detector",
  "model_version": "1.0.0"
}
```

The service layer resolves the model_id automatically.

## Satellite Resolution

Satellite observation ingestion supports satellite resolution by name:

```python
# Can provide either satellite_id directly
{
  "satellite_id": 2
}

# Or satellite name
{
  "satellite_name": "Sentinel-2"
}
```

The service creates the satellite if it doesn't exist.

## Related Services

- `AIModelService` - Model management and resolution
- `ImageryService` - Imagery management
- `SatelliteService` - Satellite management and resolution
- `FieldService` - Field validation
- `FarmService` - Farm validation
- `SensorService` - Sensor data management
- `SatelliteObservationService` - Satellite observation management
- `DiagnosisService` - Diagnosis management
- `IrrigationPlanService` - Irrigation plan management
- `YieldPredictionService` - Yield prediction management
- `CropMixService` - Crop mix recommendation management

## Dependencies

- `verify_api_key` - API key authentication dependency
- All service dependencies injected via `Depends()`

## Error Handling

- **401 Unauthorized** - Missing or invalid API key
- **404 Not Found** - Field or farm not found
- **422 Unprocessable Entity** - Invalid input data
- **500 Internal Server Error** - Server error

## Notes

- All internal endpoints require API key authentication
- API keys are module-specific for tracking and security
- Field state endpoint provides aggregated view of all field data
- Date filtering uses ISO format
- Use `latest=true` query parameter for single latest record
- Model and satellite resolution provides flexibility for ingestion
