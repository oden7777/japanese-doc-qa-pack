"""Helpers shared by the per-case fixture scripts in tools/gen/.

Only what every case needs lives here: hashing, code point lists, and writing
expected.json. Scripts never touch the network and only write inside their
own cases/<id>/ directory.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FONT_PATH = ROOT / "fonts" / "BIZUDGothic-Regular.ttf"
UNICODE_VERSION = unicodedata.unidata_version

_CASE_ID = re.compile(r"^(pdf|ocr|csv|txt|archive)-[0-9]{3}$")


def case_dir(case_id: str) -> Path:
    if not _CASE_ID.fullmatch(case_id):
        raise ValueError(f"invalid case id: {case_id!r}")
    return ROOT / "cases" / case_id


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def codepoints(s: str) -> list[str]:
    return [f"U+{ord(c):04X}" for c in s]


def text_value(s: str) -> dict[str, object]:
    return {"text": s, "codepoints": codepoints(s)}


def write_expected(
    case_id: str,
    *,
    category: str,
    description: str,
    input_file: str,
    mime_type: str,
    encoding: str | None,
    features: list[str],
    ground_truth: dict[str, object],
) -> Path:
    """Write cases/<id>/expected.json. Call only after the input passed its self-check."""
    directory = case_dir(case_id)
    input_path = directory / input_file
    if not input_path.is_file():
        raise FileNotFoundError(input_path)
    input_info: dict[str, str] = {"file": input_file, "mime_type": mime_type}
    if encoding is not None:
        input_info["encoding"] = encoding
    input_info["sha256"] = sha256_file(input_path)
    doc = {
        "id": case_id,
        "category": category,
        "description": description,
        "input": input_info,
        "features": features,
        "ground_truth": ground_truth,
    }
    path = directory / "expected.json"
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
