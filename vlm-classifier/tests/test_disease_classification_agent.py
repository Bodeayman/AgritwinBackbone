"""Offline tests for the VLM disease classification agent.

Covers the pure, non-network logic: knowledge-base loading, user-message
building, MIME guessing, and CoT output parsing. The Gemini HTTP call
itself is not tested (requires a live API key).
"""

import json
import sys
from pathlib import Path

import pytest

_SERVICE_DIR = Path(__file__).resolve().parent.parent
if str(_SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(_SERVICE_DIR))

import disease_classification_agent as dca

KB = [
    {
        "disease_name": "Maize Lethal Necrosis (MLN)",
        "description": "Severe yellowing and necrosis in maize.",
    },
    {
        "disease_name": "Northern Leaf Blight (NLB)",
        "description": "Long pale gray lesions on leaves.",
    },
    {
        "disease_name": "Healthy",
        "description": "No disease symptoms present.",
    },
]


def test_load_knowledge_base_returns_records(tmp_path):
    kb_file = tmp_path / "kb.json"
    kb_file.write_text(json.dumps(KB), encoding="utf-8")
    records = dca.load_knowledge_base(str(kb_file))
    assert records == KB


def test_load_knowledge_base_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        dca.load_knowledge_base(str(tmp_path / "nope.json"))


def test_load_knowledge_base_empty_raises(tmp_path):
    kb_file = tmp_path / "kb.json"
    kb_file.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError):
        dca.load_knowledge_base(str(kb_file))


def test_build_classification_user_message_lists_all_diseases():
    msg = dca.build_classification_user_message(KB)
    assert "Maize Lethal Necrosis (MLN)" in msg
    assert "Northern Leaf Blight (NLB)" in msg
    assert "Healthy" in msg
    assert msg.index("1.") < msg.index("2.") < msg.index("3.")


def test_guess_mime_type_by_extension():
    assert dca._guess_mime_type("leaf.png") == "image/png"
    assert dca._guess_mime_type("leaf.JPG") == "image/jpeg"
    assert dca._guess_mime_type("leaf.webp") == "image/webp"
    assert dca._guess_mime_type("leaf.unknown") == "image/jpeg"


def test_classify_image_bytes_requires_api_key():
    with pytest.raises(RuntimeError, match="No Gemini API key"):
        dca.classify_image_bytes(b"", "image/jpeg", KB, api_key="")


def test_parse_score_output_all_scores():
    raw = (
        "1. Maize Lethal Necrosis (MLN): 1.2\n"
        "2. Northern Leaf Blight (NLB): 0.8\n"
        "Healthy: 0.1"
    )
    result = dca._parse_score_output(raw, KB)
    assert result["scores"] == {
        "Maize Lethal Necrosis (MLN)": 1.2,
        "Northern Leaf Blight (NLB)": 0.8,
        "Healthy": 0.1,
    }
    assert result["disease_name"] == "Maize Lethal Necrosis (MLN)"
    assert result["max_score"] == 1.2
    assert "_parse_error" not in result


def test_parse_score_output_matches_name_without_parenthetical():
    raw = (
        "Maize Lethal Necrosis: 2.0\n"
        "Northern Leaf Blight: 0.5\n"
        "Healthy: 0.1"
    )
    result = dca._parse_score_output(raw, KB)
    assert result["scores"]["Maize Lethal Necrosis (MLN)"] == 2.0
    assert result["disease_name"] == "Maize Lethal Necrosis (MLN)"


def test_parse_score_output_missing_disease_not_classified():
    raw = "Maize Lethal Necrosis (MLN): 1.2 Northern Leaf Blight (NLB): 0.8"
    result = dca._parse_score_output(raw, KB)
    assert result["disease_name"] is None
    assert result["max_score"] is None
    assert result["_missing_scores"] == ["Healthy"]


def test_parse_score_output_no_match():
    raw = "no disease scores here at all"
    result = dca._parse_score_output(raw, KB)
    assert result["scores"] == {}
    assert result["disease_name"] is None
    assert "_parse_error" in result


def test_parse_score_output_tolerates_punctuation_variants():
    raw = "Maize Lethal Necrosis (MLN)-1.5, Northern Leaf Blight (NLB): 0.9, Healthy: 0.0"
    result = dca._parse_score_output(raw, KB)
    assert result["scores"]["Maize Lethal Necrosis (MLN)"] == 1.5
    assert result["scores"]["Healthy"] == 0.0