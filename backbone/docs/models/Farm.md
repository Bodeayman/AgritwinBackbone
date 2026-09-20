# Farm Model

## Overview

The `Farm` model represents an agricultural organization or property in the AgriTwin system. Farms are the top-level organizational unit and contain multiple fields for crop management, monitoring, and analysis.

## File Location

`app/models/farm.py`

## Table Schema

**Table Name:** `farms`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique identifier |
| `owner_id` | INTEGER | FOREIGN KEY (users.id), NOT NULL, INDEX | Owner of the farm |
| `name` | VARCHAR(100) | NOT NULL | Human-readable farm name |
| `location` | VARCHAR(255) | NULLABLE | Geographic location description |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT NOW(), ON UPDATE | Last modification timestamp |

## Relationships

- **Belongs to:** `User` (owner) via `owner_id`
- **Has many:** `Field` entities (one-to-many via `Field.farm_id`)

## Cascade Behavior

- When a User is deleted, all owned Farms are deleted (CASCADE)
- When a Farm is deleted, all associated Fields are deleted (CASCADE)

## Indexes

- `owner_id` - Indexed for efficient owner lookup

## Usage Examples

### Creating a Farm

```python
from app.models.farm import Farm

farm = Farm(
    owner_id=1,
    name="Green Valley Farm",
    location="California, USA"
)
```

### Querying Farms by Owner

```python
from app.repositories.farm_repository import FarmRepository

repo = FarmRepository(db)
farms = repo.list_by_user(user_id=1)
```

## Related Services

- `FarmService` - Business logic for farm operations
- `FieldService` - Field operations within farms

## Related API Endpoints

### Farmer Endpoints (JWT Auth)
- `GET /api/v1/farms` - List user's farms
- `POST /api/v1/farms` - Create a new farm
- `GET /api/v1/farms/{id}` - Get farm details
- `PUT /api/v1/farms/{id}` - Update farm
- `DELETE /api/v1/farms/{id}` - Delete farm

### Internal Endpoints (API Key Auth)
- `GET /api/farms/{farm_id}` - Get farm details
- `GET /api/farms/{farm_id}/fields` - List farm fields
- `GET /api/farms/{farm_id}/crop-mixes/latest` - Get latest crop mixes

## Notes

- Farm names are not required to be unique
- Location is free-text and can include address, region, or coordinates
- All timestamp fields use UTC timezone
