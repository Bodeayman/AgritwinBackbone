import re
import requests
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.disease import Disease
from app.schemas.disease import DiseaseCreate, DiseaseUpdate


class DiseaseService:
    def __init__(self, db: Session):
        self.db = db
    
    def normalize_disease_name(self, name: str) -> str:
        """Normalize disease name for search comparison"""
        # Lowercase, remove extra spaces, remove special chars
        normalized = name.lower().strip()
        normalized = re.sub(r'\s+', ' ', normalized)
        normalized = re.sub(r'[^\w\s]', '', normalized)
        return normalized
    
    def find_or_create_disease(self, disease_name: str, crop_type: str) -> Disease:
        """
        Find disease by normalized name, or create if not found.
        Searches in disease_name and local_synonyms.
        """
        normalized_name = self.normalize_disease_name(disease_name)
        
        # Try exact match on disease_name
        disease = self.db.query(Disease).filter(
            Disease.crop_type == crop_type,
            Disease.is_active == True
        ).filter(
            func.lower(Disease.disease_name) == normalized_name
        ).first()
        
        if disease:
            return disease
        
        # Try match in local_synonyms
        diseases = self.db.query(Disease).filter(
            Disease.crop_type == crop_type,
            Disease.is_active == True,
            Disease.local_synonyms.isnot(None)
        ).all()
        
        for disease in diseases:
            if disease.local_synonyms:
                for synonym in disease.local_synonyms:
                    if self.normalize_disease_name(synonym) == normalized_name:
                        return disease
        
        # Create new disease if not found
        disease = Disease(
            disease_name=disease_name,
            crop_type=crop_type,
            source="auto_created"
        )
        self.db.add(disease)
        self.db.commit()
        self.db.refresh(disease)
        print(f"Auto-created disease: {disease_name} for crop: {crop_type}")
        return disease
    
    def get_disease(self, disease_id: int) -> Optional[Disease]:
        """Get disease by ID"""
        return self.db.query(Disease).filter(Disease.id == disease_id).first()
    
    def get_by_external_id(self, external_id: str) -> Optional[Disease]:
        """Get disease by external disease ID"""
        return self.db.query(Disease).filter(
            Disease.external_disease_id == external_id
        ).first()
    
    def list_diseases(
        self,
        crop_type: Optional[str] = None,
        is_active: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[Disease]:
        """List diseases with optional filters"""
        query = self.db.query(Disease).filter(Disease.is_active == is_active)
        
        if crop_type:
            query = query.filter(Disease.crop_type == crop_type)
        
        return query.order_by(Disease.disease_name).offset(skip).limit(limit).all()
    
    def create_disease(self, disease_in: DiseaseCreate) -> Disease:
        """Create a new disease"""
        disease = Disease(**disease_in.model_dump())
        self.db.add(disease)
        self.db.commit()
        self.db.refresh(disease)
        return disease
    
    def update_disease(self, disease_id: int, disease_in: DiseaseUpdate) -> Optional[Disease]:
        """Update an existing disease"""
        disease = self.get_disease(disease_id)
        if not disease:
            return None
        
        update_data = disease_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(disease, key, value)
        
        disease.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(disease)
        return disease
    
    def delete_disease(self, disease_id: int) -> bool:
        """Soft delete disease (set is_active=False)"""
        disease = self.get_disease(disease_id)
        if not disease:
            return False
        
        disease.is_active = False
        disease.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def sync_from_external(self, external_url: str) -> dict:
        """
        Sync diseases from external knowledge base module.
        Returns sync statistics.
        """
        try:
            response = requests.get(f"{external_url}/diseases", timeout=30)
            response.raise_for_status()
            diseases_data = response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch from external KB: {str(e)}")
        
        created_count = 0
        updated_count = 0
        
        for disease_data in diseases_data:
            external_id = disease_data.get("disease_id")
            if not external_id:
                continue
            
            existing = self.get_by_external_id(external_id)
            
            if existing:
                # Update existing
                existing.disease_name = disease_data.get("disease_name", existing.disease_name)
                existing.crop_type = disease_data.get("crop", existing.crop_type)
                existing.local_synonyms = disease_data.get("local_synonyms", existing.local_synonyms)
                existing.pathogen = disease_data.get("pathogen", existing.pathogen)
                existing.pathogen_type = disease_data.get("pathogen_type", existing.pathogen_type)
                existing.description = disease_data.get("description", existing.description)
                existing.visual_features_json = disease_data.get("visual_diagnosis", existing.visual_features_json)
                existing.evidence_level = disease_data.get("evidence_level", existing.evidence_level)
                existing.source = "synced"
                existing.updated_at = datetime.utcnow()
                updated_count += 1
            else:
                # Create new
                disease = Disease(
                    external_disease_id=external_id,
                    disease_name=disease_data.get("disease_name"),
                    crop_type=disease_data.get("crop"),
                    local_synonyms=disease_data.get("local_synonyms"),
                    pathogen=disease_data.get("pathogen"),
                    pathogen_type=disease_data.get("pathogen_type"),
                    description=disease_data.get("description"),
                    visual_features_json=disease_data.get("visual_diagnosis"),
                    evidence_level=disease_data.get("evidence_level"),
                    source="synced"
                )
                self.db.add(disease)
                created_count += 1
        
        self.db.commit()
        
        return {
            "created": created_count,
            "updated": updated_count,
            "total": created_count + updated_count
        }
    
    def search_external(self, external_url: str, name: str, crop: str) -> Optional[dict]:
        """Search external knowledge base by name and crop"""
        try:
            response = requests.get(
                f"{external_url}/diseases/search",
                params={"name": name, "crop": crop},
                timeout=30
            )
            response.raise_for_status()
            results = response.json()
            return results[0] if results else None
        except requests.RequestException:
            return None
    
    def get_total_disease_count(self) -> int:
        """Get total count of active diseases"""
        return self.db.query(Disease).filter(Disease.is_active == True).count()
    
    def get_disease_count_by_crop(self) -> dict:
        """Get disease count grouped by crop type"""
        result = self.db.query(
            Disease.crop_type,
            func.count(Disease.id)
        ).filter(
            Disease.is_active == True
        ).group_by(Disease.crop_type).all()
        
        return {crop: count for crop, count in result}
    
    def check_external_kb_reachable(self, external_url: str) -> bool:
        """Check if external knowledge base is reachable"""
        try:
            response = requests.get(f"{external_url}/health", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False