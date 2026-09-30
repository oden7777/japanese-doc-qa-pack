"""Generate cases/txt-002: Japanese text containing invisible characters.

Each line hides one invisible or special space character inside ordinary
Japanese text. No bidirectional control characters are used.

Usage: python tools/gen/txt_002.py
"""

from __future__ import annotations

import unicodedata

from common import UNICODE_VERSION, case_dir, text_value, write_expected

CASE_ID = "txt-002"
LINES = [
    "東京\u200b都",          # ZERO WIDTH SPACE
    "価格\u00a0100円",       # NO-BREAK SPACE
    "全角\u3000スペース",    # IDEOGRAPHIC SPACE
    "文中\ufeffのBOM",       # ZERO WIDTH NO-BREAK SPACE (not at file start)
    "単語\u2060結合子",      # WORD JOINER
]
INVISIBLE = {"\u200b", "\u00a0", "\u3000", "\ufeff", "\u2060"}
BIDI_CONTROLS = {chr(c) for c in [*range(0x202A, 0x202F), *range(0x2066, 0x206A), 0x200E, 0x200F, 0x061C]}


def invisible_chars() -> list[dict[str, object]]:
    return [
        {"line": n, "index": i, "codepoint": f"U+{ord(ch):04X}", "name": unicodedata.name(ch)}
        for n, line in enumerate(LINES, start=1)
        for i, ch in enumerate(line)
        if ch in INVISIBLE
    ]


def self_check(raw: bytes) -> None:
    assert not raw.startswith(b"\xef\xbb\xbf"), "U+FEFF must not be at the start of the file"
    text = raw.decode("utf-8")
    assert "\r" not in text and text.endswith("\n")
    lines = text[:-1].split("\n")
    assert lines == LINES
    assert not BIDI_CONTROLS & set(text), "bidirectional controls are not allowed"
    for entry in invisible_chars():
        assert f"U+{ord(lines[entry['line'] - 1][entry['index']]):04X}" == entry["codepoint"]
    assert {"\u200b", "\u00a0", "\u3000"} <= set(text)


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
            "UTF-8 text in which each line hides one invisible or special space character "
            "inside Japanese text: ZERO WIDTH SPACE, NO-BREAK SPACE, IDEOGRAPHIC SPACE, "
            "ZERO WIDTH NO-BREAK SPACE (mid-text, not a BOM) and WORD JOINER."
        ),
        input_file="input.txt",
        mime_type="text/plain",
        encoding="UTF-8",
        features=["zero-width-space", "no-break-space", "ideographic-space", "zero-width-no-break-space",
                  "word-joiner", "invisible-characters"],
        ground_truth={
            "encoding": "UTF-8",
            "bom": False,
            "line_terminator": "LF",
            "trailing_newline": True,
            "unicode_version": UNICODE_VERSION,
            "lines": [text_value(s) for s in LINES],
            "invisible_chars": invisible_chars(),
        },
    )


if __name__ == "__main__":
    main()
