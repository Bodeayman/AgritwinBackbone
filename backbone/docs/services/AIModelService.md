# AIModelService

## Overview

The `AIModelService` handles business logic for AI/ML model management including model registration, resolution by name/version, and active model queries. It ensures models are properly registered before being used in diagnoses, predictions, and recommendations.

## File Location

`app/services/ai_model_service.py`

## Responsibilities

- Register AI models
- Retrieve models by ID
- List all models
- List active models
- Resolve model ID by name and version
- Get or create models by name

## Methods

### `create_model(model_in: AIModelCreate) -> AIModelOut`

Registers a new AI model or returns existing model if name/version match.

**Parameters:**
- `model_in` - AIModelCreate schema with model metadata

**Returns:** Created or existing model as AIModelOut schema

**Example:**
```python
from app.services.ai_model_service import AIModelService
from app.schemas.ai_model import AIModelCreate

service = AIModelService(db)
model = service.create_model(
    AIModelCreate(
        name="disease_detector",
        version="1.0.0",
        description="Detects crop diseases from imagery",
        model_type="classification",
        framework="pytorch",
        framework_version="2.0.0",
        parameters={"learning_rate": 0.001},
        performance_metrics={"accuracy": 0.95}
    )
)
```

### `get_model(model_id: int) -> AIModelOut | None`

Retrieves a model by ID.

**Parameters:**
- `model_id` - Model primary key

**Returns:** Model as AIModelOut schema, or None if not found

**Example:**
```python
model = service.get_model(model_id=1)
```

### `list_models(skip: int = 0, limit: int = 100) -> List[AIModelOut]`

Lists all registered models.

**Parameters:**
- `skip` - Number of records to skip (pagination)
- `limit` - Maximum records to return

**Returns:** List of models as AIModelOut schemas

**Example:**
```python
models = service.list_models(skip=0, limit=50)
```

### `list_active(skip: int = 0, limit: int = 100) -> List[AIModelOut]`

Lists only active models.

**Parameters:**
- `skip` - Number of records to skip (pagination)
- `limit` - Maximum records to return

**Returns:** List of active models as AIModelOut schemas

**Example:**
```python
active_models = service.list_active()
```

### `get_by_name_and_version(name: str, version: str) -> AIModelOut | None`

Retrieves a model by name and version.

**Parameters:**
- `name` - Model name
- `version` - Model version

**Returns:** Model as AIModelOut schema, or None if not found

**Example:**
```python
model = service.get_by_name_and_version("disease_detector", "1.0.0")
```

### `resolve_model_id(model_id: int | None, model_name: str | None, model_version: str | None) -> int | None`

Resolves model ID from either direct ID or name/version combination.

**Parameters:**
- `model_id` - Direct model ID (takes precedence)
- `model_name` - Model name (used if model_id is None)
- `model_version` - Model version (used with model_name)

**Returns:** Resolved model ID, or None if not found

**Example:**
```python
# Resolve by ID
model_id = service.resolve_model_id(model_id=5, model_name=None, model_version=None)

# Resolve by name and version
model_id = service.resolve_model_id(model_id=None, model_name="disease_detector", model_version="1.0.0")
```

### `get_or_create(name: str) -> AIModelOut`

Gets an existing model by name or creates a new one with default values.

**Parameters:**
- `name` - Model name

**Returns:** Existing or created model as AIModelOut schema

**Example:**
```python
model = service.get_or_create("Sentinel-2")
```

## Dependencies

- `AIModelRepository` - Data access for AIModel entities

## Related API Endpoints

### Internal Endpoints (API Key Auth)
- `POST /api/models` - Register or get an AI model
- `GET /api/models` - List registered AI models

## Business Logic

### Model Registration
- Enforces unique (name, version) constraint
- Allows registering multiple versions of same model
- Stores metadata for reproducibility
- Tracks performance metrics

### Model Resolution
- Prioritizes direct model_id over name/version
- Used in ingestion endpoints for flexibility
- Enables ingestion by model name without knowing ID

### Active Model Management
- Only one version per model name should be active
- Active models are used in production
- Deactivate old versions before activating new ones

## Model Lifecycle

1. **Development** - Model trained and evaluated
2. **Registration** - Model metadata registered via API
3. **Activation** - Model marked as active
4. **Usage** - Model used in diagnoses/predictions
5. **Deprecation** - Model deactivated when superseded

## Versioning

Use semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR** - Breaking changes
- **MINOR** - New features, backward compatible
- **PATCH** - Bug fixes, backward compatible

Example: `1.0.0` → `1.0.1` → `1.1.0` → `2.0.0`

## Error Handling

- **404 Not Found** - Model not found
- **409 Conflict** - Model name/version already exists
- **422 Validation Error** - Invalid input data
- **500 Internal Server Error** - Database errors

## Notes

- Models must be registered before being used
- Store only metadata, not model weights
- Use semantic versioning for consistency
- Track performance metrics for model comparison
- Deactivate old versions before activating new ones
- All timestamp fields use UTC timezone
