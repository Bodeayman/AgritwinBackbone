# Schemas Documentation

This directory contains documentation for Pydantic schemas used in the AgriTwin system.

## Schema Layer Overview

The schema layer defines Pydantic models for request validation, response serialization, and data transformation. Schemas ensure data integrity and provide automatic validation for API endpoints.

## Schema Categories

### Request Schemas (Create/Update)
- Used for validating incoming API requests
- Define required and optional fields
- Provide type hints and validation rules

### Response Schemas (Out)
- Used for serializing database entities to API responses
- Exclude sensitive fields (passwords, etc.)
- Format data for client consumption

## Common Schema Patterns

### Create Schema
```python
class EntityCreate(BaseModel):
    field1: str
    field2: int
    optional_field: str | None = None
```

### Update Schema
```python
class EntityUpdate(BaseModel):
    field1: str | None = None
    field2: int | None = None
    optional_field: str | None = None
```

### Response Schema
```python
class EntityOut(BaseModel):
    id: int
    field1: str
    field2: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

## Available Schemas

### Authentication
- `UserRegister` - User registration request
- `UserLogin` - User login request
- `Token` - JWT token response

### Organizational
- `FarmCreate` - Farm creation request
- `FarmUpdate` - Farm update request
- `FarmOut` - Farm response

- `FieldCreate` - Field creation request
- `FieldUpdate` - Field update request
- `FieldOut` - Field response

- `FieldBoundaryOut` - Field boundary response

### AI & Satellite
- `AIModelCreate` - AI model registration request
- `AIModelOut` - AI model response

- `SatelliteCreate` - Satellite creation request
- `SatelliteOut` - Satellite response

- `ImageryCreate` - Imagery creation request
- `ImageryOut` - Imagery response

- `SatelliteObservationCreate` - Satellite observation creation request
- `SatelliteObservationOut` - Satellite observation response

### Monitoring & Analysis
- `SensorCreate` - Sensor reading creation request
- `SensorOut` - Sensor reading response

- `WeatherOut` - Weather response

- `DiagnosisCreate` - Diagnosis creation request
- `DiagnosisOut` - Diagnosis response

- `IrrigationPlanCreate` - Irrigation plan creation request
- `IrrigationPlanOut` - Irrigation plan response

- `YieldPredictionCreate` - Yield prediction creation request
- `YieldPredictionOut` - Yield prediction response

### Crop Management
- `CropCycleCreate` - Crop cycle creation request
- `CropCycleUpdate` - Crop cycle update request
- `CropCycleOut` - Crop cycle response

- `CropMixRecommendationCreate` - Crop mix recommendation creation request
- `CropMixRecommendationOut` - Crop mix recommendation response

## Schema File Locations

All schemas are located in: `app/schemas/`

- `auth.py` - Authentication schemas
- `farm.py` - Farm schemas
- `field.py` - Field schemas
- `field_boundary.py` - Field boundary schemas
- `ai_model.py` - AI model schemas
- `satellite.py` - Satellite schemas
- `imagery.py` - Imagery schemas
- `satellite_observation.py` - Satellite observation schemas
- `diagnosis.py` - Diagnosis schemas
- `irrigation_plan.py` - Irrigation plan schemas
- `yield_prediction.py` - Yield prediction schemas
- `crop_cycle.py` - Crop cycle schemas
- `crop_mix_recommendation.py` - Crop mix recommendation schemas
- `sensor_reading.py` - Sensor reading schemas
- `weather.py` - Weather schemas

## Validation Features

Pydantic provides automatic validation:

### Type Validation
```python
class EntityCreate(BaseModel):
    age: int  # Must be integer
    name: str  # Must be string
```

### Required vs Optional
```python
class EntityCreate(BaseModel):
    required_field: str  # Must be provided
    optional_field: str | None = None  # Can be omitted
```

### String Constraints
```python
class EntityCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr  # Email validation
```

### Numeric Constraints
```python
class EntityCreate(BaseModel):
    age: int = Field(..., ge=0, le=150)
    price: float = Field(..., gt=0)
```

### Date/Time Validation
```python
class EntityCreate(BaseModel):
    date: date
    timestamp: datetime
```

## Converting Entities to Schemas

Using `model_validate()` to convert SQLAlchemy entities to Pydantic schemas:

```python
from app.schemas.field import FieldOut

# Convert entity to schema
field_out = FieldOut.model_validate(field_entity)
```

## Converting Schemas to Entities

Using `dict()` to convert Pydantic schemas to dictionaries for entity creation:

```python
field_dict = field_create.dict()
field_entity = Field(**field_dict)
```

## Config Options

Common configuration options:

```python
class EntityOut(BaseModel):
    ...

    class Config:
        from_attributes = True  # Allow ORM mode
        populate_by_name = True  # Allow population by alias
```

## Best Practices

### DO
- Use schemas for all API request/response data
- Separate Create, Update, and Out schemas
- Use field validation in schemas
- Exclude sensitive fields in Out schemas
- Use descriptive field names

### DON'T
- Pass raw entities to API responses
- Mix validation logic in controllers
- Skip schema validation
- Include passwords in response schemas
- Use ambiguous field names

## Notes

- Schemas provide automatic validation
- Invalid data returns 422 Unprocessable Entity
- Use `model_validate()` for entity to schema conversion
- Use `dict()` for schema to entity conversion
- All datetime fields are in UTC
- JSON fields use Python types (dict, list)
