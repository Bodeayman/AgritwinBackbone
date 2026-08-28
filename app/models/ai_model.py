from datetime import datetime
from sqlalchemy import String, Text, DateTime, Boolean, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class AIModel(Base):
    """
    AI/ML model metadata entity with enhanced traceability and versioning.

    Stores information about machine learning models used for diagnoses,
    irrigation planning, yield prediction, and crop mix recommendations.
    Supports semantic versioning, framework tracking, and performance metrics.

    Attributes:
        id: Primary key, auto-incrementing integer.
        name: Model name (e.g., "disease_detector_v1", "yield_predictor").
        version: Semantic version string (e.g., "1.0.0", "2.1.3").
        description: Optional human-readable model description.
        model_type: Type of ML model (classification, regression, etc.).
        framework: ML framework used (tensorflow, pytorch, scikit-learn, etc.).
        framework_version: Framework version for reproducibility.
        training_data_version: Version of training data used.
        parameters: JSON field for hyperparameters and configuration.
        performance_metrics: JSON field for metrics (accuracy, F1, precision, recall).
        deployment_date: Date when model was deployed to production.
        is_active: Flag indicating if model is currently in use.
        created_at: Timestamp when model record was created.

    Relationships:
        Referenced by diagnoses, irrigation_plans, yield_predictions,
        and crop_mix_recommendations via model_id foreign key.

    Constraints:
        Unique constraint on (name, version) combination.
        is_active flag allows only one active version per model name.

    Indexes:
        name: Indexed for efficient model lookup.
        version: Indexed for version queries.
        ix_ai_models_name_version: Unique index on (name, version).
        ix_ai_models_name_active: Composite index for active model lookup.

    Usage:
        Models are registered via internal API endpoints before being used
        in diagnoses, predictions, or recommendations. The service layer
        resolves model IDs by name and version.
    """

    __tablename__ = "ai_models"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # classification, regression, etc.
    framework: Mapped[str | None] = mapped_column(String(50), nullable=True)  # tensorflow, pytorch, etc.
    framework_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    training_data_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    parameters: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # hyperparameters, config
    performance_metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # accuracy, F1, etc.
    deployment_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_ai_models_name_version", "name", "version", unique=True),
        Index("ix_ai_models_name_active", "name", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<AIModel(id={self.id}, name='{self.name}', version='{self.version}', is_active={self.is_active})>"

