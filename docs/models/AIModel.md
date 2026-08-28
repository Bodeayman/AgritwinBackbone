# AIModel Model

## Overview

The `AIModel` model stores metadata about machine learning models used for diagnoses, irrigation planning, yield prediction, and crop mix recommendations. It supports semantic versioning, framework tracking, and performance metrics for model traceability and reproducibility.

## File Location

`app/models/ai_model.py`

## Table Schema

**Table Name:** `ai_models`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique identifier |
| `name` | VARCHAR(100) | NOT NULL, INDEX | Model name (e.g., "disease_detector") |
| `version` | VARCHAR(50) | NOT NULL, INDEX | Semantic version (e.g., "1.0.0") |
| `description` | TEXT | NULLABLE | Human-readable description |
| `model_type` | VARCHAR(50) | NULLABLE | ML model type (classification, regression) |
| `framework` | VARCHAR(50) | NULLABLE | ML framework (tensorflow, pytorch) |
| `framework_version` | VARCHAR(50) | NULLABLE | Framework version |
| `training_data_version` | VARCHAR(50) | NULLABLE | Training data version |
| `parameters` | JSON | NULLABLE | Hyperparameters and config |
| `performance_metrics` | JSON | NULLABLE | Metrics (accuracy, F1, etc.) |
| `deployment_date` | TIMESTAMP | NULLABLE | Production deployment date |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Active status flag |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Creation timestamp |

## Relationships

- **Referenced by:** `Diagnosis`, `IrrigationPlan`, `YieldPrediction`, `CropMixRecommendation` via `model_id`

## Constraints

- **Unique constraint:** (name, version) combination must be unique
- **Active flag:** Only one version per model name should be active at a time

## Indexes

- `name` - Indexed for efficient model lookup
- `version` - Indexed for version queries
- `ix_ai_models_name_version` - Unique index on (name, version)
- `ix_ai_models_name_active` - Composite index for active model lookup

## Usage Examples

### Registering a Model

```python
from app.models.ai_model import AIModel

model = AIModel(
    name="disease_detector",
    version="1.0.0",
    description="Detects crop diseases from imagery",
    model_type="classification",
    framework="pytorch",
    framework_version="2.0.0",
    parameters={"learning_rate": 0.001, "batch_size": 32},
    performance_metrics={"accuracy": 0.95, "f1_score": 0.93},
    is_active=True
)
```

### Querying Active Models

```python
from app.repositories.ai_model_repository import AIModelRepository

repo = AIModelRepository(db)
active_models = repo.list_active()
```

### Resolving Model by Name and Version

```python
from app.services.ai_model_service import AIModelService

service = AIModelService(db)
model = service.get_by_name_and_version("disease_detector", "1.0.0")
```

## Related Services

- `AIModelService` - Model registration, resolution, and management

## Related API Endpoints

### Internal Endpoints (API Key Auth)
- `POST /api/models` - Register or get an AI model
- `GET /api/models` - List registered AI models

## Model Types

- **classification** - For disease diagnosis
- **regression** - For yield prediction
- **optimization** - For crop mix recommendations
- **time_series** - For irrigation planning

## Frameworks Supported

- **pytorch** - PyTorch deep learning framework
- **tensorflow** - TensorFlow/Keras
- **scikit-learn** - Traditional ML algorithms
- **xgboost** - Gradient boosting
- **custom** - Custom or proprietary frameworks

## Performance Metrics

Common metrics stored in `performance_metrics` JSON field:
- **accuracy** - Overall accuracy
- **precision** - Precision score
- **recall** - Recall score
- **f1_score** - F1 score
- **mae** - Mean absolute error (regression)
- **rmse** - Root mean squared error (regression)
- **r2** - R-squared (regression)

## Notes

- Models must be registered before being used in diagnoses/predictions
- Use semantic versioning (MAJOR.MINOR.PATCH)
- Deactivate old versions before activating new ones
- Store only metadata, not model weights (weights stored separately)
- All timestamp fields use UTC timezone
