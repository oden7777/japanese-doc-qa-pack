# txt-001: the same Japanese strings in NFC and NFD

## Purpose

Tests how text processing handles canonically equivalent strings: Japanese
kana with voiced (゛) or semi-voiced (゜) sound marks, stored once
precomposed (NFC) and once decomposed (NFD). They usually look identical but
compare as different strings. NFD text is common in file names created on
macOS. Typical things to check: string comparison and search, sorting,
de-duplication, length counting, and whether a tool normalises input.

## Input

- `input.txt`: UTF-8, no BOM, LF line endings, final newline, six lines in
  three pairs. In each pair the first line is NFC and the second NFD:

| Line | Looks like | Code points | Form |
|------|------------|-------------|------|
| 1 | が | U+304C | NFC |
| 2 | が | U+304B U+3099 | NFD |
| 3 | パ | U+30D1 | NFC |
| 4 | パ | U+30CF U+309A | NFD |
| 5 | ガイド | U+30AC U+30A4 U+30C9 | NFC |
| 6 | ガイド | U+30AB U+3099 U+30A4 U+30C8 U+3099 | NFD |

## Features

`nfc`, `nfd`, `combining-dakuten`, `combining-handakuten`,
`canonical-equivalence`

## Ground truth

`expected.json` → `ground_truth` records:

- `encoding`, `bom`, `line_terminator`, `trailing_newline`.
- `lines`: each line as text plus code points, with `is_nfc` and `is_nfd`
  (whether the line is already in that normalization form).
- `canonically_equivalent_pairs`: 1-based line numbers of each NFC/NFD pair.
- `unicode_version`: the Unicode version of the Python `unicodedata` used to
  compute `is_nfc` / `is_nfd`. It records where the values came from; for these
  characters the results are the same in every Unicode version since 4.1.

## How it was generated

`python tools/gen/txt_001.py`. The script builds each pair with
`unicodedata.normalize("NFC" / "NFD", ...)`, writes one line per string with
LF endings, reads the file back and checks the lines, that line 1 is U+304C
and line 2 is U+304B U+3099, and that each NFD line normalises to its NFC
partner, before it writes `expected.json`.

## Notes

- U+3099 and U+309A are the *combining* sound marks. The spacing marks
  U+309B / U+309C are a different thing and appear in txt-003.
