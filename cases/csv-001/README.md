# csv-001: Windows-31J CSV with quoting edge cases

## Purpose

Tests how a CSV reader handles a typical Japanese business CSV saved in
Windows-31J (CP932): the encoding itself, RFC 4180-style quoting, and
characters that decode to different Unicode code points depending on the
mapping table. Typical things to check: encoding detection, commas and double
quotes inside quoted fields, a line break inside a field, CRLF record
endings, empty fields, and whether `～`, `－`, `①` and `髙` survive decoding
and round-tripping.

## Input

- `input.csv`: Windows-31J, no BOM, 6 records × 4 columns, header row
  `商品コード,商品名,備考,金額`.
- Every record ends with CRLF. One field contains a bare LF (`1行目` LF `2行目`).
- Fields are quoted only when needed: `"青森産, 大玉"` (comma), `"15""モニター"`
  (escaped double quote), the field with the LF, and the amounts `"1,200"` and
  `"3,980"` (thousands separator). Row A005 has an empty field.
- Mapping-sensitive characters (byte sequence → CP932 / Shift_JIS):

| Char | Bytes | CP932 (Microsoft) | Shift_JIS (JIS X 0208) |
|------|-------|-------------------|------------------------|
| ～ | `81 60` | U+FF5E FULLWIDTH TILDE | U+301C WAVE DASH |
| － | `81 7C` | U+FF0D FULLWIDTH HYPHEN-MINUS | U+2212 MINUS SIGN |
| ① | `87 40` | U+2460 (NEC special character) | not defined |
| 髙 | `EE E0` | U+9AD9 (NEC-selected IBM extension) | not defined |

## Features

`windows-31j`, `cp932`, `quoted-field`, `embedded-comma`, `escaped-quote`,
`embedded-newline`, `crlf`, `cp932-mapping-differences`

## Ground truth

`expected.json` → `ground_truth` records:

- `encoding` `Windows-31J` and `decoder`: the values were decoded with
  Python's `cp932` codec, which follows Microsoft's CP932 mapping.
- `bom: false`, `record_terminator: CRLF`, `in_field_newline: LF`,
  `has_header: true`, `row_count` (including the header) and `column_count`.
- `rows`: every cell after unquoting (surrounding quotes removed, `""`
  turned into `"`), as text plus Unicode code points.
- `mapping_sensitive`: for each character in the table above, its bytes, its
  CP932 code point, its Shift_JIS code point (`null` if undefined), and its
  `row` / `column` (1-based, header is row 1).

The ground truth does not say how a reader should report the embedded LF,
trim spaces, or convert the amounts to numbers.

## How it was generated

`python tools/gen/csv_001.py`. Python's `csv.writer` (minimal quoting, CRLF
line terminator) writes the rows, which are then encoded with `cp932`. The
script decodes the bytes again, parses them with `csv.reader`, and checks
that the rows match, that every record ends with CRLF, that there is exactly
one in-field LF, that the file is not valid UTF-8, and that no cell starts with
`=`, `+`, `-` or `@`, before it writes the file and `expected.json`.

## Notes

- `髙` has two encodings in CP932 (`EE E0` and the IBM extension `FB FC`).
  Both decode to U+9AD9; Python's `cp932` encoder writes `EE E0`, which is what
  this file contains.
- Product names and codes are fictional. No cell can act as a spreadsheet
  formula.
