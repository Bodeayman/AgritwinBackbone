import sys, os

# ─────────────────────────────────────────────────────────────────────────────
# CRITICAL: point tests at the isolated test database BEFORE any app modules
# are imported so the SQLAlchemy engine is created with the test URL.
# This prevents pytest from ever touching the live `agritwin` database.
# ─────────────────────────────────────────────────────────────────────────────
TEST_DATABASE_URL = (
    "postgresql://postgres:REDACTED_DB_PASSWORD@localhost:5432/agritwin_test"
)
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db
from app.core.storage import StorageService, get_storage
from app.models.base import Base
from app import models as app_models  # noqa: F401 — ensure all models are registered


# ── Test-only engine pointing at agritwin_test ────────────────────────────────
test_engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def mock_init_storage_on_startup():
    """Mock init_storage on startup so test client starts instantly without MinIO."""
    with patch("app.main.init_storage") as mock_init:
        mock_init.return_value = None
        yield mock_init


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """
    Creates all tables in agritwin_test before the test session and drops
    them cleanly afterwards.  The live `agritwin` database is never touched.
    """
    # Enable PostGIS on the test DB
    try:
        with test_engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            print("PostGIS extension checked/enabled on agritwin_test.")
    except Exception as e:
        print(f"Skipping PostGIS on test DB: {e}")

    # Create all app tables
    Base.metadata.create_all(bind=test_engine)
    print("Database tables initialized on agritwin_test.")

    yield

    # Tear down — drop everything in the test DB only
    Base.metadata.drop_all(bind=test_engine)
    print("agritwin_test tables dropped after test session.")


@pytest.fixture
def db_session():
    """
    Runs each test inside a transaction on agritwin_test, rolling back
    all changes after the test completes so tests stay isolated.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)

    yield session

    session.close()
    try:
        transaction.rollback()
    except Exception:
        pass
    connection.close()


@pytest.fixture
def mock_storage():
    """Mock MinIO storage so tests never need a real MinIO instance."""
    service = MagicMock(spec=StorageService)
    service.upload_file.return_value = "locations/mock-uuid/mock_image.jpg"
    service.get_download_url.return_value = (
        "http://localhost:9000/agritwin-bucket/locations/mock-uuid/mock_image.jpg"
        "?token=mock_sig"
    )
    service.delete_file.return_value = None
    return service


@pytest.fixture
def client(db_session, mock_storage):
    """
    FastAPI TestClient wired to the agritwin_test session and mocked storage.
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
