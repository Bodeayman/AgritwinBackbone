"""
AgriTwin Mock Server
====================
A lightweight FastAPI mock that loads scenario data from JSON files and serves
responses that exactly mirror the real AgriTwin API contract.

Usage:
    MOCK_SCENARIO=default uvicorn mock_server.server:app --port 8001 --reload
    
    -- or from the mock_server directory --
    start.bat default          (Windows)
    ./start.sh default         (Linux / Mac)

POST / PUT / DELETE mutations are applied to in-memory state.
Restart the server (or call POST /mock/reset) to reload from the JSON files.
"""

from __future__ import annotations

import copy
import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import Body, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# ─── Configuration ─────────────────────────────────────────────────────────────

MOCK_SCENARIO = os.getenv("MOCK_SCENARIO", "default")
DATA_DIR = Path(__file__).parent / "data" / "scenarios"
MOCK_PORT = int(os.getenv("MOCK_PORT", "8001"))

# Any client can use this static token – it is never validated cryptographically.
MOCK_JWT_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJzdWIiOiIxIiwiZW1haWwiOiJmYXJtZXJAZXhhbXBsZS5jb20iLCJleHAiOjk5OTk5OTk5OTl9"
    ".MOCK_SIGNATURE_NOT_FOR_PRODUCTION"
)


# ─── In-Memory State ────────────────────────────────────────────────────────────


class MockState:
    """
    Holds all scenario data in memory keyed by entity name.

    - Starts populated from the JSON files in the chosen scenario folder.
    - POST / PUT / DELETE endpoints mutate this in-memory store so the mock
      behaves like a real stateful API within a single server session.
    - Call ``state.load(scenario)`` (or hit ``POST /mock/reset``) to wipe and
      reload from disk.
    """

    def __init__(self) -> None:
        self._data: Dict[str, Any] = {}
        self._id_counters: Dict[str, int] = {}

    # ── Loading ─────────────────────────────────────────────────────────────

    def load(self, scenario: str) -> None:
        scenario_dir = DATA_DIR / scenario
        if not scenario_dir.exists():
            available = sorted(d.name for d in DATA_DIR.iterdir() if d.is_dir())
            raise FileNotFoundError(
                f"Scenario '{scenario}' not found in {DATA_DIR}. "
                f"Available scenarios: {available}"
            )
        self._data.clear()
        self._id_counters.clear()

        for json_file in scenario_dir.glob("*.json"):
            entity = json_file.stem
            with open(json_file, encoding="utf-8") as fh:
                self._data[entity] = json.load(fh)

        # Seed ID counters from max existing IDs so new records don't clash.
        for entity, records in self._data.items():
            if isinstance(records, list) and records:
                max_id = max(
                    (r.get("id", 0) for r in records if isinstance(r, dict)),
                    default=0,
                )
                self._id_counters[entity] = max_id

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _next_id(self, entity: str) -> int:
        self._id_counters[entity] = self._id_counters.get(entity, 0) + 1
        return self._id_counters[entity]

    def _list(self, entity: str) -> list:
        if entity not in self._data:
            self._data[entity] = []
        return self._data[entity]

    # ── Read ─────────────────────────────────────────────────────────────────

    def get_list(self, entity: str) -> list:
        return copy.deepcopy(self._list(entity))

    def get_by_id(self, entity: str, record_id: int) -> Optional[dict]:
        for r in self._list(entity):
            if isinstance(r, dict) and r.get("id") == record_id:
                return copy.deepcopy(r)
        return None

    def filter_by(self, entity: str, **kwargs) -> list:
        return [
            copy.deepcopy(r)
            for r in self._list(entity)
            if isinstance(r, dict) and all(r.get(k) == v for k, v in kwargs.items())
        ]

    def raw(self, key: str) -> Any:
        return copy.deepcopy(self._data.get(key))

    # ── Write ────────────────────────────────────────────────────────────────

    def add(self, entity: str, record: dict) -> dict:
        record = copy.deepcopy(record)
        record["id"] = self._next_id(entity)
        record.setdefault("created_at", _now())
        self._list(entity).append(record)
        return copy.deepcopy(record)

    def update(self, entity: str, record_id: int, updates: dict) -> Optional[dict]:
        records = self._list(entity)
        for i, r in enumerate(records):
            if isinstance(r, dict) and r.get("id") == record_id:
                records[i] = {**r, **updates, "updated_at": _now()}
                return copy.deepcopy(records[i])
        return None

    def delete(self, entity: str, record_id: int) -> bool:
        before = len(self._list(entity))
        self._data[entity] = [
            r for r in self._list(entity)
            if not (isinstance(r, dict) and r.get("id") == record_id)
        ]
        return len(self._data[entity]) < before

    @property
    def summary(self) -> dict:
        return {
            k: len(v) if isinstance(v, list) else type(v).__name__
            for k, v in self._data.items()
        }


# ─── Utilities ─────────────────────────────────────────────────────────────────


def _now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _paginate(items: list, skip: int, limit: int) -> list:
    return items[skip: skip + limit]


def _404(msg: str):
    raise HTTPException(status_code=404, detail=msg)


def _resolve_ai_model(model_id: Optional[int]) -> Optional[dict]:
    if model_id is None:
        return None
    return state.get_by_id("ai_models", model_id)


def _get_or_create_model(name: Optional[str], version: Optional[str]) -> Optional[int]:
    """Mirror the real API's auto-resolve logic."""
    if not name or not version:
        return None
    existing = [
        m for m in state.get_list("ai_models")
        if m.get("name") == name and m.get("version") == version
    ]
    if existing:
        return existing[0]["id"]
    new_model = state.add("ai_models", {
        "name": name,
        "version": version,
        "description": f"Auto-registered: {name} {version}",
        "created_at": _now(),
    })
    return new_model["id"]


def _require_bearer(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Add header: Authorization: Bearer <token>",
        )


def _require_api_key(x_api_key: Optional[str] = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=403, detail="Missing X-API-Key header")


# ─── App Bootstrap ──────────────────────────────────────────────────────────────

state = MockState()
state.load(MOCK_SCENARIO)

app = FastAPI(
    title="AgriTwin Mock Server",
    description=(
        f"Mock API — active scenario: **`{MOCK_SCENARIO}`**\n\n"
        "Responses exactly mirror the real AgriTwin API contract.\n\n"
        "**JWT**: Use `Authorization: Bearer <any_string>` — any non-empty token is accepted.\n\n"
        "**API Key**: Use `X-API-Key: <any_string>` — any non-empty value is accepted.\n\n"
        "**Reset data**: `POST /mock/reset` reloads the active scenario JSON files.\n\n"
        "**See scenarios**: `GET /mock/scenario`"
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ════════════════════════════════════════════════════════════════════════════════
# HEALTH
# ════════════════════════════════════════════════════════════════════════════════

@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "ok",
        "mock_scenario": MOCK_SCENARIO,
        "server": "AgriTwin Mock",
        "data_summary": state.summary,
    }


# ════════════════════════════════════════════════════════════════════════════════
# MOCK CONTROL
# ════════════════════════════════════════════════════════════════════════════════

@app.get("/mock/scenario", tags=["Mock Control"])
def get_scenario():
    """Returns the active scenario name and record counts per entity."""
    return {"active_scenario": MOCK_SCENARIO, "data_summary": state.summary}


@app.post("/mock/reset", tags=["Mock Control"])
def reset_scenario():
    """Reload the active scenario from disk — discards all in-memory mutations."""
    state.load(MOCK_SCENARIO)
    return {"message": f"Scenario '{MOCK_SCENARIO}' reloaded from disk.", "data_summary": state.summary}


# ════════════════════════════════════════════════════════════════════════════════
# AUTH  (POST /api/v1/auth/*)
# ════════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/auth/register", status_code=201, tags=["01 · Auth"])
def register(body: dict = Body(...)):
    auth = state.raw("auth") or {}
    user_tmpl = auth.get("user", {"id": 1, "email": "farmer@example.com", "is_active": True, "role": "user"})
    return {**user_tmpl, "email": body.get("email", user_tmpl.get("email"))}


@app.post("/api/v1/auth/login", tags=["01 · Auth"])
def login(body: dict = Body(...)):
    auth = state.raw("auth") or {}
    return {
        "access_token": MOCK_JWT_TOKEN,
        "token_type": "bearer",
        "user": auth.get("user", {"id": 1, "email": body.get("email", "farmer@example.com"), "role": "user"}),
    }


# ════════════════════════════════════════════════════════════════════════════════
# FARMS  (JWT)
# ════════════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/farms", tags=["02 · Farms"])
def list_farms(skip: int = 0, limit: int = 100, authorization: Optional[str] = Header(None)):
    _require_bearer(authorization)
    return _paginate(state.get_list("farms"), skip, limit)


@app.post("/api/v1/farms", status_code=201, tags=["02 · Farms"])
def create_farm(body: dict = Body(...), authorization: Optional[str] = Header(None)):
    _require_bearer(authorization)
    return state.add("farms", {
        "owner_id": 1,
        "name": body.get("name", "New Farm"),
        "location": body.get("location"),
        "created_at": _now(),
        "updated_at": _now(),
    })


@app.get("/api/v1/farms/{farm_id}", tags=["02 · Farms"])
def get_farm(farm_id: int, authorization: Optional[str] = Header(None)):
    _require_bearer(authorization)
    farm = state.get_by_id("farms", farm_id)
    if not farm:
        _404(f"Farm {farm_id} not found")
    return farm


# ════════════════════════════════════════════════════════════════════════════════
# FIELDS  (JWT)
# ════════════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/fields", tags=["03 · Fields"])
def list_fields(skip: int = 0, limit: int = 100, authorization: Optional[str] = Header(None)):
    _require_bearer(authorization)
    return _paginate(state.get_list("fields"), skip, limit)


@app.post("/api/v1/fields", status_code=201, tags=["03 · Fields"])
def create_field(body: dict = Body(...), authorization: Optional[str] = Header(None)):
    _require_bearer(authorization)
    return state.add("fields", {
        "farm_id": body.get("farm_id", 1),
        "name": body.get("name", "New Field"),
        "crop_type": body.get("crop_type"),
        "created_at": _now(),
        "updated_at": _now(),
    })


@app.get("/api/v1/fields/{field_id}", tags=["03 · Fields"])
def get_field(field_id: int, authorization: Optional[str] = Header(None)):
    _require_bearer(authorization)
    field = state.get_by_id("fields", field_id)
    if not field:
        _404(f"Field {field_id} not found")
    return field


@app.put("/api/v1/fields/{field_id}", tags=["03 · Fields"])
def update_field(field_id: int, body: dict = Body(...), authorization: Optional[str] = Header(None)):
    _require_bearer(authorization)
    updated = state.update("fields", field_id, body)
    if not updated:
        _404(f"Field {field_id} not found")
    return updated


@app.delete("/api/v1/fields/{field_id}", status_code=204, tags=["03 · Fields"])
def delete_field(field_id: int, authorization: Optional[str] = Header(None)):
    _require_bearer(authorization)
    if not state.delete("fields", field_id):
        _404(f"Field {field_id} not found")


# ── GPS Boundary ──────────────────────────────────────────────────────────────

@app.post("/api/v1/fields/{field_id}/boundary", tags=["03 · Fields"])
def set_boundary(field_id: int, body: dict = Body(...), authorization: Optional[str] = Header(None)):
    _require_bearer(authorization)
    if not state.get_by_id("fields", field_id):
        _404(f"Field {field_id} not found")
    coords = body.get("coordinates", [])
    existing = state.filter_by("field_boundaries", field_id=field_id)
    if existing:
        return state.update("field_boundaries", existing[0]["id"], {
            "coordinates": coords,
            "area_hectares": round(len(coords[0]) * 0.247, 4) if coords else 0,
        })
    return state.add("field_boundaries", {
        "field_id": field_id,
        "coordinates": coords,
        "area_hectares": round(len(coords[0]) * 0.247, 4) if coords else 0,
        "created_at": _now(),
        "updated_at": _now(),
    })


@app.get("/api/v1/fields/{field_id}/boundary", tags=["03 · Fields"])
def get_boundary_jwt(field_id: int, authorization: Optional[str] = Header(None)):
    _require_bearer(authorization)
    if not state.get_by_id("fields", field_id):
        _404(f"Field {field_id} not found")
    boundaries = state.filter_by("field_boundaries", field_id=field_id)
    return boundaries[0] if boundaries else None


# ════════════════════════════════════════════════════════════════════════════════
# INTERNAL INGESTION  (X-API-Key)  POST /api/fields/{id}/...
# ════════════════════════════════════════════════════════════════════════════════

@app.post("/api/fields/{field_id}/sensor-readings", status_code=201, tags=["04 · Internal Ingestion"])
def ingest_sensor(field_id: int, body: dict = Body(...), x_api_key: Optional[str] = Header(None)):
    _require_api_key(x_api_key)
    return state.add("sensor_readings", {
        "field_id": field_id,
        "sensor_id": body.get("sensor_id"),
        "soil_moisture": body.get("soil_moisture"),
        "soil_temperature": body.get("soil_temperature"),
        "air_temperature": body.get("air_temperature"),
        "humidity": body.get("humidity"),
        "soil_ph": body.get("soil_ph"),
        "electrical_conductivity": body.get("electrical_conductivity"),
        "recorded_at": body.get("recorded_at", _now()),
        "created_at": _now(),
    })


@app.post("/api/fields/{field_id}/satellite-observations", status_code=201, tags=["04 · Internal Ingestion"])
def ingest_satellite(field_id: int, body: dict = Body(...), x_api_key: Optional[str] = Header(None)):
    _require_api_key(x_api_key)
    model_id = _get_or_create_model(body.get("model_name"), body.get("model_version"))
    return state.add("satellite_observations", {
        "field_id": field_id,
        "model_id": model_id,
        "ndvi": body.get("ndvi"),
        "ndmi": body.get("ndmi"),
        "evi": body.get("evi"),
        "status": body.get("status", "processed"),
        "image_reference": body.get("image_reference"),
        "captured_at": body.get("captured_at", _now()),
        "created_at": _now(),
        "ai_model": _resolve_ai_model(model_id),
    })


@app.post("/api/fields/{field_id}/diagnoses", status_code=201, tags=["04 · Internal Ingestion"])
def ingest_diagnosis(field_id: int, body: dict = Body(...), x_api_key: Optional[str] = Header(None)):
    _require_api_key(x_api_key)
    model_id = _get_or_create_model(body.get("model_name"), body.get("model_version"))
    return state.add("diagnoses", {
        "field_id": field_id,
        "model_id": model_id,
        "image_reference": body.get("image_reference"),
        "crop_type": body.get("crop_type"),
        "disease_or_pest": body.get("disease_or_pest", "Unknown"),
        "severity": body.get("severity"),
        "confidence": body.get("confidence"),
        "latitude": body.get("latitude"),
        "longitude": body.get("longitude"),
        "status": body.get("status", "processed"),
        "diagnosed_at": body.get("diagnosed_at", _now()),
        "explanation": body.get("explanation"),
        "treatment_suggestion": body.get("treatment_suggestion"),
        "created_at": _now(),
        "ai_model": _resolve_ai_model(model_id),
    })


@app.post("/api/fields/{field_id}/irrigation-plans", status_code=201, tags=["04 · Internal Ingestion"])
def ingest_irrigation(field_id: int, body: dict = Body(...), x_api_key: Optional[str] = Header(None)):
    _require_api_key(x_api_key)
    model_id = _get_or_create_model(body.get("model_name"), body.get("model_version"))
    return state.add("irrigation_plans", {
        "field_id": field_id,
        "model_id": model_id,
        "water_requirement": body.get("water_requirement", 0.0),
        "unit": body.get("unit", "mm"),
        "recommended_date": body.get("recommended_date", str(date.today())),
        "created_at": _now(),
        "ai_model": _resolve_ai_model(model_id),
    })


@app.post("/api/fields/{field_id}/yield-predictions", status_code=201, tags=["04 · Internal Ingestion"])
def ingest_yield(field_id: int, body: dict = Body(...), x_api_key: Optional[str] = Header(None)):
    _require_api_key(x_api_key)
    model_id = _get_or_create_model(body.get("model_name"), body.get("model_version"))
    return state.add("yield_predictions", {
        "field_id": field_id,
        "model_id": model_id,
        "crop_type": body.get("crop_type", "Unknown"),
        "predicted_yield": body.get("predicted_yield", 0.0),
        "unit": body.get("unit", "kg/ha"),
        "confidence": body.get("confidence"),
        "status": body.get("status", "processed"),
        "prediction_date": body.get("prediction_date", str(date.today())),
        "model_version": body.get("model_version"),
        "created_at": _now(),
        "ai_model": _resolve_ai_model(model_id),
    })


@app.post("/api/fields/{field_id}/crop-mix-recommendations", status_code=201, tags=["04 · Internal Ingestion"])
def ingest_crop_mix(field_id: int, body: dict = Body(...), x_api_key: Optional[str] = Header(None)):
    _require_api_key(x_api_key)
    model_id = _get_or_create_model(body.get("model_name"), body.get("model_version"))
    return state.add("crop_mix_recommendations", {
        "field_id": field_id,
        "model_id": model_id,
        "expected_profit": body.get("expected_profit"),
        "binding_constraint": body.get("binding_constraint"),
        "status": body.get("status", "processed"),
        "created_at": _now(),
        "allocations": body.get("allocations", []),
        "ai_model": _resolve_ai_model(model_id),
    })


# ════════════════════════════════════════════════════════════════════════════════
# AI MODELS  (X-API-Key)  /api/models
# ════════════════════════════════════════════════════════════════════════════════

@app.post("/api/models", status_code=201, tags=["05 · AI Models"])
def create_ai_model(body: dict = Body(...), x_api_key: Optional[str] = Header(None)):
    _require_api_key(x_api_key)
    existing = [
        m for m in state.get_list("ai_models")
        if m.get("name") == body.get("name") and m.get("version") == body.get("version")
    ]
    if existing:
        return existing[0]
    return state.add("ai_models", {
        "name": body.get("name"),
        "version": body.get("version"),
        "description": body.get("description"),
        "created_at": _now(),
    })


@app.get("/api/models", tags=["05 · AI Models"])
def list_ai_models(skip: int = 0, limit: int = 100, x_api_key: Optional[str] = Header(None)):
    _require_api_key(x_api_key)
    return _paginate(state.get_list("ai_models"), skip, limit)


# ════════════════════════════════════════════════════════════════════════════════
# INTERNAL READ ENDPOINTS  (X-API-Key)  GET /api/fields/{id}/...
# ════════════════════════════════════════════════════════════════════════════════

@app.get("/api/fields/{field_id}", tags=["06 · Internal Read"])
def get_internal_field(field_id: int, x_api_key: Optional[str] = Header(None)):
    _require_api_key(x_api_key)
    field = state.get_by_id("fields", field_id)
    if not field:
        _404(f"Field {field_id} not found")
    return field


@app.get("/api/fields/{field_id}/boundary", tags=["06 · Internal Read"])
def get_internal_boundary(field_id: int, x_api_key: Optional[str] = Header(None)):
    _require_api_key(x_api_key)
    boundaries = state.filter_by("field_boundaries", field_id=field_id)
    return boundaries[0] if boundaries else None


@app.get("/api/fields/{field_id}/sensor-readings", tags=["06 · Internal Read"])
def get_sensor_readings(
    field_id: int,
    skip: int = 0,
    limit: int = 100,
    latest: bool = Query(False),
    x_api_key: Optional[str] = Header(None),
):
    _require_api_key(x_api_key)
    items = sorted(
        state.filter_by("sensor_readings", field_id=field_id),
        key=lambda r: r.get("recorded_at", ""),
        reverse=True,
    )
    return items[:1] if latest else _paginate(items, skip, limit)


@app.get("/api/fields/{field_id}/satellite-observations", tags=["06 · Internal Read"])
def get_satellite_observations(
    field_id: int,
    skip: int = 0,
    limit: int = 100,
    latest: bool = Query(False),
    x_api_key: Optional[str] = Header(None),
):
    _require_api_key(x_api_key)
    items = sorted(
        state.filter_by("satellite_observations", field_id=field_id),
        key=lambda r: r.get("captured_at", ""),
        reverse=True,
    )
    return items[:1] if latest else _paginate(items, skip, limit)


@app.get("/api/fields/{field_id}/diagnoses", tags=["06 · Internal Read"])
def get_diagnoses(
    field_id: int,
    skip: int = 0,
    limit: int = 100,
    latest: bool = Query(False),
    x_api_key: Optional[str] = Header(None),
):
    _require_api_key(x_api_key)
    items = sorted(
        state.filter_by("diagnoses", field_id=field_id),
        key=lambda r: r.get("diagnosed_at", ""),
        reverse=True,
    )
    return items[:1] if latest else _paginate(items, skip, limit)


@app.get("/api/fields/{field_id}/irrigation-plans", tags=["06 · Internal Read"])
def get_irrigation_plans(
    field_id: int,
    skip: int = 0,
    limit: int = 100,
    latest: bool = Query(False),
    x_api_key: Optional[str] = Header(None),
):
    _require_api_key(x_api_key)
    items = sorted(
        state.filter_by("irrigation_plans", field_id=field_id),
        key=lambda r: r.get("recommended_date", ""),
        reverse=True,
    )
    return items[:1] if latest else _paginate(items, skip, limit)


@app.get("/api/fields/{field_id}/yield-predictions", tags=["06 · Internal Read"])
def get_yield_predictions(
    field_id: int,
    skip: int = 0,
    limit: int = 100,
    latest: bool = Query(False),
    x_api_key: Optional[str] = Header(None),
):
    _require_api_key(x_api_key)
    items = sorted(
        state.filter_by("yield_predictions", field_id=field_id),
        key=lambda r: r.get("prediction_date", ""),
        reverse=True,
    )
    return items[:1] if latest else _paginate(items, skip, limit)


@app.get("/api/fields/{field_id}/crop-mix-recommendations", tags=["06 · Internal Read"])
def get_crop_mix_recommendations(
    field_id: int,
    skip: int = 0,
    limit: int = 100,
    latest: bool = Query(False),
    x_api_key: Optional[str] = Header(None),
):
    _require_api_key(x_api_key)
    items = sorted(
        state.filter_by("crop_mix_recommendations", field_id=field_id),
        key=lambda r: r.get("created_at", ""),
        reverse=True,
    )
    return items[:1] if latest else _paginate(items, skip, limit)


@app.get("/api/farms/{farm_id}/fields", tags=["06 · Internal Read"])
def get_farm_fields(
    farm_id: int,
    skip: int = 0,
    limit: int = 100,
    x_api_key: Optional[str] = Header(None),
):
    _require_api_key(x_api_key)
    if not state.get_by_id("farms", farm_id):
        _404(f"Farm {farm_id} not found")
    return _paginate(state.filter_by("fields", farm_id=farm_id), skip, limit)


@app.get("/api/farms/{farm_id}/crop-mixes/latest", tags=["06 · Internal Read"])
def get_farm_latest_crop_mixes(farm_id: int, x_api_key: Optional[str] = Header(None)):
    _require_api_key(x_api_key)
    if not state.get_by_id("farms", farm_id):
        _404(f"Farm {farm_id} not found")
    results = []
    for field in state.filter_by("fields", farm_id=farm_id):
        recs = sorted(
            state.filter_by("crop_mix_recommendations", field_id=field["id"]),
            key=lambda r: r.get("created_at", ""),
            reverse=True,
        )
        results.append({
            "field_id": field["id"],
            "field_name": field["name"],
            "latest_recommendation": recs[0] if recs else None,
        })
    return results


@app.get("/api/fields/{field_id}/state", tags=["06 · Internal Read"])
def get_field_state(field_id: int, x_api_key: Optional[str] = Header(None)):
    _require_api_key(x_api_key)
    field = state.get_by_id("fields", field_id)
    if not field:
        _404(f"Field {field_id} not found")

    def _latest(entity: str, sort_key: str) -> Optional[dict]:
        items = sorted(
            state.filter_by(entity, field_id=field_id),
            key=lambda r: r.get(sort_key, ""),
            reverse=True,
        )
        return items[0] if items else None

    boundaries = state.filter_by("field_boundaries", field_id=field_id)
    return {
        "field": field,
        "boundary": boundaries[0] if boundaries else None,
        "latest_sensor_reading": _latest("sensor_readings", "recorded_at"),
        "latest_satellite_observation": _latest("satellite_observations", "captured_at"),
        "latest_diagnosis": _latest("diagnoses", "diagnosed_at"),
        "latest_irrigation_plan": _latest("irrigation_plans", "recommended_date"),
        "latest_yield_prediction": _latest("yield_predictions", "prediction_date"),
        "latest_crop_mix_recommendation": _latest("crop_mix_recommendations", "created_at"),
    }


# ─── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=MOCK_PORT, reload=True)
