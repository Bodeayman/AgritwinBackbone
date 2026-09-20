# Repositories Documentation

This directory contains documentation for the repository layer components in the AgriTwin system.

## Repository Layer Overview

The repository layer implements the Repository pattern to abstract database operations. It provides a clean separation between the service layer (business logic) and the database (data access).

## Repository Pattern

All repositories follow this pattern:

```python
from app.repositories.base import BaseRepository
from sqlalchemy import select
from sqlalchemy.orm import Session

class EntityRepository(BaseRepository[EntityType]):
    def __init__(self, db: Session):
        super().__init__(EntityType, db)

    # Custom domain-specific queries
    def list_by_related_field(self, related_id: int, skip: int = 0, limit: int = 100):
        statement = select(EntityType).where(EntityType.related_id == related_id)
        statement = statement.offset(skip).limit(limit)
        return list(self.db.scalars(statement).all())
```

## Available Repositories

### Base Repository
- [BaseRepository](./BaseRepository.md) - Generic CRUD operations

### Entity-Specific Repositories
- `FarmRepository` - Farm data access
- `FieldRepository` - Field data access
- `FieldBoundaryRepository` - Field boundary geometry operations
- `AIModelRepository` - AI model data access
- `SatelliteRepository` - Satellite data access
- `ImageryRepository` - Imagery data access
- `SatelliteObservationRepository` - Satellite observation data access
- `DiagnosisRepository` - Diagnosis data access
- `IrrigationPlanRepository` - Irrigation plan data access
- `YieldPredictionRepository` - Yield prediction data access
- `CropCycleRepository` - Crop cycle data access
- `CropMixRecommendationRepository` - Crop mix recommendation data access
- `SensorRepository` - Sensor reading data access
- `WeatherRepository` - Weather data access

## Common Repository Methods

### Base Methods (from BaseRepository)
- `get(id)` - Get by primary key
- `get_multi(skip, limit)` - Get multiple with pagination
- `create(db_obj)` - Create new record
- `update(db_obj, update_data)` - Update existing record
- `remove(id)` - Delete record

### Custom Methods (entity-specific)
- `list_by_farm(farm_id)` - List by farm
- `list_by_field(field_id)` - List by field
- `list_by_field_date_range(field_id, from_dt, to_dt)` - List with date filtering
- `get_by_name(name)` - Get by name
- `get_by_name_and_version(name, version)` - Get by name and version
- `get_latest_by_field(field_id)` - Get latest record for field

## Database Session

Repositories receive a database session via dependency injection:

```python
from app.core.database import get_db

def get_field_service(db: Session = Depends(get_db)) -> FieldService:
    return FieldService(db)
```

The session:
- Is created per request
- Is managed by FastAPI
- Is closed after request completes
- Handles transactions automatically

## Query Examples

### Simple Query
```python
statement = select(Field).where(Field.farm_id == farm_id)
result = list(self.db.scalars(statement).all())
```

### Query with Pagination
```python
statement = select(Field).where(Field.farm_id == farm_id)
statement = statement.offset(skip).limit(limit)
result = list(self.db.scalars(statement).all())
```

### Query with Date Range
```python
statement = select(Diagnosis).where(
    Diagnosis.field_id == field_id,
    Diagnosis.diagnosed_at >= from_dt,
    Diagnosis.diagnosed_at <= to_dt
)
result = list(self.db.scalars(statement).all())
```

### Query with Ordering
```python
statement = select(Diagnosis).where(
    Diagnosis.field_id == field_id
).order_by(Diagnosis.diagnosed_at.desc())
result = list(self.db.scalars(statement).all())
```

## Eager Loading

For relationships, use eager loading to avoid N+1 queries:

```python
from sqlalchemy.orm import selectinload

statement = select(Field).options(
    selectinload(Field.boundary)
).where(Field.id == field_id)
```

## Repository File Locations

All repositories are located in: `app/repositories/`

- `base.py` - BaseRepository
- `farm_repository.py` - FarmRepository
- `field_repository.py` - FieldRepository
- `field_boundary_repository.py` - FieldBoundaryRepository
- `ai_model_repository.py` - AIModelRepository
- `satellite_repository.py` - SatelliteRepository
- `imagery_repository.py` - ImageryRepository
- `satellite_observation_repository.py` - SatelliteObservationRepository
- `diagnosis_repository.py` - DiagnosisRepository
- `irrigation_plan_repository.py` - IrrigationPlanRepository
- `yield_prediction_repository.py` - YieldPredictionRepository
- `crop_cycle_repository.py` - CropCycleRepository
- `crop_mix_recommendation_repository.py` - CropMixRecommendationRepository
- `sensor_repository.py` - SensorRepository
- `weather_repository.py` - WeatherRepository

## Best Practices

### DO
- Use repositories for all database access
- Add custom methods for domain-specific queries
- Use SQLAlchemy 2.0 select() syntax
- Add indexes in model definitions
- Use eager loading for relationships
- Keep repositories focused on data access only

### DON'T
- Put business logic in repositories
- Directly use database session in services
- Mix repository and service logic
- Skip transactions for multi-step operations
- Ignore N+1 query problems

## Notes

- Repositories should be thin - business logic in services
- Use BaseRepository for common operations
- Add custom methods for specific query needs
- Test repositories with in-memory databases
- All queries use SQLAlchemy 2.0 syntax
