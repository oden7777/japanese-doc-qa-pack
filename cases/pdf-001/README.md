# pdf-001: Japanese vertical writing (WMode 1) with ruby

## Purpose

Tests how a PDF tool handles Japanese text set in **true PDF vertical writing**:
text shown with a vertical CMap (WMode 1), where each glyph advances downward
and columns run right to left. The page also carries ruby (furigana) beside
two words, and uses a standard Japanese CID font that is **not embedded**.
Typical things to check: text extraction from vertical text, reading order of
columns, how ruby is separated from the main text, and behaviour when the font
program is missing from the file.

## Input

- `input.pdf`: one A5 portrait page, no rotation.
- Three vertical columns of body text, read right to left:
  1. 雨上がりの庭に紫陽花が咲き、
  2. 東雲の空が明るくなった。
  3. 喫茶店でコーヒーを飲んだ。
- Ruby, drawn at half size to the right of its base characters:
  紫陽花 → あじさい, 東雲 → しののめ.
- Font: `HeiseiMin-W3` with the `UniJIS-UCS2-V` CMap (`Type0` font, WMode 1).

## Features

`vertical-writing`, `pdf-wmode-1`, `ruby`, `text-layer`, `cid-font`,
`non-embedded-font`

## Ground truth

`expected.json` → `ground_truth` records:

- `page_count`, and per page the MediaBox exactly as written in the file,
  rotation, size name and whether a text layer / image is present.
- `layout`: `visual_direction` `vertical-rl`, `pdf_wmode` 1, `cmap`
  `UniJIS-UCS2-V`.
- `fonts`: the font is referenced by name, `embedded: false`,
  `to_unicode: false`.
- `body_text`: the body without ruby, as one string; `columns`: the body as
  drawn, one string per column (right to left).
- `ruby`: each base text with its ruby text. `ruby_in_text_layer: true` means
  the ruby characters are also real text in the text layer.

All strings are given as text plus Unicode code points. The ground truth does
**not** say in which order a tool should extract the text, or whether ruby
should be dropped, kept or attached to its base: that is up to the tool under
test.

## How it was generated

`python tools/gen/pdf_001.py` (ReportLab 5.0.1, `invariant=1`). Each column is
one `drawString` call with the vertical CID font; each ruby string is one
`drawString` call at 10 pt next to its 20 pt base. The script reads the file
back with pypdf and checks page size, rotation, that every string can be
extracted, that the CMap is present and that no font file or ToUnicode map was
written, before it writes `expected.json`.

## Notes

- This is true PDF vertical writing (WMode 1), not horizontal glyphs placed
  one by one.
- The font is **not embedded** and there is **no ToUnicode** map. How the glyphs
  look depends on the viewer's substitute Japanese font, and whether text can
  be extracted depends on the extractor supporting the predefined Adobe-Japan1
  CMap `UniJIS-UCS2-V`. Both are intended test conditions.
- No font program is bundled or embedded for this case, so no third-party font
  license applies to it.
