# Services Documentation

This directory contains documentation for all service layer components in the AgriTwin system.

## Service Layer Overview

The service layer contains business logic and orchestrates operations between the API layer and repository layer. Services follow a clean architecture pattern with clear separation of concerns.

## Service Responsibilities

- **Business Logic** - Implement domain-specific rules and operations
- **Orchestration** - Coordinate operations across multiple repositories
- **Validation** - Validate business rules before data persistence
- **Model Resolution** - Resolve AI models, satellites, imagery by name/version
- **Data Transformation** - Convert between entities and schemas

## Available Services

### Authentication & User Management
- [AuthService](./AuthService.md) - User registration, authentication, JWT tokens

### Farm & Field Management
- [FarmService](./FarmService.md) - Farm CRUD operations
- [FieldService](./FieldService.md) - Field CRUD operations, farm field listing
- [FieldBoundaryService](./FieldBoundaryService.md) - Field boundary geometry and area calculations

### AI & Satellite Management
- [AIModelService](./AIModelService.md) - AI model registration, resolution, active model queries
- [SatelliteService](./SatelliteService.md) - Satellite registration, resolution
- [ImageryService](./ImageryService.md) - Imagery record management
- [SatelliteObservationService](./SatelliteObservationService.md) - Satellite observation data management

### Monitoring & Analysis
- [SensorService](./SensorService.md) - Sensor reading management
- [WeatherService](./WeatherService.md) - Weather data management
- [DiagnosisService](./DiagnosisService.md) - Disease diagnosis record management
- [IrrigationPlanService](./IrrigationPlanService.md) - Irrigation plan management
- [YieldPredictionService](./YieldPredictionService.md) - Yield prediction management

### Crop Management
- [CropCycleService](./CropCycleService.md) - Crop cycle management
- [CropMixService](./CropMixService.md) - Crop mix recommendation management

### Specialized Services
- [ImageProcessingService](./ImageProcessingService.md) - Image processing operations
- [EventService](./EventService.md) - Event management
- [LocationService](./LocationService.md) - Location and geometry operations

## Service Pattern

All services follow this pattern:

```python
class EntityService:
    def __init__(self, db: Session):
        self.repo = EntityRepository(db)

    def create(self, entity_in: EntityCreate) -> EntityOut:
        # Business logic
        obj = Entity(**entity_in.dict())
        self.repo.create(obj)
        return EntityOut.model_validate(obj)

    def get(self, entity_id: int) -> EntityOut | None:
        obj = self.repo.get(entity_id)
        return EntityOut.model_validate(obj) if obj else None

    def list(self, skip: int = 0, limit: int = 100) -> List[EntityOut]:
        objs = self.repo.get_multi(skip=skip, limit=limit)
        return [EntityOut.model_validate(o) for o in objs]

    def update(self, entity_id: int, entity_in: EntityUpdate) -> EntityOut | None:
        obj = self.repo.get(entity_id)
        if not obj:
            return None
        self.repo.update(obj, entity_in.dict(exclude_unset=True))
        return EntityOut.model_validate(obj)

    def delete(self, entity_id: int) -> bool:
        return self.repo.remove(entity_id)
```

## Dependency Injection

Services are injected via FastAPI dependency injection:

```python
from app.api.deps import get_field_service

@router.post("/fields")
def create_field(
    field_in: FieldCreate,
    field_service: FieldService = Depends(get_field_service)
):
    return field_service.create_field(field_in)
```

## Error Handling

Services should:
- Validate business rules before persistence
- Return `None` for not-found scenarios
- Raise HTTPException for validation errors
- Use appropriate HTTP status codes:
  - 400 - Bad Request (validation errors)
  - 404 - Not Found (entity doesn't exist)
  - 409 - Conflict (duplicate, constraint violation)
  - 422 - Unprocessable Entity (invalid data)
  - 500 - Internal Server Error (unexpected errors)

## Transaction Management

Services typically:
- Use repository pattern for data access
- Rely on SQLAlchemy session for transactions
- Commit changes in repository layer
- Consider explicit transaction boundaries for complex operations

## Model Resolution

Services that handle AI models, satellites, or imagery provide resolution methods:

```python
def resolve_model_id(model_id: int | None, model_name: str | None, model_version: str | None) -> int | None:
    """Resolve model ID from either direct ID or name/version."""
    if model_id:
        return model_id
    if model_name and model_version:
        model = get_by_name_and_version(model_name, model_version)
        return model.id if model else None
    return None
```

## Service File Locations

All services are located in: `app/services/`

- `auth_service.py` - AuthService
- `farm_service.py` - FarmService
- `field_service.py` - FieldService
- `field_boundary_service.py` - FieldBoundaryService
- `ai_model_service.py` - AIModelService
- `satellite_service.py` - SatelliteService
- `imagery_service.py` - ImageryService
- `satellite_observation_service.py` - SatelliteObservationService
- `diagnosis_service.py` - DiagnosisService
- `irrigation_plan_service.py` - IrrigationPlanService
- `yield_prediction_service.py` - YieldPredictionService
- `crop_cycle_service.py` - CropCycleService
- `crop_mix_service.py` - CropMixService
- `sensor_service.py` - SensorService
- `weather_service.py` - WeatherService
- `image_processing_service.py` - ImageProcessingService
- `event_service.py` - EventService
- `location_service.py` - LocationService

## Notes

- Services should not contain HTTP-specific logic
- Use repositories for all data access
- Return Pydantic schemas, not raw entities
- Keep services focused on business logic
- Avoid circular dependencies between services
- Use dependency injection for testability
