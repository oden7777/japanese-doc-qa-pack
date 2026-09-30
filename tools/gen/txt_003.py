"""Generate cases/txt-003: strings whose NFC/NFD/NFKC/NFKD forms differ.

Each line is one string, and the ground truth records its four Unicode
normalization forms as computed with Python's unicodedata. All characters
have been assigned since long before Unicode 4.1, so by the Unicode
normalization stability policy these results do not change between versions.

Usage: python tools/gen/txt_003.py
"""

from __future__ import annotations

import unicodedata

from common import UNICODE_VERSION, case_dir, text_value, write_expected

CASE_ID = "txt-003"
LINES = [
    "ｶﾞ",          # half-width katakana + half-width voiced sound mark
    "ﾊﾟ",          # half-width katakana + half-width semi-voiced sound mark
    "ＡＢＣ１２３",  # full-width Latin letters and digits
    "①",           # circled digit one
    "㈱",           # parenthesized ideograph stock
    "㍻",           # square era name Heisei
    "゛",           # U+309B spacing voiced sound mark (not combining)
    "\ufa19",       # CJK compatibility ideograph 神 (NFC maps it to U+795E)
]
FORMS = ("NFC", "NFD", "NFKC", "NFKD")


def normalizations() -> list[dict[str, object]]:
    return [
        {"line": n, "source": text_value(s),
         **{form.lower(): text_value(unicodedata.normalize(form, s)) for form in FORMS}}
        for n, s in enumerate(LINES, start=1)
    ]


def self_check(raw: bytes) -> None:
    text = raw.decode("utf-8")
    assert not text.startswith("\ufeff") and "\r" not in text and text.endswith("\n")
    assert text[:-1].split("\n") == LINES
    for s in LINES:
        assert unicodedata.normalize("NFKC", s) != s, f"NFKC must change {s!r}"
    assert unicodedata.normalize("NFC", "\ufa19") == "神"
    assert unicodedata.normalize("NFKC", "ｶﾞ") == "ガ"


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
            "UTF-8 text with one string per line whose NFKC/NFKD (and in one case NFC) forms "
            "differ from the source: half-width katakana with voiced marks, full-width "
            "alphanumerics, circled and parenthesized characters, a square era name, a spacing "
            "voiced sound mark and a CJK compatibility ideograph."
        ),
        input_file="input.txt",
        mime_type="text/plain",
        encoding="UTF-8",
        features=["nfkc", "nfkd", "halfwidth-katakana", "fullwidth-alphanumerics",
                  "compatibility-characters", "cjk-compatibility-ideograph"],
        ground_truth={
            "encoding": "UTF-8",
            "bom": False,
            "line_terminator": "LF",
            "trailing_newline": True,
            "unicode_version": UNICODE_VERSION,
            "lines": [text_value(s) for s in LINES],
            "normalizations": normalizations(),
        },
    )


if __name__ == "__main__":
    main()
