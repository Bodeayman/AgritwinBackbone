# Models Documentation

This directory contains documentation for all database models in the AgriTwin system.

## Model Overview

The AgriTwin data model is organized around farms, fields, and agricultural monitoring data. Models follow SQLAlchemy 2.0 conventions with proper foreign key relationships and cascade behaviors.

## Core Models

### Organizational Models
- [User](./User.md) - User accounts for farmer authentication
- [Farm](./Farm.md) - Agricultural organizations/properties
- [Field](./Field.md) - Specific agricultural areas within farms

### AI & Satellite Models
- [AIModel](./AIModel.md) - AI/ML model metadata and versioning
- [Satellite](./Satellite.md) - Satellite platform information
- [Imagery](./Imagery.md) - Centralized image/file management
- [SatelliteObservation](./SatelliteObservation.md) - Satellite data observations

### Monitoring & Analysis Models
- [SensorReading](./SensorReading.md) - IoT sensor data from fields
- [Weather](./Weather.md) - Weather measurements for fields
- [Diagnosis](./Diagnosis.md) - Disease and pest diagnosis results
- [IrrigationPlan](./IrrigationPlan.md) - AI-generated irrigation recommendations
- [YieldPrediction](./YieldPrediction.md) - AI-generated yield forecasts

### Crop Management Models
- [CropCycle](./CropCycle.md) - Planting and harvest cycles

## Model Relationships

```
User (1) ──────── (∞) Farm (1) ──────── (∞) Field
                                                  │
                                                  ├───── (∞) SensorReading
                                                  ├───── (∞) Weather
                                                  ├───── (∞) Diagnosis
                                                  ├───── (∞) IrrigationPlan
                                                  ├───── (∞) YieldPrediction
                                                  ├───── (∞) CropCycle
                                                  ├───── (∞) SatelliteObservation
                                                  ├───── (∞) Imagery
                                                  └───── (1) FieldBoundary

AIModel (1) ──────── (∞) Diagnosis
AIModel (1) ──────── (∞) IrrigationPlan
AIModel (1) ──────── (∞) YieldPrediction

Satellite (1) ────── (∞) SatelliteObservation
Imagery (1) ──────── (∞) SatelliteObservation
Imagery (1) ──────── (∞) Diagnosis
```

## Cascade Behaviors

### User Deletion
- Deleting a User cascades to delete all owned Farms
- Farms cascade to delete all Fields
- Fields cascade to delete all related data

### Field Deletion
- Deleting a Field cascades to delete:
  - SensorReadings
  - Weather
  - Diagnoses
  - IrrigationPlans
  - YieldPredictions
  - CropCycles
  - SatelliteObservations
  - Imagery (field_id set to NULL, imagery preserved)

### AIModel Deletion
- Deleting an AIModel sets model_id to NULL in referencing entities

### Satellite Deletion
- Deleting a Satellite sets satellite_id to NULL in SatelliteObservations

### Imagery Deletion
- Deleting Imagery sets imagery_id to NULL in referencing entities

## Common Patterns

### Timestamps
All models include:
- `created_at` - Record creation timestamp (UTC)
- Some models include `updated_at` - Last modification timestamp

### Foreign Keys
- All foreign keys use proper constraints
- CASCADE or SET NULL on delete specified
- Indexed for efficient queries

### JSON Fields
Several models use JSON columns for flexible data:
- `AIModel.parameters` - Hyperparameters
- `AIModel.performance_metrics` - Model metrics
- `Imagery.spectral_bands` - Spectral band data
- `Diagnosis.leaf_boundary_box` - Bounding box coordinates
- `Diagnosis.detected_diseases` - Disease list
- `SensorReading.additional_data` - Custom sensor data
- `Weather.additional_data` - Custom weather data

## Database Migrations

All schema changes are managed through Alembic migrations:
- Migration files: `migrations/versions/`
- Generate migration: `alembic revision --autogenerate -m "description"`
- Apply migration: `alembic upgrade head`
- Rollback: `alembic downgrade -1`

## Model File Locations

All models are located in: `app/models/`

- `base.py` - Base model class
- `user.py` - User model
- `farm.py` - Farm model
- `field.py` - Field model
- `field_boundary.py` - FieldBoundary model (PostGIS)
- `ai_model.py` - AIModel model
- `satellite.py` - Satellite model
- `imagery.py` - Imagery model
- `satellite_observation.py` - SatelliteObservation model
- `diagnosis.py` - Diagnosis model
- `irrigation_plan.py` - IrrigationPlan model
- `yield_prediction.py` - YieldPrediction model
- `crop_cycle.py` - CropCycle model
- `crop_mix_recommendation.py` - CropMixRecommendation model
- `crop_mix_allocation.py` - CropMixAllocation model
- `sensor_reading.py` - SensorReading model
- `weather.py` - Weather model

## Notes

- All models use SQLAlchemy 2.0 with Mapped columns
- Primary keys are auto-incrementing integers
- Foreign keys use proper referential integrity
- Indexes are added for frequently queried columns
- Models follow N-Tier architecture separation
- Use repository pattern for data access
- Use service layer for business logic
