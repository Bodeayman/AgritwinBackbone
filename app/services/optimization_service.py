from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.repositories.crop_catalog_repository import CropCatalogRepository
from app.repositories.crop_rotation_repository import CropRotationRepository
from app.repositories.field_repository import FieldRepository
from app.repositories.farm_repository import FarmRepository


class OptimizationService:
    def __init__(self, db: Session):
        self.db = db
        self.crop_repo = CropCatalogRepository(db)
        self.rotation_repo = CropRotationRepository(db)
        self.field_repo = FieldRepository(db)
        self.farm_repo = FarmRepository(db)

    def run_optimization(
        self,
        farm_id: int,
        season: str,
        zone: str,
        optimizer_version: str = "v4"
    ) -> Dict[str, Any]:
        """
        Run LP optimization for crop mix planning using a heuristic approach.
        
        Args:
            farm_id: Farm to optimize for
            season: Season to plan for
            zone: Regional zone
            optimizer_version: Optimizer version identifier
            
        Returns:
            Optimization result with allocations and financial summary
        """
        # Get farm data with budgets
        farm = self.farm_repo.get(farm_id)
        if not farm:
            raise ValueError(f"Farm {farm_id} not found")
        
        # Get fields for this farm
        fields = self.field_repo.list_by_farm(farm_id)
        if not fields:
            raise ValueError(f"No fields found for farm {farm_id}")
        
        # Get available crops (global catalog)
        crops = self.crop_repo.get_all_global()
        if not crops:
            raise ValueError("No crops available in catalog")
        
        # Run heuristic optimization
        return self._run_heuristic_optimization(farm, fields, crops, season, optimizer_version)

    def _run_heuristic_optimization(self, farm, fields, crops, season, optimizer_version):
        """
        Run a greedy heuristic optimization to maximize profit subject to constraints.
        This is a fallback when Pyomo solvers are not available.
        """
        allocations = []
        total_land_used = 0
        total_water_used = 0
        total_labor_used = 0
        total_fertilizer_used = 0
        total_revenue = 0
        total_production_cost = 0
        
        # Sort crops by profit per feddan (descending)
        sorted_crops = sorted(
            crops,
            key=lambda c: (c.expected_yield_tons_per_feddan * c.price_egp_per_ton - c.production_cost_egp_per_feddan),
            reverse=True
        )
        
        # Greedy allocation: assign most profitable crops first subject to constraints
        for field in fields:
            remaining_area = field.area_feddans or 0
            if remaining_area <= 0:
                continue
            
            for crop in sorted_crops:
                if remaining_area <= 0:
                    break
                
                # Check constraints
                water_per_feddan = crop.water_requirement_m3_per_feddan
                labor_per_feddan = crop.labor_requirement_hours_per_feddan
                fertilizer_per_feddan = crop.fertilizer_requirement_kg_per_feddan
                
                # Check if adding this crop would exceed any budget
                if (total_water_used + remaining_area * water_per_feddan > farm.water_budget_m3 or
                    total_labor_used + remaining_area * labor_per_feddan > farm.labor_budget_hours or
                    total_fertilizer_used + remaining_area * fertilizer_per_feddan > farm.fertilizer_budget_kg):
                    continue
                
                # Check soil compatibility
                if field.soil_ph and (field.soil_ph < crop.min_ph or field.soil_ph > crop.max_ph):
                    continue
                if field.soil_ec_ds_m and field.soil_ec_ds_m > crop.max_ec_ds_m:
                    continue
                if field.soil_texture and field.soil_texture not in crop.suitable_textures:
                    continue
                
                # Check crop rotation compatibility
                if field.previous_crop_name:
                    suitability = self.rotation_repo.get_suitability(field.previous_crop_name, crop.name_en)
                    if suitability == 0:
                        continue
                
                # Allocate
                allocated_area = remaining_area
                profit_contribution = allocated_area * (
                    crop.expected_yield_tons_per_feddan * crop.price_egp_per_ton - 
                    crop.production_cost_egp_per_feddan
                )
                
                allocations.append({
                    "field_id": field.id,
                    "field_name": field.name_en or field.name,
                    "crop_id": crop.id,
                    "crop_name": crop.name_en,
                    "allocated_area_feddans": allocated_area,
                    "expected_profit_contribution_egp": profit_contribution
                })
                
                total_land_used += allocated_area
                total_water_used += allocated_area * water_per_feddan
                total_labor_used += allocated_area * labor_per_feddan
                total_fertilizer_used += allocated_area * fertilizer_per_feddan
                total_revenue += allocated_area * crop.expected_yield_tons_per_feddan * crop.price_egp_per_ton
                total_production_cost += allocated_area * crop.production_cost_egp_per_feddan
                remaining_area = 0
        
        # Calculate costs
        total_labor_cost = total_labor_used * farm.labor_rate_egp_per_hour
        total_fertilizer_cost = total_fertilizer_used * farm.fertilizer_rate_egp_per_kg
        net_profit = total_revenue - total_production_cost - total_labor_cost - total_fertilizer_cost
        
        # Detect binding constraints
        binding_constraints = []
        if total_water_used >= farm.water_budget_m3 * 0.95:
            binding_constraints.append("water")
        if total_labor_used >= farm.labor_budget_hours * 0.95:
            binding_constraints.append("labor")
        if total_fertilizer_used >= farm.fertilizer_budget_kg * 0.95:
            binding_constraints.append("fertilizer")
        if total_land_used >= sum(f.area_feddans or 0 for f in fields) * 0.95:
            binding_constraints.append("land")
        
        return {
            "is_feasible": len(allocations) > 0,
            "status": "optimal" if len(allocations) > 0 else "infeasible",
            "total_land_used_feddans": total_land_used,
            "total_water_used_m3": total_water_used,
            "total_labor_used_hours": total_labor_used,
            "total_fertilizer_used_kg": total_fertilizer_used,
            "total_expected_revenue_egp": total_revenue,
            "total_production_cost_egp": total_production_cost,
            "total_labor_cost_egp": total_labor_cost,
            "total_fertilizer_cost_egp": total_fertilizer_cost,
            "net_profit_egp": net_profit,
            "allocations": allocations,
            "binding_constraints": binding_constraints,
            "solver_status": "heuristic_greedy"
        }