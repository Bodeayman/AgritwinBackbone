# FieldService

## Overview

The `FieldService` handles business logic for field operations including CRUD operations, field lookup by farm, and field validation. It serves as the application layer for field-related operations.

## File Location

`app/services/field_service.py`

## Responsibilities

- Create, read, update, delete field operations
- List fields by farm
- Field existence validation
- Business logic for field operations

## Methods

### `create_field(field_in: FieldCreate) -> FieldOut`

Creates a new field.

**Parameters:**
- `field_in` - FieldCreate schema with field data

**Returns:** Created field as FieldOut schema

**Example:**
```python
from app.services.field_service import FieldService
from app.schemas.field import FieldCreate

service = FieldService(db)
field = service.create_field(
    FieldCreate(
        farm_id=1,
        name="North Field"
    )
)
```

### `get_field(field_id: int) -> FieldOut | None`

Retrieves a field by ID.

**Parameters:**
- `field_id` - Field primary key

**Returns:** Field as FieldOut schema, or None if not found

**Example:**
```python
field = service.get_field(field_id=1)
```

### `list_by_farm(farm_id: int, skip: int = 0, limit: int = 100) -> List[FieldOut]`

Lists all fields belonging to a farm.

**Parameters:**
- `farm_id` - Farm primary key
- `skip` - Number of records to skip (pagination)
- `limit` - Maximum records to return

**Returns:** List of fields as FieldOut schemas

**Example:**
```python
fields = service.list_by_farm(farm_id=1, skip=0, limit=50)
```

### `update_field(field_id: int, field_in: FieldUpdate) -> FieldOut | None`

Updates an existing field.

**Parameters:**
- `field_id` - Field primary key
- `field_in` - FieldUpdate schema with updated data

**Returns:** Updated field as FieldOut schema, or None if not found

**Example:**
```python
field = service.update_field(
    field_id=1,
    FieldUpdate(name="Updated Field Name")
)
```

### `delete_field(field_id: int) -> bool`

Deletes a field.

**Parameters:**
- `field_id` - Field primary key

**Returns:** True if deleted, False if not found

**Note:** Deleting a field cascades to delete all related data (sensor readings, weather, diagnoses, etc.)

**Example:**
```python
deleted = service.delete_field(field_id=1)
```

## Dependencies

- `FieldRepository` - Data access for Field entities
- `FarmRepository` - Data access for Farm entities (for validation)

## Related API Endpoints

### Farmer Endpoints (JWT Auth)
- `GET /api/v1/fields` - List user's fields
- `POST /api/v1/fields` - Create a new field
- `GET /api/v1/fields/{id}` - Get field details
- `PUT /api/v1/fields/{id}` - Update field
- `DELETE /api/v1/fields/{id}` - Delete field

### Internal Endpoints (API Key Auth)
- `GET /api/fields/{field_id}` - Get field details
- `GET /api/farms/{farm_id}/fields` - List farm fields

## Business Logic

### Field Creation
- Validates that the farm exists
- Ensures field name is provided
- Automatically sets timestamps

### Field Deletion
- Cascades to delete all related data
- Consider archiving instead of hard delete for historical data

### Field Updates
- Preserves creation timestamp
- Updates modification timestamp

## Error Handling

- **404 Not Found** - Field or farm not found
- **422 Validation Error** - Invalid input data
- **500 Internal Server Error** - Database errors

## Notes

- Fields are the central entity linking most data in the system
- Use pagination for large farm field lists
- Consider soft delete for historical data preservation
- All operations use repository pattern for data access
