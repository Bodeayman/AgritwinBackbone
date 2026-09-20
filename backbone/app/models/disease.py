from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base


class Disease(Base):
    __tablename__ = "diseases"

    id = Column(Integer, primary_key=True, index=True)
    external_disease_id = Column(String(100), unique=True, nullable=True, index=True)
    disease_name = Column(String(255), nullable=False, index=True)
    crop_type = Column(String(100), nullable=False, index=True)
    local_synonyms = Column(JSON, nullable=True)
    pathogen = Column(String(255), nullable=True)
    pathogen_type = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    visual_features_json = Column(JSON, nullable=True)
    evidence_level = Column(String(50), nullable=True)
    source = Column(String(100), nullable=True)  # "seeded", "synced", "auto_created"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship
    diagnoses = relationship("Diagnosis", back_populates="disease")

    def __repr__(self):
        return f"<Disease(id={self.id}, disease_name='{self.disease_name}', crop_type='{self.crop_type}')>"