# Satellite Model

## Overview

The `Satellite` model represents remote sensing data sources that provide imagery and observation data for agricultural monitoring. It stores metadata about satellite platforms including operator, launch date, sensor type, resolution, and revisit period.

## File Location

`app/models/satellite.py`

## Table Schema

**Table Name:** `satellites`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique identifier |
| `name` | VARCHAR(100) | UNIQUE, NOT NULL, INDEX | Satellite name (e.g., "Sentinel-2") |
| `operator` | VARCHAR(100) | NULLABLE | Operating organization (ESA, NASA) |
| `launch_date` | DATE | NULLABLE | Launch date of the satellite |
| `sensor_type` | VARCHAR(50) | NULLABLE | Sensor type (optical, SAR) |
| `resolution_m` | FLOAT | NULLABLE | Spatial resolution in meters |
| `revisit_period_days` | FLOAT | NULLABLE | Days between revisits |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'active' | Satellite status |
| `description` | VARCHAR(500) | NULLABLE | Platform description |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Creation timestamp |

## Relationships

- **Has many:** `SatelliteObservation` entities

## Constraints

- **Unique constraint:** Satellite name must be unique

## Indexes

- `name` - Unique indexed for efficient lookup
- `ix_satellites_name_status` - Composite index for active satellite queries

## Usage Examples

### Registering a Satellite

```python
from app.models.satellite import Satellite

satellite = Satellite(
    name="Sentinel-2",
    operator="ESA",
    launch_date="2015-06-23",
    sensor_type="multispectral",
    resolution_m=10.0,
    revisit_period_days=5,
    status="active",
    description="ESA's Sentinel-2 mission for land monitoring"
)
```

### Querying Active Satellites

```python
from app.repositories.satellite_repository import SatelliteRepository

repo = SatelliteRepository(db)
active_satellites = repo.list_active()
```

### Getting Satellite by Name

```python
from app.services.satellite_service import SatelliteService

service = SatelliteService(db)
satellite = service.get_by_name("Sentinel-2")
```

## Related Services

- `SatelliteService` - Satellite registration, resolution, and management

## Related API Endpoints

### Farmer Endpoints (JWT Auth)
- `GET /api/v1/satellites` - List satellites
- `POST /api/v1/satellites` - Create satellite record
- `GET /api/v1/satellites/{id}` - Get satellite details

### Internal Endpoints (API Key Auth)
- `POST /api/satellites` - Create satellite record
- `GET /api/satellites` - List satellite records
- `GET /api/satellites/active` - List active satellites
- `GET /api/satellites/{id}` - Get satellite by ID
- `GET /api/satellites/name/{name}` - Get satellite by name
- `GET /api/satellites/{id}/observations` - Get satellite with observations

## Satellite Examples

### Common Satellites

| Name | Operator | Resolution (m) | Revisit (days) |
|------|----------|----------------|---------------|
| Sentinel-2 | ESA | 10-60 | 5 |
| Landsat-8 | NASA/USGS | 15-30 | 16 |
| PlanetScope | Planet Labs | 3 | 1 |
| MODIS | NASA | 250-1000 | 1-2 |

## Sensor Types

- **optical** - Optical/visible imagery
- **multispectral** - Multiple spectral bands
- **hyperspectral** - Many narrow spectral bands
- **SAR** - Synthetic Aperture Radar
- **thermal** - Thermal infrared
- **LiDAR** - Light Detection and Ranging

## Status Values

- **active** - Currently operational
- **retired** - No longer operational but data available
- **decommissioned** - End of life, no longer functioning
- **planned** - Scheduled for future launch

## Notes

- Satellite names must be unique across the system
- Resolution is ground sample distance in meters
- Revisit period is average time between observations
- Satellites can be registered via internal API
- Satellite observations reference satellites by ID
- Service layer can resolve satellite IDs by name for ingestion
- All timestamp fields use UTC timezone
