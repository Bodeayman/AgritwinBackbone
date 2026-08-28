from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class AIModelBase(BaseModel):
    name: str = Field(..., max_length=100, examples=["ResNet50_CropDisease"])
    version: str = Field(..., max_length=50, examples=["v1.2.0"])
    description: Optional[str] = Field(None, examples=["ResNet50 model fine-tuned for corn/wheat leaf diseases."])
    model_type: Optional[str] = Field(None, max_length=50, examples=["classification", "regression", "segmentation"])
    framework: Optional[str] = Field(None, max_length=50, examples=["tensorflow", "pytorch", "onnx"])
    framework_version: Optional[str] = Field(None, max_length=50, examples=["2.0.1"])
    training_data_version: Optional[str] = Field(None, max_length=50, examples=["v1.2.0"])
    parameters: Optional[Dict[str, Any]] = Field(None, examples=[{"bands": ["B4", "B8"], "threshold": 0.3}])
    performance_metrics: Optional[Dict[str, Any]] = Field(None, examples=[{"accuracy": 0.95, "f1_score": 0.93}])
    deployment_date: Optional[datetime] = Field(None, examples=["2026-08-01T00:00:00Z"])
    is_active: bool = Field(True, examples=[True])


class AIModelCreate(AIModelBase):
    pass


class AIModelOut(AIModelBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., examples=[1])
    created_at: Optional[datetime] = Field(None, examples=["2026-08-09T10:00:00Z"])
