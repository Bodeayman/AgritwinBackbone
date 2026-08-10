from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.core.storage import init_storage
from app.models.base import Base
import app.models  # noqa: F401
from app.api.router import api_router
from app.api.internal_router import internal_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Set up CORS middleware
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.BACKEND_CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Register routes
    # 1. Farmer routes under /api/v1 (JWT Bearer Auth)
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # 2. Internal Module routes under /api (X-API-Key Auth)
    app.include_router(internal_router, prefix="/api")

    @app.on_event("startup")
    def on_startup():
        print("Initializing services...")
        
        # 1. Enable PostGIS extension on startup if not already enabled
        try:
            with engine.begin() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
                print("PostGIS extension checked/enabled.")
        except Exception as e:
            print(f"Error checking/enabling PostGIS extension: {e}")
            print("Note: If using SQLite/spatialite during local tests, this will fail safely.")

        # 2. Create database tables if they do not exist
        try:
            Base.metadata.create_all(bind=engine)
            print("Database tables initialized.")
        except Exception as e:
            print(f"Error creating database tables: {e}")

        # 3. Create MinIO object storage buckets
        init_storage()

    @app.get("/", tags=["Health"])
    def health_check():
        return {
            "status": "healthy",
            "project": settings.PROJECT_NAME,
            "version": "1.0.0"
        }

    # Custom OpenAPI schema documenting both BearerAuth and ApiKeyAuth
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title=settings.PROJECT_NAME,
            version="1.0.0",
            description=(
                "Farm Twin Core API with Dual Authentication:\n\n"
                "1. **Farmer Endpoints (`/api/v1/`)**: Authenticated via JWT Bearer Token in `Authorization: Bearer <token>` header.\n"
                "2. **Internal Internship Modules (`/api/`)**: Authenticated via `X-API-Key: <api_key>` header."
            ),
            routes=app.routes,
        )
        if "components" not in openapi_schema:
            openapi_schema["components"] = {}
        if "securitySchemes" not in openapi_schema["components"]:
            openapi_schema["components"]["securitySchemes"] = {}

        openapi_schema["components"]["securitySchemes"]["HTTPBearer"] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT Access Token obtained from POST /api/v1/auth/login",
        }
        openapi_schema["components"]["securitySchemes"]["ApiKeyAuth"] = {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API Key for internal internship modules (e.g., INTERN_2_API_KEY, INTERN_3_API_KEY, etc.)",
        }
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    return app


app = create_app()
