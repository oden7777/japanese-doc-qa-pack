"""Generate cases/csv-002: a UTF-8 CSV with BOM and width/compatibility variants.

Records end with CRLF. Cells mix half-width katakana (with separate voiced
sound marks), full-width Latin letters and digits, and Unicode compatibility
characters such as ㈱ and ㌔.

Usage: python tools/gen/csv_002.py
"""

from __future__ import annotations

import csv
import io

from common import case_dir, text_value, write_expected

CASE_ID = "csv-002"
BOM = b"\xef\xbb\xbf"
ROWS = [
    ["区分", "表記", "読み", "数量"],
    ["半角カナ", "ｶﾞｸｾｲ証", "ｶﾞｸｾｲｼｮｳ", "1"],
    ["全角英数", "ＡＢＣ１２３", "エービーシー", "２"],
    ["互換文字", "㈱サンプル", "カブシキガイシャサンプル", "1"],
    ["単位記号", "㌔グラム", "キログラム", "3"],
    ["丸数字", "①②③", "マルスウジ", "3"],
]
FORMULA_PREFIXES = ("=", "+", "-", "@")


def encode() -> bytes:
    buf = io.StringIO(newline="")
    csv.writer(buf, lineterminator="\r\n", quoting=csv.QUOTE_MINIMAL).writerows(ROWS)
    return BOM + buf.getvalue().encode("utf-8")


def self_check(raw: bytes) -> None:
    assert raw.startswith(BOM) and not raw[3:].startswith(BOM)
    text = raw[3:].decode("utf-8")
    assert list(csv.reader(io.StringIO(text, newline=""))) == ROWS
    assert text.count("\r\n") == len(ROWS) and text.count("\n") == len(ROWS), "CRLF records only"
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
            "UTF-8 CSV with a byte order mark and CRLF records. Cells mix half-width katakana "
            "with separate voiced sound marks, full-width Latin letters and digits, and Unicode "
            "compatibility characters (㈱, ㌔, circled digits)."
        ),
        input_file="input.csv",
        mime_type="text/csv",
        encoding="UTF-8",
        features=["utf-8", "bom", "crlf", "halfwidth-katakana", "fullwidth-alphanumerics",
                  "compatibility-characters"],
        ground_truth={
            "encoding": "UTF-8",
            "bom": True,
            "record_terminator": "CRLF",
            "has_header": True,
            "row_count": len(ROWS),
            "column_count": len(ROWS[0]),
            "rows": [[text_value(cell) for cell in cells] for cells in ROWS],
        },
    )


if __name__ == "__main__":
    main()
