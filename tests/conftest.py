import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from app.main import app
from app.core.database import engine, SessionLocal, get_db
from app.core.storage import StorageService, get_storage
from app.models.base import Base


@pytest.fixture(scope="session", autouse=True)
def mock_init_storage_on_startup():
    """Mock init_storage on startup so test client starts instantly without MinIO network retries."""
    with patch("app.main.init_storage") as mock_init:
        mock_init.return_value = None
        yield mock_init


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """
    Creates test database tables and cleans them up after test session.
    """
    try:
        with engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
    except Exception as e:
        print(f"Skipping PostGIS extension creation: {e}")

    Base.metadata.create_all(bind=engine)
    yield
    try:
        with engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS crop_mix_allocations CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS crop_mix_recommendations CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS yield_predictions CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS irrigation_plans CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS diagnoses CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS disease_detections CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS satellite_observations CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS satellite_data CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS sensor_readings CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS field_boundaries CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS crop_cycles CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS weather CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS fields CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS farms CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
    except Exception as e:
        print(f"Cleanup error: {e}")


@pytest.fixture
def db_session():
    """
    Runs each test inside a database transaction, rolling back modifications
    after completion.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def mock_storage():
    """
    Mocks storage operations to eliminate network dependencies on MinIO during testing.
    """
    service = MagicMock(spec=StorageService)
    service.upload_file.return_value = "locations/mock-uuid/mock_image.jpg"
    service.get_download_url.return_value = "http://localhost:9000/agritwin-bucket/locations/mock-uuid/mock_image.jpg?token=mock_sig"
    service.delete_file.return_value = None
    return service


@pytest.fixture
def client(db_session, mock_storage):
    """
    Provides a FastAPI TestClient with database session and storage service overrides.
    """
    def _override_get_db():
        yield db_session

    def _override_get_storage():
        yield mock_storage

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_storage] = _override_get_storage

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
