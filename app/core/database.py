from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import get_database_url

# Create the SQLAlchemy engine
# psycopg is used as the driver (postgresql://...)
engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,
    echo=False  # Set to True to log SQL statements in development
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency generator for database sessions.
    Ensures that sessions are closed after a request is handled.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
