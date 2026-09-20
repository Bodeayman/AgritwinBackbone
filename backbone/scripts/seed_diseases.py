"""
Seed diseases from JSON files into the database.

Usage:
    python scripts/seed_diseases.py --file path/to/disease.json
    python scripts/seed_diseases.py --directory path/to/diseases/
    python scripts/seed_diseases.py --file knowledge_base.json
"""
import json
import argparse
from pathlib import Path
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.disease import Disease


def seed_disease_from_comprehensive_json(db: Session, file_path: Path) -> Disease:
    """Seed a single disease from a comprehensive JSON file (like MAIZE_001.json)"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Check if disease already exists
    existing = db.query(Disease).filter(
        Disease.external_disease_id == data.get("disease_id")
    ).first()
    
    if existing:
        print(f"Disease {data.get('disease_id')} already exists, skipping...")
        return existing
    
    # Create new disease
    disease = Disease(
        external_disease_id=data.get("disease_id"),
        disease_name=data.get("disease_name"),
        crop_type=data.get("crop"),
        local_synonyms=data.get("local_synonyms"),
        pathogen=data.get("pathogen"),
        pathogen_type=data.get("pathogen_type"),
        description=data.get("description"),
        visual_features_json=data.get("visual_diagnosis"),
        evidence_level=data.get("evidence_level"),
        source="seeded"
    )
    
    db.add(disease)
    db.commit()
    db.refresh(disease)
    print(f"Seeded disease: {disease.disease_name} ({disease.external_disease_id})")
    return disease


def seed_diseases_from_knowledge_base(db: Session, file_path: Path):
    """Seed diseases from knowledge_base.json (simplified format)"""
    with open(file_path, 'r', encoding='utf-8') as f:
        diseases_data = json.load(f)
    
    for disease_data in diseases_data:
        # Check if disease already exists
        existing = db.query(Disease).filter(
            Disease.external_disease_id == disease_data.get("disease_id")
        ).first()
        
        if existing:
            print(f"Disease {disease_data.get('disease_id')} already exists, skipping...")
            continue
        
        # Extract crop type from disease name or use default
        disease_name = disease_data.get("disease_name", "")
        crop_type = "Unknown"
        if "maize" in disease_name.lower() or "corn" in disease_name.lower():
            crop_type = "Maize"
        elif "wheat" in disease_name.lower():
            crop_type = "Wheat"
        elif "rice" in disease_name.lower():
            crop_type = "Rice"
        
        # Create new disease with basic info
        disease = Disease(
            external_disease_id=disease_data.get("disease_id"),
            disease_name=disease_data.get("disease_name"),
            crop_type=crop_type,
            description=disease_data.get("description"),
            source="seeded"
        )
        
        db.add(disease)
        db.commit()
        db.refresh(disease)
        print(f"Seeded disease: {disease.disease_name} ({disease.external_disease_id})")


def seed_diseases_from_directory(db: Session, directory_path: Path):
    """Seed all diseases from a directory of JSON files"""
    json_files = list(directory_path.glob("*.json"))
    
    if not json_files:
        print(f"No JSON files found in {directory_path}")
        return
    
    print(f"Found {len(json_files)} JSON files in {directory_path}")
    
    for json_file in json_files:
        try:
            seed_disease_from_comprehensive_json(db, json_file)
        except Exception as e:
            print(f"Error seeding {json_file}: {e}")
            continue


def main():
    parser = argparse.ArgumentParser(description="Seed diseases from JSON files")
    parser.add_argument("--file", type=str, help="Path to a single JSON file")
    parser.add_argument("--directory", type=str, help="Path to directory containing JSON files")
    
    args = parser.parse_args()
    
    db = SessionLocal()
    
    try:
        if args.file:
            file_path = Path(args.file)
            if not file_path.exists():
                print(f"File not found: {file_path}")
                return
            
            # Check if it's knowledge_base.json or a comprehensive disease file
            if file_path.name == "knowledge_base.json":
                seed_diseases_from_knowledge_base(db, file_path)
            else:
                seed_disease_from_comprehensive_json(db, file_path)
        
        elif args.directory:
            directory_path = Path(args.directory)
            if not directory_path.exists() or not directory_path.is_dir():
                print(f"Directory not found: {directory_path}")
                return
            
            seed_diseases_from_directory(db, directory_path)
        
        else:
            print("Please specify --file or --directory")
            parser.print_help()
    
    finally:
        db.close()


if __name__ == "__main__":
    main()