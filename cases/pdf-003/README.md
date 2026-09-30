# pdf-003: scan image with an invisible searchable text layer

## Purpose

Tests how a PDF tool handles a "searchable scan": a page whose visible content
is a raster image, with the same text laid over it as invisible text. This is
what OCR tools produce when they make scanned documents searchable. Typical
things to check: whether text extraction returns the invisible text, whether
"has text?" detection treats the page as text or as an image, whether
rendering hides the invisible text, and whether a tool re-runs OCR on a page
that already has a text layer.

## Input

- `input.pdf`: one A4 portrait page, no rotation.
- One greyscale image (1240 × 1754 px, 150 dpi, DeviceGray) covering the whole
  page. It shows five lines of Japanese text on off-white paper with light
  speckle noise and a slight blur:
  1. スキャン文書のサンプル
  2. この文書はテスト用の架空のデータです。
  3. 文書番号：TEST-0003
  4. 発行日：2026年1月1日
  5. 検索可能なテキストレイヤーを重ねています。
- The same five lines as text in render mode 3 (invisible), in the same font
  and size, at the same positions as the lines in the image.
- Font: BIZ UDGothic Regular, embedded as a subset with a ToUnicode map.

## Features

`scanned-image`, `invisible-text-layer`, `text-render-mode-3`,
`searchable-pdf`, `embedded-font`

## Ground truth

`expected.json` → `ground_truth` records:

- `page_count`, and for the page: MediaBox as written, rotation, size name,
  `has_text_layer: true`, `has_image: true`.
- `image`: pixel size, resolution and colour space of the page image.
- `text_render_mode`: 3 (the text layer is invisible).
- `text_layer_lines`: the five lines of the text layer (text plus Unicode code
  points). `image_text_equals_text_layer: true` means the image shows exactly
  these lines.
- `fonts`: the embedded subset font.

The ground truth is the text that was drawn, not the output of any OCR
engine.

## How it was generated

`python tools/gen/pdf_003.py` (Pillow 12.3.0, ReportLab 5.0.1 with
`invariant=1`). Pillow draws the lines with the bundled font at 36 px; the
speckle noise comes from a fixed random seed. ReportLab places the image over
the whole page and writes the invisible text at the same baselines
(pixel × 72 / 150 pt). The script reads the file back with pypdf and checks the
image size, that render mode 3 is the only render mode used, that every line
can be extracted, the font in use and the absence of active content before
it writes `expected.json`.

## Notes

- Font: BIZ UDGothic Regular (Morisawa), SIL Open Font License 1.1. See
  `fonts/OFL.txt` in the repository.
- The image is synthetic, not a real scan. It contains no personal data.
- The image is not skewed, so the text layer lines up with the image exactly.
