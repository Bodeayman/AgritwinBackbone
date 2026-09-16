from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class DiseaseBase(BaseModel):
    external_disease_id: Optional[str] = Field(None, description="External knowledge base ID")
    disease_name: str = Field(..., description="Disease name")
    crop_type: str = Field(..., description="Crop type")
    local_synonyms: Optional[List[str]] = Field(None, description="Local disease name synonyms")
    pathogen: Optional[str] = Field(None, description="Pathogen name")
    pathogen_type: Optional[str] = Field(None, description="Pathogen type")
    description: Optional[str] = Field(None, description="Disease description")
    visual_features_json: Optional[Dict[str, Any]] = Field(None, description="Visual features for ML")
    evidence_level: Optional[str] = Field(None, description="Evidence level")
    source: Optional[str] = Field(None, description="Data source")
    is_active: bool = Field(True, description="Active status")


class DiseaseCreate(DiseaseBase):
    pass


class DiseaseUpdate(BaseModel):
    disease_name: Optional[str] = None
    crop_type: Optional[str] = None
    local_synonyms: Optional[List[str]] = None
    pathogen: Optional[str] = None
    pathogen_type: Optional[str] = None
    description: Optional[str] = None
    visual_features_json: Optional[Dict[str, Any]] = None
    evidence_level: Optional[str] = None
    source: Optional[str] = None
    is_active: Optional[bool] = None


class DiseaseOut(DiseaseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DiseaseReferenceOut(BaseModel):
    """Lightweight reference for display in diagnoses"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    external_disease_id: Optional[str] = None
    disease_name: str
    crop_type: str