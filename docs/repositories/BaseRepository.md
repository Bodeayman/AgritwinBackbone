# BaseRepository

## Overview

The `BaseRepository` is a generic repository base class that provides common data access operations for all entities. It implements the Repository pattern to abstract database operations and promote testability.

## File Location

`app/repositories/base.py`

## Responsibilities

- Generic CRUD operations (Create, Read, Update, Delete)
- Common query operations (get by ID, get multiple)
- Database session management

## Methods

### `__init__(model: Type[ModelType], db: Session)`

Initializes the repository with a model class and database session.

**Parameters:**
- `model` - SQLAlchemy model class
- `db` - SQLAlchemy database session

**Example:**
```python
from app.repositories.base import BaseRepository
from app.models.field import Field

repo = BaseRepository(Field, db)
```

### `get(id: Any) -> ModelType | None`

Retrieves a record by primary key ID.

**Parameters:**
- `id` - Primary key value

**Returns:** Model instance or None if not found

**Example:**
```python
field = repo.get(1)
```

### `get_multi(skip: int = 0, limit: int = 100) -> List[ModelType]`

Retrieves multiple records with pagination.

**Parameters:**
- `skip` - Number of records to skip (default: 0)
- `limit` - Maximum records to return (default: 100)

**Returns:** List of model instances

**Example:**
```python
fields = repo.get_multi(skip=0, limit=50)
```

### `create(db_obj: ModelType) -> ModelType`

Persists a new record to the database.

**Parameters:**
- `db_obj` - Model instance to persist

**Returns:** Persisted model instance with ID assigned

**Example:**
```python
field = Field(name="North Field", farm_id=1)
created_field = repo.create(field)
```

### `update(db_obj: ModelType, update_data: dict) -> ModelType`

Updates fields on an existing record.

**Parameters:**
- `db_obj` - Model instance to update
- `update_data` - Dictionary of field names and values to update

**Returns:** Updated model instance

**Example:**
```python
field = repo.get(1)
updated_field = repo.update(field, {"name": "Updated Name"})
```

### `remove(id: Any) -> ModelType | None`

Removes a record by ID.

**Parameters:**
- `id` - Primary key value

**Returns:** Removed model instance or None if not found

**Example:**
```python
removed = repo.remove(1)
```

## Usage Pattern

All specific repositories inherit from BaseRepository:

```python
from app.repositories.base import BaseRepository
from app.models.field import Field

class FieldRepository(BaseRepository[Field]):
    def __init__(self, db: Session):
        super().__init__(Field, db)

    def list_by_farm(self, farm_id: int, skip: int = 0, limit: int = 100):
        """Custom query specific to Field."""
        statement = select(Field).where(Field.farm_id == farm_id)
        statement = statement.offset(skip).limit(limit)
        return list(self.db.scalars(statement).all())
```

## Database Session

The repository uses the provided database session:
- Session is injected via dependency injection
- Session lifecycle is managed by the caller
- Typically created via `get_db()` dependency

## Transaction Management

- Repository methods perform commits automatically
- Caller should manage transaction boundaries
- For complex operations, consider explicit transaction handling

## Generic Type

The repository uses Python generics for type safety:

```python
ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    ...
```

This allows:
- Type hints for IDE support
- Compile-time type checking
- Runtime type validation

## Advantages

- **Code Reuse** - Common operations implemented once
- **Consistency** - All repositories follow same pattern
- **Testability** - Easy to mock for testing
- **Type Safety** - Generic typing provides type hints
- **Maintainability** - Changes to base operations affect all repositories

## Limitations

- Base operations don't include relationships
- Complex queries require custom methods in specific repositories
- No built-in eager loading (must be added in specific repositories)

## Related Files

- All repository files inherit from this base
- Located in: `app/repositories/`

## Notes

- Use specific repositories for domain-specific queries
- Override base methods if custom behavior needed
- Add indexes in model definitions for performance
- Use SQLAlchemy 2.0 select() syntax for custom queries
