# Fields Controller

## Overview

The Fields controller handles field management endpoints for farmers. It provides CRUD operations for fields, allowing farmers to create, read, update, and delete fields within their farms.

## File Location

`app/api/v1/fields.py`

## Endpoints

### GET /api/v1/fields

Lists all fields belonging to the authenticated user.

**Authentication:** JWT Bearer Token required

**Query Parameters:**
- `skip` (optional) - Number of records to skip (default: 0)
- `limit` (optional) - Maximum records to return (default: 100)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "farm_id": 1,
    "name": "North Field",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/v1/fields \
  -H "Authorization: Bearer <token>"
```

---

### POST /api/v1/fields

Creates a new field.

**Authentication:** JWT Bearer Token required

**Request Body:**
```json
{
  "farm_id": 1,
  "name": "North Field"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "farm_id": 1,
  "name": "North Field",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**
- **404 Not Found** - Farm not found
- **422 Unprocessable Entity** - Invalid input data

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/fields \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"farm_id":1,"name":"North Field"}'
```

---

### GET /api/v1/fields/{id}

Retrieves a specific field by ID.

**Authentication:** JWT Bearer Token required

**Path Parameters:**
- `id` - Field primary key

**Response (200 OK):**
```json
{
  "id": 1,
  "farm_id": 1,
  "name": "North Field",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**
- **404 Not Found** - Field not found

**Example:**
```bash
curl -X GET http://localhost:8000/api/v1/fields/1 \
  -H "Authorization: Bearer <token>"
```

---

### PUT /api/v1/fields/{id}

Updates an existing field.

**Authentication:** JWT Bearer Token required

**Path Parameters:**
- `id` - Field primary key

**Request Body:**
```json
{
  "name": "Updated Field Name"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "farm_id": 1,
  "name": "Updated Field Name",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-16T14:20:00Z"
}
```

**Error Responses:**
- **404 Not Found** - Field not found
- **422 Unprocessable Entity** - Invalid input data

**Example:**
```bash
curl -X PUT http://localhost:8000/api/v1/fields/1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Updated Field Name"}'
```

---

### DELETE /api/v1/fields/{id}

Deletes a field.

**Authentication:** JWT Bearer Token required

**Path Parameters:**
- `id` - Field primary key

**Response (200 OK):**
```json
{
  "message": "Field deleted successfully"
}
```

**Error Responses:**
- **404 Not Found** - Field not found

**Note:** Deleting a field cascades to delete all related data (sensor readings, weather, diagnoses, irrigation plans, yield predictions, crop cycles, satellite observations, imagery).

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/v1/fields/1 \
  -H "Authorization: Bearer <token>"
```

---

## Related Services

- `FieldService` - Business logic for field operations
- `FarmService` - Farm validation (ensures farm exists)

## Dependencies

- `get_current_user` - JWT authentication dependency
- `get_field_service` - Field service injection

## Schemas

### FieldCreate
```python
class FieldCreate(BaseModel):
    farm_id: int
    name: str
```

### FieldUpdate
```python
class FieldUpdate(BaseModel):
    name: str | None = None
```

### FieldOut
```python
class FieldOut(BaseModel):
    id: int
    farm_id: int
    name: str
    created_at: datetime
    updated_at: datetime
```

## Authorization

- User can only access fields belonging to their farms
- User can only create fields in their own farms
- User can only update/delete their own fields

## Notes

- All timestamps are in UTC
- Field names are not required to be unique
- Use pagination for large field lists
- Consider soft delete for historical data preservation
- Field deletion cascades to all related data
