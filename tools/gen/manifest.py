"""Build manifest.json from every cases/*/expected.json.

Each entry copies id, category and features from the case's expected.json
and adds its path, sorted by id. Run it after regenerating any case.

Usage: python tools/gen/manifest.py
"""

from __future__ import annotations

import json

from common import ROOT

CASE_IDS = [
    "archive-001", "csv-001", "csv-002", "ocr-001", "pdf-001",
    "pdf-002", "pdf-003", "txt-001", "txt-002", "txt-003",
]


def main() -> None:
    found = sorted(p.parent.name for p in (ROOT / "cases").glob("*/expected.json"))
    assert found == sorted(CASE_IDS), f"expected exactly the 10 Lite cases, found {found}"
    entries = []
    for case_id in found:
        expected = json.loads((ROOT / "cases" / case_id / "expected.json").read_text(encoding="utf-8"))
        assert expected["id"] == case_id, f"{case_id}: expected.json id is {expected['id']!r}"
        entries.append({
            "id": case_id,
            "category": expected["category"],
            "path": f"cases/{case_id}",
            "features": expected["features"],
        })
    manifest = {"cases": entries}
    (ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
