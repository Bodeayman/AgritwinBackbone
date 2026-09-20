# CropCycle Model

## Overview

The `CropCycle` model represents planting and harvest cycles for fields. It tracks crop planting dates, growth stages, harvest information, and cycle status to manage crop rotations and field usage over time.

## File Location

`app/models/crop_cycle.py`

## Table Schema

**Table Name:** `crop_cycles`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique identifier |
| `field_id` | INTEGER | FOREIGN KEY (fields.id), NOT NULL | Field for this cycle |
| `crop` | VARCHAR(100) | NOT NULL | Crop type |
| `planted_at` | DATE | NULLABLE | Planting date |
| `expected_harvest_date` | DATE | NULLABLE | Expected harvest date |
| `actual_harvest_date` | DATE | NULLABLE | Actual harvest date |
| `status` | VARCHAR(50) | NOT NULL | Cycle status |
| `yield_tons_per_hectare` | FLOAT | NULLABLE | Actual yield |
| `notes` | TEXT | NULLABLE | Additional notes |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Record creation timestamp |

## Relationships

- **Belongs to:** `Field` via `field_id` (CASCADE on field deletion)

## Cascade Behavior

- When a Field is deleted, all associated CropCycles are deleted (CASCADE)

## Usage Examples

### Creating a Crop Cycle

```python
from app.models.crop_cycle import CropCycle
from datetime import date

cycle = CropCycle(
    field_id=1,
    crop="Maize",
    planted_at=date(2024, 4, 15),
    expected_harvest_date=date(2024, 9, 15),
    status="growing",
    notes="Hybrid variety XYZ planted"
)
```

### Harvesting a Crop

```python
cycle.actual_harvest_date = date(2024, 9, 10)
cycle.status = "harvested"
cycle.yield_tons_per_hectare = 8.5
```

## Related Services

- `CropCycleService` - Crop cycle management and queries

## Related API Endpoints

### Farmer Endpoints (JWT Auth)
- `GET /api/v1/crop-cycles` - List crop cycles
- `POST /api/v1/crop-cycles` - Create crop cycle
- `GET /api/v1/crop-cycles/{id}` - Get cycle details
- `PUT /api/v1/crop-cycles/{id}` - Update cycle
- `DELETE /api/v1/crop-cycles/{id}` - Delete cycle

## Status Values

- **planned** - Cycle planned but not started
- **planted** - Crop planted, growing
- **growing** - Actively growing (synonym for planted)
- **harvested** - Crop harvested
- **failed** - Cycle failed (disease, weather, etc.)
- **abandoned** - Cycle abandoned

## Common Crop Types

- **Cereals:** Wheat, Maize, Rice, Barley, Oats
- **Legumes:** Soybeans, Beans, Peas, Lentils
- **Root vegetables:** Potatoes, Carrots, Onions
- **Oilseeds:** Canola, Sunflower, Soybeans
- **Fruits:** Tomatoes, Apples, Grapes
- **Vegetables:** Lettuce, Cabbage, Peppers

## Growth Stages

Typical growth stages (not stored in model, used for status):
1. **Germination** - Seed sprouting
2. **Vegetative** - Leaf development
3. **Flowering** - Reproductive stage
4. **Fruit/Grain filling** - Yield development
5. **Maturation** - Ripening
6. **Harvest** - Ready for harvest

## Crop Rotation Benefits

- **Disease management** - Breaks pest/disease cycles
- **Soil health** - Improves soil structure and fertility
- **Nutrient balance** - Different crops have different nutrient needs
- **Weed control** - Disrupts weed life cycles
- **Yield optimization** - Reduces yield depletion

## Notes

- Crop cycles track temporal field usage
- Multiple cycles can exist per field over time
- Historical cycles enable yield trend analysis
- Current crop accessible via `Field.current_crop` property
- All timestamp fields use UTC timezone
- Used in conjunction with yield predictions for validation
