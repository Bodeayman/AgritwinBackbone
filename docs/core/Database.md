# Database Module

## Overview

The Database module manages SQLAlchemy database engine, session factory, and dependency injection for database access. It provides a centralized database configuration for the application.

## File Location

`app/core/database.py`

## Components

### Engine

The SQLAlchemy engine manages database connections:

```python
engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,
    echo=False
)
```

**Configuration:**
- `pool_pre_ping=True` - Validates connections before use
- `echo=False` - Set to True for SQL logging in development
- Connection pooling managed by SQLAlchemy

### Session Factory

The session factory creates database sessions:

```python
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
```

**Configuration:**
- `autocommit=False` - Requires explicit commit
- `autoflush=False` - Manual flush control
- Bound to engine

### Dependency Injection

The `get_db()` function provides database sessions to FastAPI endpoints:

```python
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Usage:**
```python
from app.core.database import get_db

@router.get("/fields")
def get_fields(db: Session = Depends(get_db)):
    fields = db.query(Field).all()
    return fields
```

## Database URL Processing

The `get_database_url()` function processes the database URL:

```python
def get_database_url() -> str:
    raw_url = settings.DATABASE_URL
    url = raw_url.replace("%%", "%")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url
```

**Processing:**
- Replaces double percent signs (encoding issues)
- Converts `postgres://` to `postgresql://` for psycopg2

## Connection Pooling

SQLAlchemy manages connection pooling:

**Default Pool Settings:**
- Pool size: 5 connections
- Max overflow: 10 connections
- Pool timeout: 30 seconds
- Pool recycle: 3600 seconds (1 hour)

**For Production:**
Consider configuring pool size based on expected load:
```python
engine = create_engine(
    get_database_url(),
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True
)
```

## Session Lifecycle

1. Request starts → Session created via `get_db()`
2. Operations performed using session
3. Transaction committed (explicit or automatic)
4. Request ends → Session closed automatically

## Transaction Management

### Automatic Transactions

```python
db.add(entity)
db.commit()  # Explicit commit
```

### Transaction Rollback

```python
try:
    db.add(entity)
    db.commit()
except Exception:
    db.rollback()
    raise
```

### Context Manager (for complex operations)

```python
with db.begin():
    db.add(entity1)
    db.add(entity2)
    # Auto commit on success, rollback on exception
```

## Database Engines

### PostgreSQL (Production)

```env
DATABASE_URL=postgresql://user:password@localhost:5432/agritwin
```

### SQLite (Development/Testing)

```env
DATABASE_URL=sqlite:///./agritwin.db
```

## Alembic Integration

Alembic uses the database URL from environment:

```python
# migrations/env.py
from app.core.config import settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
```

## Notes

- Always use `get_db()` dependency injection
- Close sessions automatically (handled by dependency)
- Use `pool_pre_ping=True` for connection validation
- Set `echo=True` only in development for SQL logging
- Configure pool size for production workloads
- Use environment variables for database credentials
