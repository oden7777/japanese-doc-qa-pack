"""Generate cases/csv-001: a Windows-31J (CP932) CSV with quoting edge cases.

Records end with CRLF. The file contains a quoted field with a comma, an
escaped double quote, a field with an embedded LF, quoted amounts with a
thousands separator, and characters whose Unicode mapping differs between
CP932 and Shift_JIS (JIS X 0208).

Usage: python tools/gen/csv_001.py
"""

from __future__ import annotations

import csv
import io

from common import case_dir, text_value, write_expected

CASE_ID = "csv-001"
CODEC = "cp932"
ROWS = [
    ["商品コード", "商品名", "備考", "金額"],
    ["A001", "りんご", "青森産, 大玉", "1,200"],
    ["A002", '15"モニター', "在庫～残りわずか", "3,980"],
    ["A003", "ノート", "1行目\n2行目", "150"],
    ["A004", "①番棚の髙級ペン", "型番AB－12", "500"],
    ["A005", "消しゴム", "", "80"],
]
# Characters whose decoded code point depends on the mapping table.
MAPPING_SENSITIVE = ["～", "－", "①", "髙"]
FORMULA_PREFIXES = ("=", "+", "-", "@")


def encode() -> bytes:
    buf = io.StringIO(newline="")
    csv.writer(buf, lineterminator="\r\n", quoting=csv.QUOTE_MINIMAL).writerows(ROWS)
    return buf.getvalue().encode(CODEC)


def codepoint(ch: str) -> str:
    return f"U+{ord(ch):04X}"


def mapping_entries() -> list[dict[str, object]]:
    entries = []
    for ch in MAPPING_SENSITIVE:
        raw = ch.encode(CODEC)
        try:
            shift_jis = codepoint(raw.decode("shift_jis"))
        except UnicodeDecodeError:
            shift_jis = None  # not defined in Shift_JIS (JIS X 0208)
        row, column = next((r, c) for r, cells in enumerate(ROWS, start=1)
                           for c, cell in enumerate(cells, start=1) if ch in cell)
        entries.append({"bytes_hex": raw.hex(), "cp932": codepoint(ch), "shift_jis": shift_jis,
                        "row": row, "column": column})
    return entries


def self_check(raw: bytes) -> None:
    assert not raw.startswith(b"\xef\xbb\xbf")
    try:
        raw.decode("utf-8")
        raise AssertionError("must not be valid UTF-8")
    except UnicodeDecodeError:
        pass
    text = raw.decode(CODEC)
    assert list(csv.reader(io.StringIO(text, newline=""))) == ROWS
    assert text.count("\r\n") == len(ROWS), "every record must end with CRLF"
    assert text.replace("\r\n", "").count("\n") == 1, "exactly one in-field LF"
    for cells in ROWS:
        for cell in cells:
            assert not cell.startswith(FORMULA_PREFIXES), cell


def main() -> None:
    directory = case_dir(CASE_ID)
    directory.mkdir(parents=True, exist_ok=True)
    raw = encode()
    self_check(raw)
    (directory / "input.csv").write_bytes(raw)
    assert (directory / "input.csv").read_bytes() == raw
    write_expected(
        CASE_ID,
        category="csv",
        description=(
            "Windows-31J (CP932) CSV with CRLF records: a quoted field containing a comma, "
            "an escaped double quote, a field with an embedded LF, quoted amounts with a "
            "thousands separator, an empty field, and characters whose Unicode mapping "
            "differs between CP932 and Shift_JIS."
        ),
        input_file="input.csv",
        mime_type="text/csv",
        encoding="Windows-31J",
        features=["windows-31j", "cp932", "quoted-field", "embedded-comma", "escaped-quote",
                  "embedded-newline", "crlf", "cp932-mapping-differences"],
        ground_truth={
            "encoding": "Windows-31J",
            "decoder": "Python codec cp932 (Microsoft CP932 mapping)",
            "bom": False,
            "record_terminator": "CRLF",
            "in_field_newline": "LF",
            "has_header": True,
            "row_count": len(ROWS),
            "column_count": len(ROWS[0]),
            "rows": [[text_value(cell) for cell in cells] for cells in ROWS],
            "mapping_sensitive": mapping_entries(),
        },
    )


if __name__ == "__main__":
    main()
