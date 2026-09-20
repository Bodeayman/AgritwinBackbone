# IrrigationPlan Model

## Overview

The `IrrigationPlan` model represents AI-generated irrigation recommendations for fields. It stores water usage recommendations, scheduling information, and confidence scores to optimize irrigation and water conservation.

## File Location

`app/models/irrigation_plan.py`

## Table Schema

**Table Name:** `irrigation_plans`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique identifier |
| `field_id` | INTEGER | FOREIGN KEY (fields.id), NOT NULL | Target field |
| `model_id` | INTEGER | FOREIGN KEY (ai_models.id), NULLABLE | AI model used |
| `plan_date` | DATE | NOT NULL | Date of plan |
| `water_amount_mm` | FLOAT | NULLABLE | Recommended water amount (mm) |
| `irrigation_duration_hours` | FLOAT | NULLABLE | Irrigation duration |
| `start_time` | TIME | NULLABLE | Recommended start time |
| `frequency_days` | INTEGER | NULLABLE | Frequency in days |
| `soil_moisture_target` | FLOAT | NULLABLE | Target soil moisture % |
| `estimated_cost` | FLOAT | NULLABLE | Estimated cost (currency) |
| `confidence` | FLOAT | NULLABLE | Model confidence (0.0-1.0) |
| `reasoning` | TEXT | NULLABLE | AI reasoning explanation |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Record creation timestamp |

## Relationships

- **Belongs to:** `Field` via `field_id` (CASCADE on field deletion)
- **References:** `AIModel` via `model_id` (SET NULL on model deletion)

## Cascade Behavior

- When a Field is deleted, all associated IrrigationPlans are deleted (CASCADE)
- When an AIModel is deleted, `model_id` is set to NULL

## Usage Examples

### Creating an Irrigation Plan

```python
from app.models.irrigation_plan import IrrigationPlan
from datetime import date, time

plan = IrrigationPlan(
    field_id=1,
    model_id=5,
    plan_date=date(2024, 1, 15),
    water_amount_mm=25.5,
    irrigation_duration_hours=2.5,
    start_time=time(6, 0),
    frequency_days=3,
    soil_moisture_target=65.0,
    estimated_cost=12.50,
    confidence=0.85,
    reasoning="Soil moisture below optimal level based on sensor data and weather forecast"
)
```

## Related Services

- `IrrigationPlanService` - Irrigation plan management and queries

## Related API Endpoints

### Farmer Endpoints (JWT Auth)
- `GET /api/v1/irrigation-plans` - List irrigation plans
- `GET /api/v1/irrigation-plans/{id}` - Get plan details

### Internal Endpoints (API Key Auth)
- `POST /api/fields/{field_id}/irrigation-plans` - Ingest irrigation plan
- `GET /api/fields/{field_id}/irrigation-plans` - Get field irrigation plans

## Water Amount Guidelines

**By Crop Type:**
- **Wheat:** 300-500 mm per season
- **Maize:** 400-600 mm per season
- **Rice:** 1000-1500 mm per season
- **Soybeans:** 400-600 mm per season

**By Growth Stage:**
- **Vegetative:** Lower water requirement
- **Flowering:** Peak water requirement
- **Maturation:** Decreasing water requirement

## Soil Moisture Targets

- **Sandy soil:** 50-60%
- **Loamy soil:** 60-70%
- **Clay soil:** 70-80%

## Irrigation Scheduling

**Best Practices:**
- Irrigate early morning or late evening to reduce evaporation
- Avoid irrigation during windy conditions
- Consider weather forecasts (skip if rain expected)
- Monitor soil moisture sensors for real-time adjustment

## Cost Estimation

Factors affecting irrigation cost:
- Water source (municipal, well, recycled)
- Pump energy costs
- Labor costs
- Equipment maintenance
- Water tariffs

## Notes

- Plans are historical records for analysis
- Multiple plans can exist per field over time
- Confidence scores indicate model reliability
- Plans should be validated with real-time sensor data
- All timestamp fields use UTC timezone
- Used in conjunction with weather data for optimization
