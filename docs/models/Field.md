# Field Model

## Overview

The `Field` model represents a specific agricultural area within a farm. Fields are the primary unit for crop management, monitoring, and analysis. Each field has associated data including satellite observations, sensor readings, weather data, diagnoses, irrigation plans, and yield predictions.

## File Location

`app/models/field.py`

## Table Schema

**Table Name:** `fields`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique identifier |
| `farm_id` | INTEGER | FOREIGN KEY (farms.id), NOT NULL, INDEX | Farm this field belongs to |
| `name` | VARCHAR(100) | NOT NULL | Human-readable field name |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT NOW(), ON UPDATE | Last modification timestamp |

## Relationships

- **Belongs to:** `Farm` via `farm_id`
- **Has one:** `FieldBoundary` (polygon geometry with PostGIS)
- **Has many:** `CropCycle` entities
- **Referenced by:** `SensorReading`, `Weather`, `Diagnosis`, `IrrigationPlan`, `YieldPrediction`, `CropMixRecommendation`, `SatelliteObservation`, `Imagery`

## Cascade Behavior

- When a Farm is deleted, all associated Fields are deleted (CASCADE)
- When a Field is deleted, all related data is deleted (CASCADE):
  - `sensor_readings`
  - `weather`
  - `diagnoses`
  - `irrigation_plans`
  - `yield_predictions`
  - `crop_cycles`
  - `crop_mix_recommendations`
  - `satellite_observations`
  - `imagery`

## Indexes

- `farm_id` - Indexed for efficient farm lookup

## Properties

### `current_crop`

Returns the crop from the active 'growing' cycle, if any.

```python
field.current_crop  # Returns: 'Maize' or None
```

## Usage Examples

### Creating a Field

```python
from app.models.field import Field

field = Field(
    farm_id=1,
    name="North Field"
)
```

### Getting Current Crop

```python
crop = field.current_crop
if crop:
    print(f"Currently growing: {crop}")
```

### Querying Fields by Farm

```python
from app.repositories.field_repository import FieldRepository

repo = FieldRepository(db)
fields = repo.list_by_farm(farm_id=1)
```

## Related Services

- `FieldService` - Business logic for field operations
- `FieldBoundaryService` - Geometry and area calculations
- `CropCycleService` - Crop cycle management

## Related API Endpoints

### Farmer Endpoints (JWT Auth)
- `GET /api/v1/fields` - List user's fields
- `POST /api/v1/fields` - Create a new field
- `GET /api/v1/fields/{id}` - Get field details
- `PUT /api/v1/fields/{id}` - Update field
- `DELETE /api/v1/fields/{id}` - Delete field

### Internal Endpoints (API Key Auth)
- `GET /api/fields/{field_id}` - Get field details
- `GET /api/fields/{field_id}/boundary` - Get field boundary polygon
- `GET /api/fields/{field_id}/state` - Get aggregate field state
- `GET /api/fields/{field_id}/sensor-readings` - Get sensor history
- `GET /api/fields/{field_id}/satellite-observations` - Get satellite history
- `GET /api/fields/{field_id}/diagnoses` - Get diagnosis history
- `POST /api/fields/{field_id}/sensor-readings` - Ingest sensor data
- `POST /api/fields/{field_id}/diagnoses` - Ingest diagnosis results

## Notes

- Field names are not required to be unique within a farm
- Field boundaries use PostGIS for spatial operations
- All timestamp fields use UTC timezone
- Field is the central entity linking most data in the system
