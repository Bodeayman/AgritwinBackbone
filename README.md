# AgriTwin Backend

Agricultural Digital Twin Backend API with real-time field monitoring, satellite imagery analysis, disease diagnosis, irrigation planning, and yield prediction capabilities.

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Directory Structure](#directory-structure)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Authentication](#authentication)
- [Database](#database)
- [Testing](#testing)
- [Docker Deployment](#docker-deployment)
- [Development Workflow](#development-workflow)
- [Security Considerations](#security-considerations)

## Project Overview

AgriTwin Backend is a FastAPI-based agricultural management system that provides:

- **Farm and Field Management**: Create and manage farms with geo-located fields using PostGIS
- **Satellite Imagery Integration**: Ingest and process satellite observations with multi-spectral data
- **AI/ML Model Integration**: Register and track AI models for diagnoses, irrigation planning, and yield predictions
- **Disease and Pest Diagnosis**: Multi-disease detection with confidence scores and treatment suggestions
- **Irrigation Planning**: AI-driven irrigation recommendations based on field conditions
- **Yield Prediction**: Crop yield forecasting using historical and real-time data
- **Crop Mix Optimization**: Optimal crop combination recommendations for fields
- **Sensor Data Ingestion**: IoT sensor readings for soil moisture, temperature, and environmental monitoring
- **Weather Integration**: Weather data storage and historical analysis
- **Dual Authentication**: JWT Bearer tokens for farmers, API keys for internal internship modules

## Architecture

### N-Tier Architecture

The application follows a layered N-Tier architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                   Presentation Layer                         │
│  (FastAPI Routers, API Endpoints, Validation, Auth)        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                          │
│  (Business Logic, Services, Orchestrations)                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Domain Layer                               │
│  (Models, Schemas, Domain Entities)                         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                       │
│  (Repositories, Database, Storage, External Services)       │
└─────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

**Presentation Layer** (`app/api/`)
- HTTP request/response handling
- Input validation using Pydantic schemas
- Authentication and authorization
- Dependency injection for services
- OpenAPI documentation generation

**Application Layer** (`app/services/`)
- Business logic implementation
- Service orchestration
- Model resolution (AI models, satellites, imagery)
- Transaction management
- Data transformation

**Domain Layer** (`app/models/`, `app/schemas/`)
- Entity definitions (SQLAlchemy models)
- Domain rules and constraints
- Pydantic schemas for validation
- Relationship definitions

**Infrastructure Layer** (`app/repositories/`, `app/core/`)
- Database access patterns (Repository pattern)
- External service integration (MinIO, RabbitMQ)
- Configuration management
- Security utilities

### Current Architecture Assessment

**Strengths:**
- Clear separation between API, services, repositories, and models
- Repository pattern for data access abstraction
- Dependency injection for testability
- Modular router organization
- Dual authentication system for different use cases

**Areas for Improvement:**
- Services directly access database session through repositories; consider explicit transaction boundaries
- Some business logic exists in routers (e.g., field existence checks) - consider moving to services
- Error handling is inconsistent across endpoints
- No explicit domain services for complex business rules
- No caching layer for frequently accessed data
- No message queue consumer implementation (RabbitMQ configured but not used)

**Recommendation:** The current architecture is suitable for a modular monolith. Continue refining layer boundaries before considering microservices decomposition.

## Technology Stack

### Core Framework
- **FastAPI 0.111+**: Modern, fast web framework for building APIs
- **Python 3.11+**: Core runtime language
- **Uvicorn**: ASGI server for production deployment

### Database & ORM
- **PostgreSQL 15**: Primary relational database
- **PostGIS 3.4**: Spatial extensions for geo-location data
- **SQLAlchemy 2.0+**: Python SQL toolkit and ORM
- **GeoAlchemy2**: Spatial extension for SQLAlchemy
- **Alembic**: Database migration tool
- **psycopg2**: PostgreSQL adapter for Python

### Storage & Messaging
- **MinIO**: S3-compatible object storage for images and files
- **RabbitMQ**: Message broker (configured, not actively used)

### Authentication & Security
- **python-jose**: JWT token generation and validation
- **passlib**: Password hashing with bcrypt
- **Pydantic**: Data validation and settings management

### Testing
- **pytest**: Testing framework
- **httpx**: Async HTTP client for testing
- **TestClient**: FastAPI test client

### DevOps
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **GitHub Actions**: CI/CD pipeline

## Directory Structure

```
AgriTwin/
├── app/
│   ├── api/
│   │   ├── deps.py              # Dependency injection providers
│   │   ├── internal_router.py   # Internal API endpoints (API Key auth)
│   │   ├── router.py            # Public API router (JWT auth)
│   │   └── v1/                  # API v1 endpoint modules
│   │       ├── auth.py
│   │       ├── farms.py
│   │       ├── fields.py
│   │       ├── satellite_observations.py
│   │       ├── diagnoses.py
│   │       ├── irrigation_plans.py
│   │       ├── yield_predictions.py
│   │       ├── crop_mix_recommendations.py
│   │       ├── imagery.py
│   │       ├── satellites.py
│   │       ├── sensor_readings.py
│   │       ├── weather.py
│   │       ├── crop_cycles.py
│   │       ├── images.py
│   │       └── events.py
│   ├── core/
│   │   ├── config.py            # Application settings
│   │   ├── database.py          # Database engine and session
│   │   ├── security.py          # JWT and password utilities
│   │   ├── storage.py           # MinIO S3 storage service
│   │   ├── local_storage.py     # Local disk storage fallback
│   │   └── validation.py        # Custom validators
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── farm.py
│   │   ├── field.py
│   │   ├── field_boundary.py
│   │   ├── crop_cycle.py
│   │   ├── satellite.py
│   │   ├── imagery.py
│   │   ├── satellite_observation.py
│   │   ├── ai_model.py
│   │   ├── diagnosis.py
│   │   ├── irrigation_plan.py
│   │   ├── yield_prediction.py
│   │   ├── crop_mix_recommendation.py
│   │   ├── crop_mix_allocation.py
│   │   ├── sensor_reading.py
│   │   └── weather.py
│   ├── repositories/            # Data access layer
│   │   ├── base.py
│   │   ├── farm_repository.py
│   │   ├── field_repository.py
│   │   └── ... (per-entity repositories)
│   ├── schemas/                 # Pydantic schemas
│   │   ├── auth.py
│   │   ├── farm.py
│   │   ├── field.py
│   │   └── ... (per-entity schemas)
│   ├── services/                # Business logic layer
│   │   ├── auth_service.py
│   │   ├── farm_service.py
│   │   ├── field_service.py
│   │   └── ... (per-entity services)
│   └── main.py                  # FastAPI application entry point
├── migrations/
│   ├── versions/                # Alembic migration files
│   ├── env.py                   # Migration environment
│   └── README
├── tests/
│   ├── conftest.py              # Pytest fixtures
│   ├── test_api.py
│   ├── test_auth.py
│   ├── test_farms.py
│   ├── test_fields.py
│   ├── test_models_and_repositories.py
│   ├── test_services.py
│   ├── test_internal_api.py
│   └── test_local_storage.py
├── mock_server/
│   ├── server.py                # Mock API server for testing
│   └── data/
│       └── scenarios/
│           └── default/         # Mock data JSON files
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI/CD
├── .env                         # Local environment variables (not committed)
├── .env.example                # Environment template
├── .gitignore
├── .dockerignore
├── alembic.ini                  # Alembic configuration
├── docker-compose.yml          # Docker orchestration
├── docker-compose.example.yml  # Safe template with placeholders
├── Dockerfile                  # Application container image
├── requirements.txt             # Python dependencies
├── postman_mock_collection.json # Postman API collection
└── README.md                   # This file
```

## Quick Start

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 15 with PostGIS extension
- Docker and Docker Compose (optional, for containerized setup)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Bodeayman/AgritwinBackbone.git
   cd AgriTwin
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and settings
   ```

5. **Start PostgreSQL with PostGIS**
   ```bash
   docker compose up -d db
   ```

6. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

7. **Start the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

8. **Access API documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Docker Compose Setup

1. **Start all services**
   ```bash
   docker compose up -d
   ```

2. **Run migrations inside container**
   ```bash
   docker compose exec web alembic upgrade head
   ```

3. **View logs**
   ```bash
   docker compose logs -f web
   ```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PROJECT_NAME` | Application name | AgriTwin Backend | No |
| `API_V1_STR` | API v1 prefix | /api/v1 | No |
| `DATABASE_URL` | PostgreSQL connection string | - | Yes |
| `JWT_SECRET_KEY` | JWT signing secret | (weak default) | Yes |
| `JWT_ALGORITHM` | JWT algorithm | HS256 | No |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry time | 10080 (7 days) | No |
| `MINIO_ENDPOINT` | MinIO server address | localhost:9000 | Yes |
| `MINIO_ACCESS_KEY` | MinIO access key | minioadmin | Yes |
| `MINIO_SECRET_KEY` | MinIO secret key | minioadminpassword | Yes |
| `MINIO_SECURE` | Use HTTPS for MinIO | False | No |
| `MINIO_BUCKET_NAME` | Default bucket name | agritwin-bucket | Yes |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins | * | No |
| `INTERN_2_API_KEY` through `INTERN_8_API_KEY` | Internal module API keys | (weak defaults) | Yes |

### Configuration Files

- **`.env`**: Local development environment (not committed)
- **`.env.example`**: Template with safe defaults
- **`app/core/config.py`**: Pydantic settings class
- **`alembic.ini`**: Database migration configuration

## API Documentation

### API Endpoints

The API is organized into two main authentication domains:

#### 1. Farmer Endpoints (`/api/v1/`) - JWT Bearer Authentication

| Module | Endpoints | Description |
|--------|-----------|-------------|
| Auth | `POST /api/v1/auth/login`, `POST /api/v1/auth/register` | User authentication |
| Farms | `GET/POST /api/v1/farms`, `GET/PUT/DELETE /api/v1/farms/{id}` | Farm management |
| Fields | `GET/POST /api/v1/fields`, `GET/PUT/DELETE /api/v1/fields/{id}` | Field management |
| Crop Cycles | `GET/POST /api/v1/crop-cycles` | Crop planting cycles |
| Satellite Observations | `GET /api/v1/satellite-observations` | Satellite data queries |
| Diagnoses | `GET /api/v1/diagnoses` | Disease diagnosis history |
| Irrigation Plans | `GET /api/v1/irrigation-plans` | Irrigation recommendations |
| Yield Predictions | `GET /api/v1/yield-predictions` | Yield forecasts |
| Crop Mix Recommendations | `GET /api/v1/crop-mix-recommendations` | Crop optimization |
| Sensor Readings | `GET /api/v1/sensor-readings` | IoT sensor data |
| Weather | `GET /api/v1/weather` | Weather data |
| Imagery | `GET/POST /api/v1/imagery` | Image metadata |
| Satellites | `GET/POST /api/v1/satellites` | Satellite registry |

#### 2. Internal Module Endpoints (`/api/`) - API Key Authentication

| Module | Endpoints | Description |
|--------|-----------|-------------|
| AI Models | `POST/GET /api/models` | Register/list AI models |
| Imagery | `POST/GET /api/imagery` | Create/list imagery records |
| Satellites | `POST/GET /api/satellites` | Create/list satellites |
| Ingestion | `POST /api/fields/{id}/sensor-readings` | Ingest sensor data |
| Ingestion | `POST /api/fields/{id}/satellite-observations` | Ingest satellite data |
| Ingestion | `POST /api/fields/{id}/diagnoses` | Ingest diagnosis results |
| Ingestion | `POST /api/fields/{id}/irrigation-plans` | Ingest irrigation plans |
| Ingestion | `POST /api/fields/{id}/yield-predictions` | Ingest yield predictions |
| Ingestion | `POST /api/fields/{id}/crop-mix-recommendations` | Ingest crop mix recommendations |
| Read | `GET /api/fields/{id}` | Get field details |
| Read | `GET /api/fields/{id}/state` | Get aggregate field state |
| Read | `GET /api/fields/{id}/sensor-readings` | Get sensor history |
| Read | `GET /api/fields/{id}/satellite-observations` | Get satellite history |
| Read | `GET /api/fields/{id}/diagnoses` | Get diagnosis history |
| Read | `GET /api/fields/{id}/irrigation-plans` | Get irrigation history |
| Read | `GET /api/fields/{id}/yield-predictions` | Get yield history |
| Read | `GET /api/fields/{id}/crop-mix-recommendations` | Get crop mix history |

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/api/v1/openapi.json

### Postman Collection

A complete Postman mock collection is available at `postman_mock_collection.json` with 14 modules and 39 endpoints.

## Authentication

### JWT Bearer Authentication (Farmer Endpoints)

1. **Register a user**
   ```bash
   POST /api/v1/auth/register
   {
     "email": "farmer@example.com",
     "password": "securepassword"
   }
   ```

2. **Login to get JWT token**
   ```bash
   POST /api/v1/auth/login
   {
     "email": "farmer@example.com",
     "password": "securepassword"
   }
   ```

3. **Use token in requests**
   ```bash
   GET /api/v1/farms
   Authorization: Bearer <jwt_token>
   ```

### API Key Authentication (Internal Modules)

Internal internship modules authenticate using `X-API-Key` header:

```bash
POST /api/fields/1/sensor-readings
X-API-Key: secret-intern-4a-key
Content-Type: application/json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "soil_moisture": 45.5,
  "temperature": 22.3
}
```

Available API keys (configured in `app/core/config.py`):
- `INTERN_2_API_KEY` through `INTERN_8_API_KEY`

## Database

### Schema Overview

**Core Entities:**
- `users`: Farmer accounts
- `farms`: Agricultural farms
- `fields`: Geo-located fields within farms
- `field_boundaries`: Polygon geometries for fields (PostGIS)

**AI & Satellite:**
- `ai_models`: Registered AI/ML models with versioning
- `satellites`: Satellite platforms
- `imagery`: Image/observation metadata
- `satellite_observations`: Satellite data linked to fields

**Monitoring & Analysis:**
- `sensor_readings`: IoT sensor data
- `weather`: Weather measurements
- `diagnoses`: Disease/pest diagnoses with detailed fields
- `irrigation_plans`: Irrigation recommendations
- `yield_predictions`: Yield forecasts
- `crop_mix_recommendations`: Crop optimization recommendations

**Crop Management:**
- `crop_cycles`: Planting/harvest cycles
- `crop_mix_recommendations`: Optimized crop allocations
- `crop_mix_allocations`: Field-specific crop assignments

### Foreign Key Relationships

All field-related entities reference `fields.id` with `ON DELETE CASCADE`:
- `sensor_readings.field_id`
- `weather.field_id`
- `diagnoses.field_id`
- `irrigation_plans.field_id`
- `yield_predictions.field_id`
- `crop_cycles.field_id`
- `crop_mix_recommendations.field_id`
- `satellite_observations.field_id`
- `imagery.field_id`

AI model references:
- `diagnoses.model_id`, `irrigation_plans.model_id`, `yield_predictions.model_id`, `crop_mix_recommendations.model_id` → `ai_models.id` (SET NULL on delete)

### Migrations

Database schema changes are managed through Alembic:

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

### Connection Pooling

Database connection pooling is configured in `app/core/database.py`:
- `pool_pre_ping=True`: Validates connections before use
- Default pool size: SQLAlchemy defaults (5 connections)
- Consider increasing for high-traffic deployments

## Testing

### Test Suite

The project includes comprehensive tests:
- `test_api.py`: API endpoint tests
- `test_auth.py`: Authentication tests
- `test_farms.py`: Farm entity tests
- `test_fields.py`: Field entity tests
- `test_models_and_repositories.py`: ORM and repository tests
- `test_services.py`: Business logic tests
- `test_internal_api.py`: Internal API tests
- `test_local_storage.py`: Storage tests

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v
```

### Test Database

Tests use an isolated `agritwin_test` database (configured in `tests/conftest.py`). The live `agritwin` database is never touched during testing.

### Test Fixtures

- `db_session`: Provides transactional test database session
- `mock_storage`: Mocks MinIO storage service
- `client`: FastAPI TestClient with overridden dependencies

## Docker Deployment

### Building the Image

```bash
docker build -t agritwin-backend:latest .
```

### Using Docker Compose

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f web

# Run migrations
docker compose exec web alembic upgrade head
```

### Production Considerations

- Use environment-specific `docker-compose.yml` files
- Configure proper volume mounts for data persistence
- Use secrets management for sensitive configuration
- Enable health checks for all services
- Configure resource limits (CPU, memory)
- Use external managed services (PostgreSQL, MinIO) in production

## Development Workflow

### Git Workflow

1. **Branch Strategy**
   - `master`: Main production branch
   - Feature branches: `feature/<description>`
   - Bugfix branches: `bugfix/<description>`

2. **Commit Guidelines**
   - Use conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`
   - Keep commits focused and atomic
   - Include ticket references if applicable

3. **Pull Request Process**
   - Create PR from feature branch to `master`
   - Ensure all tests pass
   - Request code review
   - Address review feedback
   - Merge after approval

### Database Changes

1. **Modify models** in `app/models/`
2. **Generate migration**: `alembic revision --autogenerate -m "description"`
3. **Review migration** in `migrations/versions/`
4. **Test migration** on local database
5. **Commit migration file** with model changes
6. **Apply migration** in all environments

### Testing Before Commit

```bash
# Run full test suite
pytest

# Check code style (if configured)
black app tests
ruff check app tests

# Verify API documentation
# Start server and visit /docs
```

## Security Considerations

### Implemented Security Measures

- **Password Hashing**: Uses pbkdf2_sha256 via passlib
- **JWT Authentication**: Token-based authentication for farmers
- **API Key Authentication**: Separate auth for internal modules
- **CORS Configuration**: Configurable allowed origins
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **Input Validation**: Pydantic schemas on all endpoints

### Security Recommendations (Critical)

1. **Change Default Secrets**
   - `JWT_SECRET_KEY` in config.py is weak
   - All `INTERN_*_API_KEY` values are weak defaults
   - `MINIO_SECRET_KEY` should be changed from default
   - Database password in docker-compose.yml should use environment variables

2. **Environment Variable Protection**
   - `.env` file is correctly excluded by `.gitignore`
   - Never commit `.env` files
   - Use secrets management in production (e.g., AWS Secrets Manager, HashiCorp Vault)

3. **Database Security**
   - `alembic.ini` contains database credentials in plain text - should use environment variables
   - Consider using connection pooling with SSL
   - Implement database user with least privileges

4. **API Security**
   - Implement rate limiting
   - Add request logging and monitoring
   - Consider API versioning strategy
   - Implement request size limits
   - Add input sanitization for file uploads

5. **Dependencies**
   - Regularly update dependencies: `pip install --upgrade -r requirements.txt`
   - Run security audits: `pip-audit` or `safety check`
   - Pin dependency versions in production

6. **HTTPS/TLS**
   - Enable HTTPS in production
   - Configure proper SSL certificates
   - Force HTTPS redirects
   - Use secure cookie flags

### Secrets Found in Tracked Files

The following files contain hardcoded credentials that should be moved to environment variables:

- `app/core/config.py`: Default JWT secret and API keys
- `alembic.ini`: Database connection string with credentials
- `docker-compose.yml`: Hardcoded database and MinIO credentials

Use `docker-compose.example.yml` as a template with placeholders instead.

## Architecture Evolution Roadmap

### Recommended Improvements

**Critical Priority:**
1. Move all secrets to environment variables
2. Implement proper secrets management
3. Add rate limiting and request throttling
4. Implement structured logging
5. Add monitoring and alerting

**High Priority:**
6. Add caching layer (Redis) for frequently accessed data
7. Implement RabbitMQ consumers for async processing
8. Add API response caching headers
9. Implement health check endpoints
10. Add comprehensive error handling middleware

**Medium Priority:**
11. Add API request/response logging
12. Implement distributed tracing
13. Add performance monitoring (APM)
14. Implement circuit breakers for external services
15. Add database query optimization and indexing

**Low Priority:**
16. Consider gRPC for internal service communication
17. Implement event sourcing for audit trails
18. Add GraphQL layer for flexible queries
19. Implement API gateway pattern
20. Consider microservices decomposition when justified

## Multi-Server Architecture Strategy

### Current State: Modular Monolith

The application is currently a **modular monolith** with clear layer separation. This is the appropriate architecture for the current scale and team size.

### Scaling Strategy: Horizontal Scaling

**Recommended approach before microservices:**

1. **Load Balancer**
   - Use Nginx, HAProxy, or cloud load balancer
   - Distribute traffic across multiple backend instances
   - Configure health checks and automatic failover

2. **Multiple Backend Instances**
   - Deploy 2-4 instances of the FastAPI application
   - Use container orchestration (Kubernetes, Docker Swarm)
   - Ensure stateless application design

3. **Shared Database**
   - Single PostgreSQL instance with connection pooling
   - Consider read replicas for read-heavy workloads
   - Use PgBouncer for connection pooling

4. **Shared Storage**
   - Single MinIO instance or cloud S3
   - All instances share the same storage backend
   - Implement CDN for static assets

5. **Caching Layer**
   - Add Redis for:
     - Session storage (if using session-based auth)
     - API response caching
     - Rate limiting
     - Distributed locking

6. **Message Queue**
   - RabbitMQ for:
     - Async task processing (image analysis, model inference)
     - Event-driven architecture
     - Decoupling components

### When to Consider Microservices

**Consider splitting into microservices when:**
- Team size exceeds 10-15 developers
- Different components have different scaling requirements
- Different components have different deployment frequencies
- Specific components require different technology stacks
- Independent teams need independent deployment cycles

**Potential microservice boundaries:**
- Image Processing Service (CPU-intensive)
- AI Model Inference Service (GPU-dependent)
- Satellite Data Ingestion Service (high-throughput)
- Notification Service (external integrations)

**Do NOT split prematurely:**
- Microservices add operational complexity
- Network latency and failure modes
- Distributed transaction challenges
- Testing and debugging complexity

### Service Communication

**Current: REST over HTTP**
- Simple, well-understood
- Good for public APIs
- Built-in JSON serialization

**Future options:**
- **gRPC**: For internal service-to-service communication (high performance, strong typing)
- **Message Queues**: For async, event-driven communication
- **GraphQL**: For flexible client queries (consider as API layer, not backend replacement)

### Deployment Architecture

```
                    ┌─────────────┐
                    │ Load Balancer│
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
         ┌────▼────┐  ┌────▼────┐  ┌────▼────┐
         │ Backend │  │ Backend │  │ Backend │
         │ Instance│  │ Instance│  │ Instance│
         └────┬────┘  └────┬────┘  └────┬────┘
              │            │            │
              └────────────┼────────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
         ┌────▼────┐  ┌────▼────┐  ┌────▼────┐
         │PostgreSQL│  │  MinIO  │  │  Redis  │
         └─────────┘  └─────────┘  └─────────┘
```

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure all tests pass
5. Submit a pull request with clear description

## License

[Specify your license here]

## Support

For issues and questions:
- GitHub Issues: https://github.com/Bodeayman/AgritwinBackbone/issues
- Documentation: [Link to external docs if available]

## Changelog

See commit history for recent changes.
