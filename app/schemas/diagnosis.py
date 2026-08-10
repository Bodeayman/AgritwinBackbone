from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from app.schemas.ai_model import AIModelOut


class DiagnosisBase(BaseModel):
    field_id: int = Field(..., examples=[1])
    model_id: Optional[int] = Field(None, description="FK ID to ai_models entity", examples=[1])
    model_name: Optional[str] = Field(None, description="Name of the AI model used", examples=["ResNet50_CropDisease"])
    model_version: Optional[str] = Field(None, description="Version of the AI model used", examples=["v1.2.0"])
    image_reference: Optional[str] = Field(
        None,
        description="Relative path to the stored diagnosis image",
        examples=["diagnoses/1/leaf_20260808_143012_b7c1.jpg"],
    )
    crop_type: Optional[str] = Field(None, max_length=100, examples=["Maize"])
    disease_or_pest: str = Field(..., max_length=255, examples=["Maize Lethal Necrosis"])
    severity: Optional[float] = Field(None, ge=0.0, le=1.0, examples=[0.45])
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, examples=[0.92])
    latitude: Optional[float] = Field(None, examples=[-1.292])
    longitude: Optional[float] = Field(None, examples=[36.821])
    status: str = Field("processed", description="AI processing status: 'pending', 'processing', 'processed', 'failed', 'ready'", examples=["processed"])
    diagnosed_at: datetime = Field(..., examples=["2026-08-08T11:00:00Z"])
    explanation: Optional[str] = Field(
        None,
        examples=["Yellowing of lower leaves combined with necrotic streaks suggests MLN infection."],
    )
    treatment_suggestion: Optional[str] = Field(
        None,
        examples=["Remove infected plants. Apply copper-based fungicide. Replant with resistant variety."],
    )


class DiagnosisCreate(DiagnosisBase):
    pass


class DiagnosisOut(DiagnosisBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., examples=[1])
    ai_model: Optional[AIModelOut] = Field(None, description="Nested AIModel entity details")
    created_at: Optional[datetime] = Field(None, examples=["2026-08-08T11:00:01Z"])
