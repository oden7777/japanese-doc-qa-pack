"""Regression tests for tools/verify.py.

Each test copies the real pack to a temporary directory, breaks one thing,
and checks the exit code and the case id that verify.py reports.

Run from the repository root: python -m unittest discover tests
"""

from __future__ import annotations

import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import verify  # noqa: E402


class VerifyTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        for name in ("cases", "schema"):
            shutil.copytree(ROOT / name, self.root / name)
        shutil.copy(ROOT / "manifest.json", self.root / "manifest.json")

    def run_verify(self) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = verify.main(["--root", str(self.root)])
        return code, out.getvalue()

    def edit_expected(self, case_id: str, change) -> None:
        path = self.root / "cases" / case_id / "expected.json"
        doc = json.loads(path.read_text(encoding="utf-8"))
        change(doc)
        path.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")

    def assert_only_failure(self, out: str, case_id: str, reason: str) -> None:
        failed = {line.split(":")[0].removeprefix("FAIL ") for line in out.splitlines() if line.startswith("FAIL ")}
        self.assertEqual(failed, {case_id}, out)
        self.assertIn(f"FAIL {case_id}: {reason}", out)
        self.assertIn("9 passed, 1 failed", out)

    def test_unmodified_pack_passes(self) -> None:
        code, out = self.run_verify()
        self.assertEqual(code, 0, out)
        self.assertIn("10 passed, 0 failed", out)

    def test_changed_input_byte_is_sha256_mismatch(self) -> None:
        path = self.root / "cases" / "pdf-002" / "input.pdf"
        data = bytearray(path.read_bytes())
        data[len(data) // 2] ^= 0x01
        path.write_bytes(bytes(data))
        code, out = self.run_verify()
        self.assertEqual(code, 1, out)
        self.assert_only_failure(out, "pdf-002", "sha256 mismatch")

    def test_missing_readme_fails(self) -> None:
        (self.root / "cases" / "txt-001" / "README.md").unlink()
        code, out = self.run_verify()
        self.assertEqual(code, 1, out)
        self.assert_only_failure(out, "txt-001", "missing README.md")

    def test_missing_features_fails_schema(self) -> None:
        self.edit_expected("csv-002", lambda d: d.pop("features"))
        code, out = self.run_verify()
        self.assertEqual(code, 1, out)
        self.assert_only_failure(out, "csv-002", "schema:")

    def test_invalid_category_fails_schema(self) -> None:
        self.edit_expected("pdf-001", lambda d: d.update(category="pdfx"))
        code, out = self.run_verify()
        self.assertEqual(code, 1, out)
        self.assert_only_failure(out, "pdf-001", "schema:")

    def test_csv_without_encoding_fails_schema(self) -> None:
        self.edit_expected("csv-001", lambda d: d["input"].pop("encoding"))
        code, out = self.run_verify()
        self.assertEqual(code, 1, out)
        self.assert_only_failure(out, "csv-001", "schema:")

    def test_broken_manifest_exits_2(self) -> None:
        (self.root / "manifest.json").write_text("{not json", encoding="utf-8")
        code, out = self.run_verify()
        self.assertEqual(code, 2, out)
        self.assertIn("ERROR manifest.json", out)


if __name__ == "__main__":
    unittest.main()
