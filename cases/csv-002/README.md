# csv-002: UTF-8 CSV with BOM, width variants and compatibility characters

## Purpose

Tests how a CSV reader and any later text processing handle a UTF-8 CSV with
a byte order mark, as written by spreadsheet software, whose cells mix
character widths and Unicode compatibility characters. Typical things to
check: BOM handling (the first header cell must not start with U+FEFF),
half-width katakana with separate voiced sound marks, full-width Latin letters
and digits, and characters such as ㈱ and ㌔ that change under NFKC.

## Input

- `input.csv`: UTF-8 with BOM (`EF BB BF`), 6 records × 4 columns, header row
  `区分,表記,読み,数量`, every record ends with CRLF, no quoted fields.
- Rows:
  - 半角カナ: `ｶﾞｸｾｲ証` / `ｶﾞｸｾｲｼｮｳ` (half-width katakana; `ﾞ` U+FF9E is a
    separate character)
  - 全角英数: `ＡＢＣ１２３`, quantity `２` (full-width digit)
  - 互換文字: `㈱サンプル` (U+3231 PARENTHESIZED IDEOGRAPH STOCK)
  - 単位記号: `㌔グラム` (U+3314 SQUARE KIRO)
  - 丸数字: `①②③`

## Features

`utf-8`, `bom`, `crlf`, `halfwidth-katakana`, `fullwidth-alphanumerics`,
`compatibility-characters`

## Ground truth

`expected.json` → `ground_truth` records:

- `encoding` `UTF-8`, `bom: true`, `record_terminator: CRLF`,
  `has_header: true`, `row_count` (including the header) and `column_count`.
- `rows`: every cell as text plus Unicode code points. The BOM is **not** part
  of the first cell.

The ground truth keeps the characters exactly as stored. It does not say
whether a reader should normalise widths or compatibility characters; see
txt-003 for normalisation results.

## How it was generated

`python tools/gen/csv_002.py`. Python's `csv.writer` (CRLF line terminator)
writes the rows, which are encoded as UTF-8 with a BOM prepended. The script
decodes the bytes again, parses them with `csv.reader`, and checks that the
rows match, that there is exactly one BOM, that every record ends with CRLF and
that no cell starts with `=`, `+`, `-` or `@`, before it writes the file and
`expected.json`.

## Notes

- The "quantity" column holds text such as `２`; the ground truth does not
  claim it is a number.
- All values are fictional. No cell can act as a spreadsheet formula.
