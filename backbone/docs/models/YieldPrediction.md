# YieldPrediction Model

## Overview

The `YieldPrediction` model represents AI-generated yield forecasts for fields. It stores predicted yield values, confidence scores, and factors affecting yield to help farmers plan harvest and marketing strategies.

## File Location

`app/models/yield_prediction.py`

## Table Schema

**Table Name:** `yield_predictions`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique identifier |
| `field_id` | INTEGER | FOREIGN KEY (fields.id), NOT NULL | Target field |
| `model_id` | INTEGER | FOREIGN KEY (ai_models.id), NULLABLE | AI model used |
| `prediction_date` | DATE | NOT NULL | Date of prediction |
| `predicted_yield_tons_per_hectare` | FLOAT | NULLABLE | Predicted yield (tons/ha) |
| `confidence` | FLOAT | NULLABLE | Model confidence (0.0-1.0) |
| `crop_type` | VARCHAR(100) | NULLABLE | Type of crop |
| `factors` | JSON | NULLABLE | Influencing factors |
| `risk_assessment` | TEXT | NULLABLE | Risk analysis |
| `harvest_date_estimate` | DATE | NULLABLE | Estimated harvest date |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Record creation timestamp |

## Relationships

- **Belongs to:** `Field` via `field_id` (CASCADE on field deletion)
- **References:** `AIModel` via `model_id` (SET NULL on model deletion)

## Cascade Behavior

- When a Field is deleted, all associated YieldPredictions are deleted (CASCADE)
- When an AIModel is deleted, `model_id` is set to NULL

## Usage Examples

### Creating a Yield Prediction

```python
from app.models.yield_prediction import YieldPrediction
from datetime import date

prediction = YieldPrediction(
    field_id=1,
    model_id=5,
    prediction_date=date(2024, 1, 15),
    predicted_yield_tons_per_hectare=8.5,
    confidence=0.82,
    crop_type="Maize",
    factors={
        "weather_conditions": "favorable",
        "soil_quality": "high",
        "pest_pressure": "low",
        "fertilizer_application": "adequate"
    },
    risk_assessment="Low risk: favorable weather conditions expected",
    harvest_date_estimate=date(2024, 9, 15)
)
```

## Related Services

- `YieldPredictionService` - Yield prediction management and queries

## Related API Endpoints

### Farmer Endpoints (JWT Auth)
- `GET /api/v1/yield-predictions` - List yield predictions
- `GET /api/v1/yield-predictions/{id}` - Get prediction details

### Internal Endpoints (API Key Auth)
- `POST /api/fields/{field_id}/yield-predictions` - Ingest yield prediction
- `GET /api/fields/{field_id}/yield-predictions` - Get field yield predictions

## Typical Yield Ranges (tons per hectare)

**By Crop:**
- **Wheat:** 3-7 t/ha
- **Maize:** 5-12 t/ha
- **Rice:** 4-9 t/ha
- **Soybeans:** 2-4 t/ha
- **Barley:** 3-6 t/ha

**Factors affecting yield:**
- Climate and weather
- Soil quality and fertility
- Water availability
- Pest and disease pressure
- Crop variety
- Management practices

## Factors JSON Format

```json
{
  "weather_conditions": "favorable",
  "soil_quality": "high",
  "pest_pressure": "low",
  "fertilizer_application": "adequate",
  "irrigation_status": "sufficient",
  "planting_density": "optimal"
}
```

## Risk Assessment Levels

- **Low risk** - Conditions favorable, high confidence
- **Moderate risk** - Some uncertainty, moderate confidence
- **High risk** - Unfavorable conditions, low confidence
- **Very high risk** - Significant threats, very low confidence

## Confidence Interpretation

- **0.9-1.0** - Very high confidence
- **0.7-0.9** - High confidence
- **0.5-0.7** - Moderate confidence
- **0.3-0.5** - Low confidence
- **0.0-0.3** - Very low confidence

## Notes

- Predictions are historical records for trend analysis
- Multiple predictions can exist per field over time
- Factors help explain prediction rationale
- Risk assessment aids decision-making
- All timestamp fields use UTC timezone
- Used in conjunction with satellite and sensor data
- Predictions should be validated against actual harvest data
