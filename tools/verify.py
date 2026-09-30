"""Verify the fixture pack without parsing any fixture content.

For every case listed in manifest.json this checks only three things:
the listed files exist, expected.json passes the JSON Schema, and the input
file's SHA-256 matches expected.json. It never touches the network.

Usage: python tools/verify.py [--root DIR]
Exit codes: 0 all cases pass, 1 at least one case fails,
2 manifest.json or the schema cannot be read.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path

from jsonschema import Draft202012Validator

MANIFEST = "manifest.json"
SCHEMA = "schema/expected.schema.json"
ENTRY_KEYS = ("id", "category", "path", "features")


@dataclass(frozen=True)
class CaseResult:
    id: str
    errors: tuple[str, ...]  # empty means the case passed


class LoadError(Exception):
    pass


def _load_json(path: Path, label: str) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, RecursionError) as e:
        raise LoadError(f"ERROR {label}: {e}") from e


def _inside(base: Path, rel: str) -> Path | None:
    """Resolve rel under base, or None if it is absolute or escapes base."""
    if Path(rel).is_absolute():
        return None
    target = (base / rel).resolve()
    if target != base and base not in target.parents:
        return None
    return target


def _check_case(root: Path, entry: object, validator: Draft202012Validator) -> CaseResult:
    if not isinstance(entry, dict):
        return CaseResult("?", ("manifest entry is not an object",))
    case_id = str(entry.get("id", "?"))
    missing_keys = [k for k in ENTRY_KEYS if k not in entry]
    if missing_keys:
        return CaseResult(case_id, (f"manifest entry missing {', '.join(missing_keys)}",))
    if not isinstance(entry["path"], str) or (case_dir := _inside(root, entry["path"])) is None:
        return CaseResult(case_id, (f"path outside the pack: {entry['path']!r}",))
    if not case_dir.is_dir():
        return CaseResult(case_id, (f"missing directory {entry['path']}",))

    errors: list[str] = []
    if not (case_dir / "README.md").is_file():
        errors.append("missing README.md")
    expected_path = case_dir / "expected.json"
    if not expected_path.is_file():
        errors.append("missing expected.json")
        return CaseResult(case_id, tuple(errors))
    try:
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        errors.append(f"expected.json is not valid JSON: {e}")
        return CaseResult(case_id, tuple(errors))

    for err in sorted(validator.iter_errors(expected), key=lambda e: e.json_path):
        errors.append(f"schema: {err.json_path}: {err.message}")

    info = expected.get("input") if isinstance(expected, dict) else None
    file_name = info.get("file") if isinstance(info, dict) else None
    want = info.get("sha256") if isinstance(info, dict) else None
    if isinstance(file_name, str) and isinstance(want, str):
        input_path = _inside(case_dir, file_name)
        if input_path is None:
            errors.append(f"input.file outside the case directory: {file_name!r}")
        elif not input_path.is_file():
            errors.append(f"missing {file_name}")
        else:
            got = hashlib.sha256(input_path.read_bytes()).hexdigest()
            if got != want:
                errors.append(f"sha256 mismatch (expected {want}, actual {got})")
    return CaseResult(case_id, tuple(errors))


def verify(root: Path) -> list[CaseResult]:
    """Check every manifest entry. Raises LoadError if manifest or schema is unusable."""
    root = root.resolve()
    manifest = _load_json(root / MANIFEST, MANIFEST)
    schema = _load_json(root / SCHEMA, SCHEMA)
    if not isinstance(manifest, dict) or not isinstance(manifest.get("cases"), list):
        raise LoadError(f'ERROR {MANIFEST}: expected an object with a "cases" list')
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as e:  # SchemaError, or anything else from a malformed schema
        raise LoadError(f"ERROR {SCHEMA}: {e}") from e
    validator = Draft202012Validator(schema)
    results = []
    for entry in manifest["cases"]:
        try:
            results.append(_check_case(root, entry, validator))
        except Exception as e:  # never crash on one bad case
            case_id = str(entry.get("id", "?")) if isinstance(entry, dict) else "?"
            results.append(CaseResult(case_id, (f"unexpected error: {e}",)))
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify the fixture pack (existence, schema, SHA-256).")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1],
                        help="pack root directory (default: repository root)")
    args = parser.parse_args(argv)
    try:
        results = verify(args.root)
    except LoadError as e:
        print(e)
        return 2
    for r in results:
        if r.errors:
            for msg in r.errors:
                print(f"FAIL {r.id}: {msg}")
        else:
            print(f"OK {r.id}")
    failed = sum(1 for r in results if r.errors)
    print(f"{len(results) - failed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
