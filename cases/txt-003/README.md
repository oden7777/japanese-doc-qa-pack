# txt-003: strings whose Unicode normalization forms differ

## Purpose

Tests how text processing applies Unicode normalization to typical Japanese
input: half-width katakana, full-width alphanumerics and compatibility
characters, which NFKC/NFKD rewrite, plus one CJK compatibility ideograph
that even NFC rewrites. Typical things to check: which normalization form a
tool applies (if any), search and matching across width variants, and
unintended changes such as `神` (U+FA19) turning into `神` (U+795E).

## Input

- `input.txt`: UTF-8, no BOM, LF line endings, final newline, one string per
  line:

| Line | Source | NFC | NFKC |
|------|--------|-----|------|
| 1 | ｶﾞ U+FF76 U+FF9E | unchanged | ガ U+30AC |
| 2 | ﾊﾟ U+FF8A U+FF9F | unchanged | パ U+30D1 |
| 3 | ＡＢＣ１２３ | unchanged | ABC123 |
| 4 | ① U+2460 | unchanged | 1 |
| 5 | ㈱ U+3231 | unchanged | (株) |
| 6 | ㍻ U+337B | unchanged | 平成 |
| 7 | ゛ U+309B | unchanged | U+0020 U+3099 |
| 8 | 神 U+FA19 | 神 U+795E | 神 U+795E |

## Features

`nfkc`, `nfkd`, `halfwidth-katakana`, `fullwidth-alphanumerics`,
`compatibility-characters`, `cjk-compatibility-ideograph`

## Ground truth

`expected.json` → `ground_truth` records:

- `encoding`, `bom`, `line_terminator`, `trailing_newline`, and `lines`
  (each line as text plus code points).
- `normalizations`: for each line, the `source` string and its `nfc`, `nfd`,
  `nfkc` and `nfkd` forms, each as text plus code points.
- `unicode_version`: the Unicode version of the Python `unicodedata` that
  computed the forms. This records where the values came from and how to
  reproduce them.

Every character here was assigned in Unicode 1.1. Under the Unicode
normalization stability policy (in force since Unicode 4.1), the normalized
form of a string made only of characters assigned in both versions does not
change between versions. These results can therefore be used with any
current Unicode implementation.

## How it was generated

`python tools/gen/txt_003.py`. The script writes one string per line,
computes the four forms with `unicodedata.normalize`, reads the file back and
checks the lines, that NFKC changes every line, and two spot values (U+FA19
→ U+795E under NFC, `ｶﾞ` → `ガ` under NFKC), before it writes `expected.json`.

## Notes

- Line 7 is the *spacing* voiced sound mark U+309B. Its compatibility
  decomposition is a SPACE followed by the combining mark U+3099, so NFKC
  output starts with an ordinary space.
- Line 8 shows that NFC is not always "harmless" for Japanese text: CJK
  compatibility ideographs have canonical decompositions to unified
  ideographs.
