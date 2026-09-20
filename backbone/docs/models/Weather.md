# Weather Model

## Overview

The `Weather` model represents weather measurements for fields. It stores temperature, precipitation, humidity, wind, and other weather data to support agricultural decision-making and yield prediction.

## File Location

`app/models/weather.py`

## Table Schema

**Table Name:** `weather`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique identifier |
| `field_id` | INTEGER | FOREIGN KEY (fields.id), NOT NULL | Field location |
| `timestamp` | TIMESTAMP | NOT NULL | Observation timestamp |
| `temperature_c` | FLOAT | NULLABLE | Temperature (Celsius) |
| `humidity_percent` | FLOAT | NULLABLE | Relative humidity (%) |
| `precipitation_mm` | FLOAT | NULLABLE | Precipitation (mm) |
| `wind_speed_kmh` | FLOAT | NULLABLE | Wind speed (km/h) |
| `wind_direction_degrees` | FLOAT | NULLABLE | Wind direction (degrees) |
| `pressure_hpa` | FLOAT | NULLABLE | Atmospheric pressure (hPa) |
| `additional_data` | JSON | NULLABLE | Custom weather data |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Record creation timestamp |

## Relationships

- **Belongs to:** `Field` via `field_id` (CASCADE on field deletion)

## Cascade Behavior

- When a Field is deleted, all associated Weather records are deleted (CASCADE)

## Usage Examples

### Creating a Weather Record

```python
from app.models.weather import Weather
from datetime import datetime

weather = Weather(
    field_id=1,
    timestamp=datetime.utcnow(),
    temperature_c=25.5,
    humidity_percent=65.0,
    precipitation_mm=0.0,
    wind_speed_kmh=12.3,
    wind_direction_degrees=180,
    pressure_hpa=1013.25
)
```

## Related Services

- `WeatherService` - Weather data management and queries

## Related API Endpoints

### Farmer Endpoints (JWT Auth)
- `GET /api/v1/weather` - List weather data
- `GET /api/v1/weather/{id}` - Get weather details

### Internal Endpoints (API Key Auth)
- Weather data typically ingested via external weather APIs
- Historical weather data accessible via field queries

## Weather Data Sources

- **Weather stations** - On-site weather stations
- **Weather APIs** - OpenWeatherMap, WeatherAPI, etc.
- **Satellite data** - Meteorological satellites
- **Government sources** - National weather services

## Temperature Guidelines

### Crop-Specific Temperature Ranges

| Crop | Optimal (°C) | Stress High (°C) | Stress Low (°C) |
|------|--------------|-----------------|----------------|
| Wheat | 15-25 | >30 | <5 |
| Maize | 20-30 | >35 | <10 |
| Rice | 25-35 | >40 | <15 |
| Soybeans | 20-30 | >35 | <10 |

### Growing Degree Days (GDD)

Used to predict crop development:
- Base temperature varies by crop
- Accumulated GDD predicts growth stage
- Used for harvest timing

## Precipitation Guidelines

### Monthly Requirements (mm)

| Crop | Low | Optimal | High |
|------|-----|---------|------|
| Wheat | 25-50 | 50-100 | 100-150 |
| Maize | 50-100 | 100-200 | 200-300 |
| Rice | 100-200 | 200-400 | 400-600 |
| Soybeans | 50-100 | 100-200 | 200-300 |

## Wind Direction

- **0° / 360°** - North
- **90°** - East
- **180°** - South
- **270°** - West

## Atmospheric Pressure

- **Normal:** 1013.25 hPa (sea level)
- **High pressure:** >1020 hPa (fair weather)
- **Low pressure:** <1000 hPA (stormy weather)

## Additional Data Format

JSON field for custom weather data:
```json
{
  "uv_index": 7,
  "visibility_km": 10,
  "cloud_cover_percent": 30,
  "dew_point_c": 18.5,
  "solar_radiation_wm2": 850
}
```

## Notes

- Weather data enables yield prediction
- Historical weather aids trend analysis
- Used in irrigation planning decisions
- Extreme weather events should be flagged
- All timestamp fields use UTC timezone
- Data quality affects model accuracy
- Consider data interpolation for missing readings
