# SensorReading Model

## Overview

The `SensorReading` model represents IoT sensor data collected from fields. It stores soil moisture, temperature, humidity, and other environmental measurements for real-time field monitoring and irrigation decision support.

## File Location

`app/models/sensor_reading.py`

## Table Schema

**Table Name:** `sensor_readings`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique identifier |
| `field_id` | INTEGER | FOREIGN KEY (fields.id), NOT NULL | Field with sensor |
| `timestamp` | TIMESTAMP | NOT NULL | Reading timestamp |
| `soil_moisture_percent` | FLOAT | NULLABLE | Soil moisture percentage |
| `soil_temperature_c` | FLOAT | NULLABLE | Soil temperature (Celsius) |
| `air_temperature_c` | FLOAT | NULLABLE | Air temperature (Celsius) |
| `humidity_percent` | FLOAT | NULLABLE | Air humidity percentage |
| `ph_level` | FLOAT | NULLABLE | Soil pH level |
| `nitrogen_level` | FLOAT | NULLABLE | Nitrogen level (mg/kg) |
| `phosphorus_level` | FLOAT | NULLABLE | Phosphorus level (mg/kg) |
| `potassium_level` | FLOAT | NULLABLE | Potassium level (mg/kg) |
| `additional_data` | JSON | NULLABLE | Custom sensor data |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Record creation timestamp |

## Relationships

- **Belongs to:** `Field` via `field_id` (CASCADE on field deletion)

## Cascade Behavior

- When a Field is deleted, all associated SensorReadings are deleted (CASCADE)

## Usage Examples

### Creating a Sensor Reading

```python
from app.models.sensor_reading import SensorReading
from datetime import datetime

reading = SensorReading(
    field_id=1,
    timestamp=datetime.utcnow(),
    soil_moisture_percent=45.5,
    soil_temperature_c=18.3,
    air_temperature_c=22.1,
    humidity_percent=65.0,
    ph_level=6.8,
    nitrogen_level=25.0,
    phosphorus_level=15.0,
    potassium_level=30.0
)
```

## Related Services

- `SensorService` - Sensor reading management and queries

## Related API Endpoints

### Farmer Endpoints (JWT Auth)
- `GET /api/v1/sensor-readings` - List sensor readings
- `GET /api/v1/sensor-readings/{id}` - Get reading details

### Internal Endpoints (API Key Auth)
- `POST /api/fields/{field_id}/sensor-readings` - Ingest sensor data
- `GET /api/fields/{field_id}/sensor-readings` - Get field sensor readings

## Sensor Types

### Soil Sensors
- **Soil Moisture** - Volumetric water content (%)
- **Soil Temperature** - Temperature at root zone (°C)
- **Soil pH** - Acidity/alkalinity (0-14 scale)
- **NPK Sensors** - Nitrogen, Phosphorus, Potassium levels

### Environmental Sensors
- **Air Temperature** - Ambient temperature (°C)
- **Humidity** - Relative humidity (%)
- **Wind Speed** - Wind velocity (km/h)
- **Solar Radiation** - Sunlight intensity (W/m²)

## Optimal Ranges

### Soil Moisture
- **Sandy soil:** 50-60%
- **Loamy soil:** 60-70%
- **Clay soil:** 70-80%

### Soil pH
- **Most crops:** 6.0-7.0
- **Acid-loving:** 4.5-5.5 (blueberries, potatoes)
- **Alkaline-tolerant:** 7.0-8.0 (asparagus, beans)

### Soil Temperature
- **Germination:** 15-25°C for most crops
- **Optimal growth:** 20-30°C
- **Stress:** >35°C or <10°C

### NPK Levels (mg/kg)
- **Nitrogen:** 20-40 (adequate)
- **Phosphorus:** 10-30 (adequate)
- **Potassium:** 15-35 (adequate)

## Additional Data Format

JSON field for custom sensor data:
```json
{
  "wind_speed_kmh": 12.5,
  "solar_radiation_wm2": 850,
  "leaf_wetness": true,
  "battery_level": 85
}
```

## Data Frequency

Recommended reading intervals:
- **Soil moisture:** Every 1-4 hours
- **Temperature:** Every 30-60 minutes
- **NPK levels:** Daily or weekly
- **pH level:** Weekly or monthly

## Notes

- Sensor readings enable real-time monitoring
- High-frequency data can be aggregated
- Used in irrigation planning decisions
- Historical data enables trend analysis
- All timestamp fields use UTC timezone
- Sensor calibration important for accuracy
- Data quality affects model predictions
