"""
Disease Classification Agent — ChatLeafDisease (ChatLD) CoT Scoring
=======================================================================
Implements Section 2.3 / Supplementary Material C2 of the ChatLeafDisease
paper: a single-model, training-free disease classification agent guided
by a Chain-of-Thought prompt (task definition -> scoring rules -> important
notes -> disease classification).

THIS VERSION calls the Google Gemini API instead of a local Ollama VLM.
Everything else (prompt, knowledge base format, output parsing) is unchanged
from the local version -- only the model-calling layer changed.

===========================================================================
WHAT YOU NEED TO CHANGE TO USE THIS: just set GEMINI_API_KEY below (or set
it as an environment variable of the same name). Nothing else is required.
===========================================================================

Get a free API key at: https://aistudio.google.com  (no credit card needed
for the free tier -- see GEMINI_MODEL comment below for which models are
free and their current rate limits, which Google changes periodically).

Run:
    python disease_classification_agent.py diagnose "<path to leaf image>" [--kb knowledge_base.json]
    python disease_classification_agent.py list_kb [--kb knowledge_base.json]
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Configuration -- EDIT HERE
# ---------------------------------------------------------------------------

# NOTE: this MUST match --output in text_preprocessing.py unless overridden
# with --kb on this script's CLI.
KB_JSON_PATH = r"./knowledge_base.json"

# ============================ PUT YOUR KEY HERE ============================
# Get one free at https://aistudio.google.com -> "Get API key".
# You can either paste it directly here, OR (safer) leave this as "" and set
# an environment variable instead:
#   Windows (PowerShell):  setx GEMINI_API_KEY "your-key-here"   (restart terminal after)
#   macOS/Linux:            export GEMINI_API_KEY="your-key-here"
GEMINI_API_KEY = ""   # <-- paste your key between the quotes, or leave blank and use env var
# =============================================================================

GEMINI_API_KEY = GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")

# Free-tier model as of writing -- check https://ai.google.dev/gemini-api/docs/rate-limits
# for the current free model list/limits, these change periodically.
GEMINI_MODEL = "gemini-3.6-flash"

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
GEMINI_TIMEOUT = 120

# Simple rate-limit safety net: min seconds to wait between calls, and how
# many times to retry on HTTP 429 (rate limited) with exponential backoff.
MIN_SECONDS_BETWEEN_CALLS = 4.5   # ~13 requests/min, under most free-tier RPM caps
MAX_RETRIES_ON_429 = 5
_last_call_time = 0.0


# ---------------------------------------------------------------------------
# C2 prompt -- CoT Disease Classification Agent (verbatim from Supplementary C2)
# ---------------------------------------------------------------------------

COT_SYSTEM_PROMPT = """###Task Definition
You will receive descriptive prompt text of disease symptoms and image of leaf diseases.
As an experienced botanist, your task is to assess whether the leaf disease in the image
satisfies the semantic meaning of the text prompt according to the scoring criteria.

###Scoring Rule
[Scoring Criteria]
When evaluating whether the representation of leaf disease in the image conforms to the
description of the prompt text, it is crucial to consider the consistency of the visual content of
the disease spots in the image with the text description. It can be evaluated from the size,
shape, color, leaf morphology and other characteristics of the spot:
1. The text prompt includes the description of pathological features corresponding to the front
of the diseased leaf, and is scored according to the consistency between the image features
and the text description. If the image features are in high consistency with the text description,
a higher score should be obtained, and vice versa.
2. Due to the inconsistency of leaf disease severity, special attention should be paid to the
inconsistency and conflict between image information and text description, which is an
important basis for judging consistency

[Scoring Range]
Score based on the consistency of image features and text descriptions, with a score range of
0.0-100.0:
The score for this section should be derived from how well the text description matches the
features of the image. When there is a conflict between the text description and the image
features, the overall score should be biased towards a lower score (for example, the lesion is
described as circular, while the image shows the lesion has no regular shape). Moderate
scores should be properly considered when you are unable to assess how well the text
description matches the features of the image (for example, when the text mentions features
on the back of the leaf, while the picture only has information on the front of the leaf). When the
text description matches the image features, the higher the degree of matching, the higher
the score.
Note that when a feature in the prompt text is a marker of the current disease judgment, the
impact of the feature on the total score should be improved

[Scoring Reassessment]
After the score is obtained, analyze the matching scoring process of the two diseases with the
highest score, check that the scoring scale is consistent, think about the previous tasks, and
judge whether the current score is reasonable and accurate. If there is any unreasonable score,
please adjust it.

###Input format
Every time you will receive some prompt text and an image.
Please carefully review image and these text prompt.

### Output Format
Score: [Disease Name,Score1;Disease Name,Score2....;Disease Name,Score(n)]
You must adhere to the specified output format, which means that only the scores need to be
output, excluding your analysis process.
And the order of the scores should correspond to the order of the diseases in the prompt text.
Finally, the category of image disease is judged by the maximum score, so there should not be
multiple categories of the same score.

###Important Notes
[Tips]
Assessing the consistency of the description does not require that the picture and the text be
exactly the same, but that they be relatively consistent in the image display and the text
description in order to obtain a higher score.You must be true to the evaluation criteria and your
own judgment, rather than tending to give neutral scores or very high scores.

[Internal Thinking]
Did you understand the task above?
Please summarize the tasks you need to do and show how
you will execute the detailed plan for the task.
"""

# COT_SYSTEM_PROMPT = "Which of these maize diseases is in the image based on the kb given in user prompt "

def build_classification_user_message(kb_records: list[dict]) -> str:
    """
    Builds the "descriptive prompt text of disease symptoms" the C2 prompt
    expects, listing every disease's condensed description in order --
    the model's output score order must follow this same order.
    """
    lines = ["Disease description prompt texts, in this order:\n"]
    for i, rec in enumerate(kb_records, start=1):
        lines.append(f"{i}. {rec['disease_name']}: {rec['description']}")
    lines.append(
        "\nScore the attached leaf image against each disease description above, "
        "following the scoring rules and reassessment steps, then respond using "
        "EXACTLY the specified output format."
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Knowledge base loading (produced by text_preprocessing.py)
# ---------------------------------------------------------------------------

def load_knowledge_base(kb_path: str = KB_JSON_PATH) -> list[dict]:
    path = Path(kb_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Knowledge base not found at '{kb_path}'. "
            "Run text_preprocessing.py first to generate it, or pass --kb "
            "pointing at the file it wrote."
        )
    with open(path, "r", encoding="utf-8-sig") as f:
        records = json.load(f)
    if not records:
        raise ValueError(f"Knowledge base at '{kb_path}' is empty.")
    return records


# ---------------------------------------------------------------------------
# VLM call -- Gemini API
# ---------------------------------------------------------------------------

def _guess_mime_type(image_path: str) -> str:
    ext = Path(image_path).suffix.lower()
    return {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
        ".gif": "image/gif",
    }.get(ext, "image/jpeg")


def classify_image_bytes(
    image_bytes: bytes,
    mime_type: str,
    kb_records: list[dict],
    api_key: str = None,
    model: str = None,
    base_url: str = None,
) -> dict:
    """Classify a leaf image from raw bytes using the Gemini VLM.

    Parameters
    ----------
    image_bytes : bytes
        Raw image file content.
    mime_type : str
        MIME type of the image, e.g. ``"image/jpeg"``.
    kb_records : list[dict]
        Knowledge base records produced by :func:`load_knowledge_base`.
    api_key : str, optional
        Gemini API key. Defaults to the global GEMINI_API_KEY.
    model : str, optional
        Gemini model name. Defaults to the global GEMINI_MODEL.
    base_url : str, optional
        Gemini API base URL. Defaults to the global GEMINI_BASE_URL.

    Returns
    -------
    dict
        Classification result with ``scores``, ``disease_name``,
        ``max_score``, ``_raw_output``, and optional error fields.
    """
    api_key = api_key or GEMINI_API_KEY
    model = model or GEMINI_MODEL
    base_url = base_url or GEMINI_BASE_URL

    if not api_key:
        raise RuntimeError(
            "No Gemini API key provided. Set GEMINI_API_KEY environment variable "
            "or pass it explicitly."
        )

    img_b64 = base64.b64encode(image_bytes).decode("utf-8")
    user_text = build_classification_user_message(kb_records)

    payload = {
        "system_instruction": {
            "parts": [
                {
                    "text": COT_SYSTEM_PROMPT
                }
            ]
        },

        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": user_text
                    },
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": img_b64
                        }
                    }
                ]
            }
        ],

        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 2000,

            "thinkingConfig": {
                "thinkingBudget": 200
            }
        }
    }
    raw = _gemini_generate(payload, api_key, model, base_url)
    print("\n========== RAW VLM OUTPUT ==========")
    print(raw)
    print("====================================\n")
    return _parse_score_output(raw, kb_records)


def classify_image(image_path: str, kb_records: list[dict]) -> dict:
    """Classify a leaf image on disk (convenience wrapper).

    Reads *image_path* and delegates to :func:`classify_image_bytes`.
    """
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    mime_type = _guess_mime_type(image_path)
    return classify_image_bytes(image_bytes, mime_type, kb_records)


def _gemini_generate(payload: dict, api_key: str, model: str, base_url: str) -> str:
    global _last_call_time

    url = f"{base_url}/{model}:generateContent?key={api_key}"

    for attempt in range(MAX_RETRIES_ON_429 + 1):
        # Simple pacing so we don't blow past the free-tier RPM limit.
        elapsed = time.time() - _last_call_time
        if elapsed < MIN_SECONDS_BETWEEN_CALLS:
            time.sleep(MIN_SECONDS_BETWEEN_CALLS - elapsed)

        try:
            resp = requests.post(url, json=payload, timeout=GEMINI_TIMEOUT)
        except requests.exceptions.ConnectionError:
            raise RuntimeError("Cannot reach the Gemini API. Check your internet connection.")
        finally:
            _last_call_time = time.time()

        if resp.status_code == 429:
            wait = (2 ** attempt) * 2  # 2s, 4s, 8s, 16s, 32s
            print(f"  Rate limited (429). Waiting {wait}s before retry "
                  f"({attempt + 1}/{MAX_RETRIES_ON_429})...")
            time.sleep(wait)
            continue

        if resp.status_code != 200:
            raise RuntimeError(f"Gemini API returned HTTP {resp.status_code}: {resp.text[:500]}")

        data = resp.json()
        try:
            candidate = data["candidates"][0]
            finish_reason = candidate.get("finishReason", "")
            parts = candidate.get("content", {}).get("parts", [])
            text = "".join(p.get("text", "") for p in parts).strip()
            if not text:
                raise RuntimeError(
                    f"Gemini returned an empty response (finishReason={finish_reason}). "
                    f"Raw: {json.dumps(data)[:500]}"
                )
            return text
        except (KeyError, IndexError):
            raise RuntimeError(f"Unexpected Gemini API response shape: {json.dumps(data)[:500]}")

    raise RuntimeError(f"Still rate limited after {MAX_RETRIES_ON_429} retries. Try again later.")


# ---------------------------------------------------------------------------
# Output parsing -- the paper's format:
#   Score: [Disease Name,Score1;Disease Name,Score2;...;Disease Name,Score(n)]
# ---------------------------------------------------------------------------

_NUMBER_RE = r"[-+]?\d+(?:\.\d+)?"


def _parse_score_output(raw: str, kb_records: list[dict]) -> dict:
    scores: dict[str, float] = {}

    # Aliases that tolerate the model dropping abbreviations in parentheses
    aliases = {}

    for rec in kb_records:
        name = rec["disease_name"]

        # Full name
        names_to_try = [name]

        # Remove parenthetical abbreviation:
        # "Northern Leaf Blight (NLB)" -> "Northern Leaf Blight"
        short_name = re.sub(r"\s*\([^)]*\)", "", name).strip()

        if short_name != name:
            names_to_try.append(short_name)

        aliases[name] = names_to_try

    for canonical_name, candidate_names in aliases.items():

        for candidate in candidate_names:
            pattern = re.compile(
                rf"{re.escape(candidate)}\s*[,:\-]\s*({_NUMBER_RE})",
                re.IGNORECASE
            )

            match = pattern.search(raw)

            if match:
                try:
                    scores[canonical_name] = float(match.group(1))
                    break
                except ValueError:
                    pass

    known_names = {rec["disease_name"] for rec in kb_records}
    missing = known_names - set(scores)

    if missing:
        print(f"WARNING: no score recovered for: {missing}")

    if not scores:
        return {
            "scores": {},
            "disease_name": None,
            "max_score": None,
            "_raw_output": raw,
            "_parse_error": (
                "Could not match any known disease name "
                "to a numeric score in the model output."
            ),
        }

    # IMPORTANT:
    # Do not classify if even one disease score is missing.
    if missing:
        return {
            "scores": scores,
            "disease_name": None,
            "max_score": None,
            "_raw_output": raw,
            "_missing_scores": sorted(missing),
            "_parse_error": (
                f"Missing scores for: {sorted(missing)}"
            ),
        }

    best_name = max(scores, key=scores.get)
    best_score = scores[best_name]

    return {
        "scores": scores,
        "disease_name": best_name,
        "max_score": best_score,
        "_raw_output": raw,
    }


# ---------------------------------------------------------------------------
# Pretty printing
# ---------------------------------------------------------------------------

def print_result(result: dict) -> None:
    print("=" * 70)
    print("DIAGNOSIS RESULT (ChatLD CoT scoring)")
    print("=" * 70)
    if result.get("_parse_error"):
        print(f"PARSE ERROR: {result['_parse_error']}")
        print("Raw model output:")
        print(result["_raw_output"])
    else:
        for name, score in sorted(result["scores"].items(), key=lambda kv: -kv[1]):
            marker = " <== max" if name == result["disease_name"] else ""
            print(f"  {name:30s} {score:6.1f}{marker}")
        print("-" * 70)
        print(f"Final classification: {result['disease_name']} "
              f"(score {result['max_score']:.1f})")
    print("=" * 70)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="ChatLeafDisease-style CoT disease classification agent "
                    "running on the Gemini API."
    )
    parser.add_argument(
        "--kb", default=KB_JSON_PATH,
        help=f"Path to the condensed knowledge base JSON produced by "
             f"text_preprocessing.py (default: {KB_JSON_PATH}).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    diagnose_parser = subparsers.add_parser("diagnose", help="Classify a leaf image.")
    diagnose_parser.add_argument("image_path", help="Path to the leaf image.")

    subparsers.add_parser("list_kb", help="List loaded knowledge base entries.")

    args = parser.parse_args()

    try:
        kb_records = load_knowledge_base(args.kb)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    if args.command == "diagnose":
        print(f"Loaded {len(kb_records)} disease description(s) from '{args.kb}'.")
        print(f"Calling {GEMINI_MODEL} for scoring ...\n")
        try:
            result = classify_image(args.image_path, kb_records)
        except Exception as e:
            print(f"ERROR: {e}")
            sys.exit(1)
        print_result(result)

    elif args.command == "list_kb":
        print(f"Found {len(kb_records)} disease record(s) in '{args.kb}':")
        for rec in kb_records:
            print(f"  - {rec.get('disease_id')}: {rec.get('disease_name')}")
            print(f"      {rec.get('description')}")


if __name__ == "__main__":
    main()