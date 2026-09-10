from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.crop_catalog_repository import CropCatalogRepository
from app.models.crop_catalog import CropCatalog
from app.schemas.crop_catalog import CropCatalogCreate, CropCatalogOut


class CropCatalogService:
    def __init__(self, db: Session):
        self.repo = CropCatalogRepository(db)

    def create_crop(self, crop_in: CropCatalogCreate) -> CropCatalogOut:
        obj = CropCatalog(
            farm_id=crop_in.farm_id,
            name_en=crop_in.name_en,
            name_ar=crop_in.name_ar,
            category=crop_in.category,
            expected_yield_tons_per_feddan=crop_in.expected_yield_tons_per_feddan,
            price_egp_per_ton=crop_in.price_egp_per_ton,
            production_cost_egp_per_feddan=crop_in.production_cost_egp_per_feddan,
            water_requirement_m3_per_feddan=crop_in.water_requirement_m3_per_feddan,
            labor_requirement_hours_per_feddan=crop_in.labor_requirement_hours_per_feddan,
            fertilizer_requirement_kg_per_feddan=crop_in.fertilizer_requirement_kg_per_feddan,
            min_ph=crop_in.min_ph,
            max_ph=crop_in.max_ph,
            max_ec_ds_m=crop_in.max_ec_ds_m,
            suitable_textures=crop_in.suitable_textures,
            is_perennial=crop_in.is_perennial,
        )
        return CropCatalogOut.model_validate(self.repo.create(obj))

    def get_crop(self, crop_id: int) -> Optional[CropCatalogOut]:
        obj = self.repo.get(crop_id)
        return CropCatalogOut.model_validate(obj) if obj else None

    def get_by_name(self, name_en: str, farm_id: Optional[int] = None) -> Optional[CropCatalogOut]:
        obj = self.repo.get_by_name(name_en, farm_id)
        return CropCatalogOut.model_validate(obj) if obj else None

    def list_crops(self, skip: int = 0, limit: int = 100, farm_id: Optional[int] = None) -> List[CropCatalogOut]:
        objs = self.repo.get_multi(skip=skip, limit=limit, farm_id=farm_id)
        return [CropCatalogOut.model_validate(o) for o in objs]

    def list_global_crops(self, skip: int = 0, limit: int = 100) -> List[CropCatalogOut]:
        objs = self.repo.get_all_global(skip=skip, limit=limit)
        return [CropCatalogOut.model_validate(o) for o in objs]

    def delete_crop(self, crop_id: int) -> bool:
        return self.repo.delete(crop_id)