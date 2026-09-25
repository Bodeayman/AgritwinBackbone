import asyncio

import pytest
from PIL import Image

from app import config, vlm


class FakeResponse:
    def __init__(self, status_code: int, data: dict | str):
        self.status_code = status_code
        self._data = data

    @property
    def text(self) -> str:
        return self._data if isinstance(self._data, str) else "{}"

    def json(self) -> dict:
        return self._data if isinstance(self._data, dict) else {}


class FakeClient:
    def __init__(self, response: FakeResponse, error: Exception | None = None):
        self.response = response
        self.error = error

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def post(self, url, **kwargs):
        if self.error is not None:
            raise self.error
        return self.response


async def _run(coro):
    return await asyncio.get_event_loop().run_until_complete(coro)


@pytest.fixture(autouse=True)
def _reset_vlm_url():
    saved = config.settings.VLM_URL
    yield
    config.settings.VLM_URL = saved


def _crop() -> Image.Image:
    return Image.new("RGB", (64, 64), (12, 34, 56))


def _patch_client(response, error=None):
    import app.vlm as vlm_mod

    client = FakeClient(response, error)
    return __import__("unittest.mock", fromlist=["patch"]).patch.object(
        vlm_mod.httpx, "AsyncClient", lambda **kw: client
    )


def test_no_vlm_url_sets_ok_false():
    config.settings.VLM_URL = ""
    result = asyncio.run(vlm.confirm_with_vlm(_crop()))
    assert result["ok"] is False
    assert "not configured" in result["info"]


def test_success_parses_vlm_fields():
    config.settings.VLM_URL = "http://vlm-classifier:8000"
    fake = FakeResponse(
        200,
        {
            "disease_name": "Gray Leaf Spot",
            "max_score": 0.91,
            "scores": {"Gray Leaf Spot": 0.91, "Leaf Rust": 0.05},
            "missing_scores": [],
        },
    )
    with _patch_client(fake):
        result = asyncio.run(vlm.confirm_with_vlm(_crop()))
    assert result["ok"] is True
    assert result["disease_name"] == "Gray Leaf Spot"
    assert result["max_score"] == 0.91
    assert result["scores"]["Leaf Rust"] == 0.05
    assert result["info"] == "vlm confirmed"


def test_non_200_sets_ok_false_with_status():
    config.settings.VLM_URL = "http://vlm-classifier:8000"
    fake = FakeResponse(503, "classifier unavailable")
    with _patch_client(fake):
        result = asyncio.run(vlm.confirm_with_vlm(_crop()))
    assert result["ok"] is False
    assert "503" in result["info"]


def test_network_error_sets_ok_false():
    config.settings.VLM_URL = "http://vlm-classifier:8000"
    with _patch_client(None, error=TimeoutError("boom")):
        result = asyncio.run(vlm.confirm_with_vlm(_crop()))
    assert result["ok"] is False
    assert "TimeoutError" in result["info"]