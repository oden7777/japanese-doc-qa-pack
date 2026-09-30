# txt-002: invisible characters inside Japanese text

## Purpose

Tests how text processing handles characters that are invisible or look like
an ordinary space. They often slip in when text is copied from web pages,
word processors or PDFs. Typical things to check: search and comparison,
trimming and whitespace splitting, tokenisation, length counting, and
whether a tool strips or reports these characters.

## Input

- `input.txt`: UTF-8, no BOM, LF line endings, final newline, five lines.
  Each line hides one character at code point index 2:

| Line | Text (character shown as ⟨⟩) | Hidden character |
|------|------------------------------|------------------|
| 1 | 東京⟨⟩都 | U+200B ZERO WIDTH SPACE |
| 2 | 価格⟨⟩100円 | U+00A0 NO-BREAK SPACE |
| 3 | 全角⟨⟩スペース | U+3000 IDEOGRAPHIC SPACE |
| 4 | 文中⟨⟩のBOM | U+FEFF ZERO WIDTH NO-BREAK SPACE |
| 5 | 単語⟨⟩結合子 | U+2060 WORD JOINER |

- U+FEFF appears in the middle of line 4, not at the start of the file, so
  the file has no BOM.

## Features

`zero-width-space`, `no-break-space`, `ideographic-space`,
`zero-width-no-break-space`, `word-joiner`, `invisible-characters`

## Ground truth

`expected.json` → `ground_truth` records:

- `encoding`, `bom: false`, `line_terminator`, `trailing_newline`.
- `lines`: each line as text plus code points.
- `invisible_chars`: every hidden character with its `line` (1-based),
  `index` (0-based position counted in Unicode code points, not UTF-16 units
  or bytes), `codepoint` and Unicode character `name`.
- `unicode_version`: the Unicode version of the Python `unicodedata` that
  supplied the character names. It records where the values came from; these
  names have not changed since the characters were assigned.

## How it was generated

`python tools/gen/txt_002.py`. The script writes the lines with LF endings,
reads the file back and checks the lines, that each recorded position holds
the recorded code point, that the file does not start with a BOM, and that
it contains no bidirectional control characters, before it writes
`expected.json`.

## Notes

- No bidirectional controls (U+202A–U+202E, U+2066–U+2069, U+200E, U+200F,
  U+061C) are included, so the file cannot be used to disguise text.
