# AgriTwin Documentation

This directory contains comprehensive documentation for the AgriTwin Backend system.

## Documentation Structure

```
docs/
├── models/           # Database model documentation
├── services/         # Service layer documentation
├── api/              # API endpoint documentation
├── repositories/     # Repository pattern documentation
├── schemas/          # Pydantic schema documentation
└── core/             # Core module documentation
```

## Quick Links

### Database Models
- [Models Overview](./models/README.md)
- [User](./models/User.md) - User accounts
- [Farm](./models/Farm.md) - Agricultural organizations
- [Field](./models/Field.md) - Agricultural areas
- [AIModel](./models/AIModel.md) - AI/ML model metadata
- [Satellite](./models/Satellite.md) - Satellite platforms
- [Imagery](./models/Imagery.md) - Image management
- [SatelliteObservation](./models/SatelliteObservation.md) - Satellite data
- [Diagnosis](./models/Diagnosis.md) - Disease diagnoses
- [IrrigationPlan](./models/IrrigationPlan.md) - Irrigation recommendations
- [YieldPrediction](./models/YieldPrediction.md) - Yield forecasts
- [CropCycle](./models/CropCycle.md) - Planting/harvest cycles
- [SensorReading](./models/SensorReading.md) - IoT sensor data
- [Weather](./models/Weather.md) - Weather measurements

### Services
- [Services Overview](./services/README.md)
- [AuthService](./services/AuthService.md) - Authentication
- [FieldService](./services/FieldService.md) - Field operations
- [DiagnosisService](./services/DiagnosisService.md) - Diagnosis operations
- [AIModelService](./services/AIModelService.md) - AI model management

### API Controllers
- [API Overview](./api/README.md) - Complete API reference
- [Auth Controller](./api/AuthController.md) - Authentication endpoints
- [Fields Controller](./api/FieldsController.md) - Field management endpoints
- [Internal Router](./api/InternalRouter.md) - Internal API endpoints

### Repositories
- [Repositories Overview](./repositories/README.md)
- [BaseRepository](./repositories/BaseRepository.md) - Generic CRUD operations

### Schemas
- [Schemas Overview](./schemas/README.md) - Pydantic schema documentation

### Core Modules
- [Core Overview](./core/README.md) - Infrastructure services
- [Config](./core/Config.md) - Configuration management
- [Database](./core/Database.md) - Database engine and sessions

### Services
- [Services Overview](./services/README.md)
- [AuthService](./services/AuthService.md) - Authentication
- [FieldService](./services/FieldService.md) - Field operations
- [DiagnosisService](./services/DiagnosisService.md) - Diagnosis operations
- [AIModelService](./services/AIModelService.md) - AI model management

### API Endpoints
- [API Overview](./api/README.md) - Complete API reference
- [Auth Controller](./api/AuthController.md) - Authentication endpoints
- [Fields Controller](./api/FieldsController.md) - Field management endpoints
- [Internal Router](./api/InternalRouter.md) - Internal API endpoints

### Additional Documentation

See project root for:
- [README.md](../README.md) - Main project documentation
- [MULTI_SERVER_ARCHITECTURE.md](../MULTI_SERVER_ARCHITECTURE.md) - Scaling strategy
- [DEVELOPMENT_WORKFLOW.md](../DEVELOPMENT_WORKFLOW.md) - Development guide
- [IMPROVEMENTS.md](../IMPROVEMENTS.md) - Prioritized improvements
- [PROJECT_INSPECTION_REPORT.md](../PROJECT_INSPECTION_REPORT.md) - Audit results

## Architecture Overview

The AgriTwin system follows N-Tier architecture:

```
Presentation Layer (app/api/)
    ↓
Application Layer (app/services/)
    ↓
Domain Layer (app/models/, app/schemas/)
    ↓
Infrastructure Layer (app/repositories/, app/core/)
```

## Getting Started

1. **Project Setup:** See [README.md](../README.md)
2. **API Documentation:** See [API Overview](./api/README.md)
3. **Database Models:** See [Models Overview](./models/README.md)
4. **Development Workflow:** See [DEVELOPMENT_WORKFLOW.md](../DEVELOPMENT_WORKFLOW.md)

## Key Concepts

### Authentication
- **JWT Bearer Tokens** - For farmer-facing endpoints
- **API Keys** - For internal module endpoints

### Data Model
- **Farms** contain **Fields**
- **Fields** have associated monitoring data
- **AI Models** provide diagnoses, predictions, recommendations
- **Satellites** provide imagery and observations

### API Structure
- **`/api/v1/`** - Farmer endpoints (JWT auth)
- **`/api/`** - Internal endpoints (API key auth)

## Documentation Conventions

- All documentation uses Markdown
- Code examples use Python syntax highlighting
- API examples use HTTP request/response format
- Database schemas use table format
- Relationships are documented with entity diagrams

## Contributing to Documentation

When adding new features:
1. Update model documentation in `docs/models/`
2. Update service documentation in `docs/services/`
3. Update API documentation in `docs/api/`
4. Update main README.md if needed
5. Keep documentation in sync with code changes

## Support

For questions or issues:
- GitHub Issues: https://github.com/Bodeayman/AgritwinBackbone/issues
- See [README.md](../README.md) for additional resources
