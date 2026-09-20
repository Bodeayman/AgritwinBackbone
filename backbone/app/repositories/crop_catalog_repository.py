from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.base import Base
from app.models.crop_catalog import CropCatalog


class CropCatalogRepository:
    def __init__(self, db: Session):
        self.db = db
        self.model = CropCatalog

    def get(self, crop_id: int) -> Optional[CropCatalog]:
        return self.db.query(self.model).filter(self.model.id == crop_id).first()

    def get_by_name(self, name_en: str, farm_id: Optional[int] = None) -> Optional[CropCatalog]:
        query = self.db.query(self.model).filter(self.model.name_en == name_en)
        if farm_id is not None:
            query = query.filter(self.model.farm_id == farm_id)
        return query.first()

    def get_multi(self, skip: int = 0, limit: int = 100, farm_id: Optional[int] = None) -> List[CropCatalog]:
        query = self.db.query(self.model)
        if farm_id is not None:
            query = query.filter(self.model.farm_id == farm_id)
        return query.offset(skip).limit(limit).all()

    def get_all_global(self, skip: int = 0, limit: int = 100) -> List[CropCatalog]:
        return self.db.query(self.model).filter(self.model.farm_id.is_(None)).offset(skip).limit(limit).all()

    def create(self, obj: CropCatalog) -> CropCatalog:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj: CropCatalog, **kwargs) -> CropCatalog:
        for key, value in kwargs.items():
            setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, crop_id: int) -> bool:
        obj = self.get(crop_id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True