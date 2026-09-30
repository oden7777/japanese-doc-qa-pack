"""Generate cases/txt-001: Japanese strings in both NFC and NFD form.

Lines come in pairs that look the same but differ in code points: the first
of each pair is precomposed (NFC), the second decomposed (NFD).

Usage: python tools/gen/txt_001.py
"""

from __future__ import annotations

import unicodedata

from common import UNICODE_VERSION, case_dir, text_value, write_expected

CASE_ID = "txt-001"
WORDS = ["が", "パ", "ガイド"]
LINES = [form for w in WORDS for form in (unicodedata.normalize("NFC", w), unicodedata.normalize("NFD", w))]


def line_value(s: str) -> dict[str, object]:
    return {**text_value(s),
            "is_nfc": unicodedata.is_normalized("NFC", s),
            "is_nfd": unicodedata.is_normalized("NFD", s)}


def self_check(raw: bytes) -> None:
    text = raw.decode("utf-8")
    assert not text.startswith("\ufeff") and "\r" not in text and text.endswith("\n")
    assert text[:-1].split("\n") == LINES
    assert LINES[0] == "が" and LINES[1] == "か\u3099", "が must appear as U+304C and U+304B U+3099"
    for nfc, nfd in zip(LINES[0::2], LINES[1::2]):
        assert nfc != nfd and unicodedata.normalize("NFC", nfd) == nfc


def main() -> None:
    directory = case_dir(CASE_ID)
    directory.mkdir(parents=True, exist_ok=True)
    raw = "".join(line + "\n" for line in LINES).encode("utf-8")
    self_check(raw)
    (directory / "input.txt").write_bytes(raw)
    assert (directory / "input.txt").read_bytes() == raw
    write_expected(
        CASE_ID,
        category="txt",
        description=(
            "UTF-8 text with Japanese strings that look identical but are stored as NFC "
            "(precomposed) on one line and NFD (base character plus combining voiced or "
            "semi-voiced sound mark) on the next, e.g. U+304C versus U+304B U+3099."
        ),
        input_file="input.txt",
        mime_type="text/plain",
        encoding="UTF-8",
        features=["nfc", "nfd", "combining-dakuten", "combining-handakuten", "canonical-equivalence"],
        ground_truth={
            "encoding": "UTF-8",
            "bom": False,
            "line_terminator": "LF",
            "trailing_newline": True,
            "unicode_version": UNICODE_VERSION,
            "lines": [line_value(s) for s in LINES],
            "canonically_equivalent_pairs": [[i, i + 1] for i in range(1, len(LINES), 2)],
        },
    )


if __name__ == "__main__":
    main()
