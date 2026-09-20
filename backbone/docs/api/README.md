# API Documentation

This directory contains documentation for all API endpoints in the AgriTwin system.

## API Overview

The AgriTwin API is organized into two authentication domains:

1. **Farmer Endpoints (`/api/v1/`)** - JWT Bearer Token Authentication
   - Used by farmers and mobile applications
   - Token obtained via `/api/v1/auth/login`

2. **Internal Module Endpoints (`/api/`)** - API Key Authentication
   - Used by internal internship modules
   - Authenticated via `X-API-Key` header

## API Structure

```
/api/v1/ (Farmer Endpoints - JWT Auth)
├── /auth              - Authentication
├── /farms             - Farm management
├── /fields            - Field management
├── /crop-cycles       - Crop cycles
├── /imagery           - Imagery records
├── /satellites        - Satellite registry
├── /satellite-observations - Satellite data
├── /diagnoses         - Disease diagnoses
├── /irrigation-plans  - Irrigation recommendations
├── /yield-predictions - Yield forecasts
├── /crop-mix-recommendations - Crop optimization
├── /sensor-readings   - IoT sensor data
├── /weather           - Weather data
├── /images            - Image upload/download
└── /events            - Event management

/api/ (Internal Endpoints - API Key Auth)
├── /models            - AI model management
├── /imagery           - Imagery management
├── /satellites        - Satellite management
├── /fields/{id}/     - Field-centric operations
│   ├── /sensor-readings
│   ├── /satellite-observations
│   ├── /diagnoses
│   ├── /irrigation-plans
│   ├── /yield-predictions
│   ├── /crop-mix-recommendations
│   ├── /boundary
│   └── /state
└── /farms/{id}/      - Farm-centric operations
    ├── /fields
    └── /crop-mixes/latest
```

## Authentication

### JWT Bearer Authentication (Farmer Endpoints)

**Obtain Token:**
```bash
POST /api/v1/auth/login
{
  "email": "farmer@example.com",
  "password": "password"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Use Token:**
```bash
GET /api/v1/farms
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### API Key Authentication (Internal Endpoints)

**Use API Key:**
```bash
POST /api/fields/1/sensor-readings
X-API-Key: REDACTED_INTERN_KEY
Content-Type: application/json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "soil_moisture": 45.5
}
```

**Available API Keys:**
- `INTERN_2_API_KEY` - Intern 2 module
- `INTERN_3_API_KEY` - Intern 3 module
- `INTERN_4A_API_KEY` - Intern 4a module
- `INTERN_4B_API_KEY` - Intern 4b module
- `INTERN_5_API_KEY` - Intern 5 module
- `INTERN_7_API_KEY` - Intern 7 module
- `INTERN_8_API_KEY` - Intern 8 module

## Response Format

### Success Response
```json
{
  "id": 1,
  "name": "Field Name",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Error Response
```json
{
  "detail": "Error message"
}
```

### Common HTTP Status Codes

- **200 OK** - Successful GET, PUT, DELETE
- **201 Created** - Successful POST
- **400 Bad Request** - Invalid input
- **401 Unauthorized** - Missing or invalid authentication
- **403 Forbidden** - Insufficient permissions
- **404 Not Found** - Resource not found
- **409 Conflict** - Duplicate or constraint violation
- **422 Unprocessable Entity** - Validation error
- **500 Internal Server Error** - Server error

## API Endpoints

### Authentication Endpoints

#### Register User
- **Endpoint:** `POST /api/v1/auth/register`
- **Auth:** None (public)
- **Body:** `{ "email": "string", "password": "string" }`
- **Response:** User object

#### Login
- **Endpoint:** `POST /api/v1/auth/login`
- **Auth:** None (public)
- **Body:** `{ "email": "string", "password": "string" }`
- **Response:** `{ "access_token": "string", "token_type": "bearer" }`

### Farm Endpoints

#### List Farms
- **Endpoint:** `GET /api/v1/farms`
- **Auth:** JWT Bearer
- **Response:** List of farms

#### Create Farm
- **Endpoint:** `POST /api/v1/farms`
- **Auth:** JWT Bearer
- **Body:** FarmCreate schema
- **Response:** Created farm

#### Get Farm
- **Endpoint:** `GET /api/v1/farms/{id}`
- **Auth:** JWT Bearer
- **Response:** Farm object

#### Update Farm
- **Endpoint:** `PUT /api/v1/farms/{id}`
- **Auth:** JWT Bearer
- **Body:** FarmUpdate schema
- **Response:** Updated farm

#### Delete Farm
- **Endpoint:** `DELETE /api/v1/farms/{id}`
- **Auth:** JWT Bearer
- **Response:** Success message

### Field Endpoints

#### List Fields
- **Endpoint:** `GET /api/v1/fields`
- **Auth:** JWT Bearer
- **Response:** List of fields

#### Create Field
- **Endpoint:** `POST /api/v1/fields`
- **Auth:** JWT Bearer
- **Body:** FieldCreate schema
- **Response:** Created field

#### Get Field
- **Endpoint:** `GET /api/v1/fields/{id}`
- **Auth:** JWT Bearer
- **Response:** Field object

#### Update Field
- **Endpoint:** `PUT /api/v1/fields/{id}`
- **Auth:** JWT Bearer
- **Body:** FieldUpdate schema
- **Response:** Updated field

#### Delete Field
- **Endpoint:** `DELETE /api/v1/fields/{id}`
- **Auth:** JWT Bearer
- **Response:** Success message

### Internal API Endpoints

#### AI Model Management
- **POST /api/models** - Register or get AI model
- **GET /api/models** - List registered models

#### Imagery Management
- **POST /api/imagery** - Create imagery record
- **GET /api/imagery** - List imagery records
- **GET /api/imagery/{id}** - Get imagery by ID
- **GET /api/imagery/field/{field_id}** - List imagery for field

#### Satellite Management
- **POST /api/satellites** - Create satellite record
- **GET /api/satellites** - List satellite records
- **GET /api/satellites/active** - List active satellites
- **GET /api/satellites/{id}** - Get satellite by ID
- **GET /api/satellites/name/{name}** - Get satellite by name

#### Data Ingestion
- **POST /api/fields/{field_id}/sensor-readings** - Ingest sensor data
- **POST /api/fields/{field_id}/satellite-observations** - Ingest satellite data
- **POST /api/fields/{field_id}/diagnoses** - Ingest diagnosis results
- **POST /api/fields/{field_id}/irrigation-plans** - Ingest irrigation plans
- **POST /api/fields/{field_id}/yield-predictions** - Ingest yield predictions
- **POST /api/fields/{field_id}/crop-mix-recommendations** - Ingest crop mix recommendations

#### Field Data Queries
- **GET /api/fields/{field_id}** - Get field details
- **GET /api/fields/{field_id}/boundary** - Get field boundary
- **GET /api/fields/{field_id}/state** - Get aggregate field state
- **GET /api/fields/{field_id}/sensor-readings** - Get sensor history
- **GET /api/fields/{field_id}/satellite-observations** - Get satellite history
- **GET /api/fields/{field_id}/diagnoses** - Get diagnosis history
- **GET /api/fields/{field_id}/irrigation-plans** - Get irrigation history
- **GET /api/fields/{field_id}/yield-predictions** - Get yield history
- **GET /api/fields/{field_id}/crop-mix-recommendations** - Get crop mix history

## Interactive Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI Schema:** http://localhost:8000/api/v1/openapi.json

## Postman Collection

A complete Postman collection is available at:
- **File:** `postman_mock_collection.json`
- **Name:** AgriTwin Complete Mock Collection
- **Modules:** 14
- **Requests:** 39
- **Response Examples:** 43

## API Router Files

All API routers are located in: `app/api/v1/`

- `auth.py` - Authentication endpoints
- `farms.py` - Farm endpoints
- `fields.py` - Field endpoints
- `crop_cycles.py` - Crop cycle endpoints
- `imagery.py` - Imagery endpoints
- `satellites.py` - Satellite endpoints
- `satellite_observations.py` - Satellite observation endpoints
- `diagnoses.py` - Diagnosis endpoints
- `irrigation_plans.py` - Irrigation plan endpoints
- `yield_predictions.py` - Yield prediction endpoints
- `crop_mix_recommendations.py` - Crop mix recommendation endpoints
- `sensor_readings.py` - Sensor reading endpoints
- `weather.py` - Weather endpoints
- `images.py` - Image upload/download endpoints
- `events.py` - Event endpoints

Internal router:
- `internal_router.py` - Internal API endpoints

## Notes

- All timestamps are in UTC
- Use pagination for list endpoints
- Filter by date range where supported
- Authentication required for most endpoints
- Rate limiting should be implemented (currently not present)
- HTTPS should be used in production
