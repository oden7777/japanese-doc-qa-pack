# ocr-001: image-only PDF of a Japanese receipt

## Purpose

Tests OCR on a Japanese receipt that exists only as an image. The PDF has no
text layer at all, so any text a tool returns must come from recognising the
image. Typical things to check: recognition of kana, kanji, full-width yen
signs and digits, alignment of item names and amounts on the same line, and
correct detection that the PDF has no extractable text.

## Input

- `input.pdf`: one 80 mm × 160 mm page (226.7717 × 453.5433 pt), no rotation.
- One greyscale image (945 × 1890 px, 300 dpi, DeviceGray) covering the page,
  showing a fictional receipt: shop name, address and phone number, date,
  three items, subtotal, tax, total, cash received and change.
- No text: the page content only draws the image. There are no text operators
  and no font objects (the page's `/Font` resource dictionary is empty).
- The image was drawn in BIZ UDGothic, a fixed-pitch font, and amounts are
  right-aligned with ASCII spaces, so each receipt line is one string.

## Features

`image-only-pdf`, `no-text-layer`, `receipt`, `fixed-pitch-layout`,
`fullwidth-yen-sign`

## Ground truth

`expected.json` → `ground_truth` records:

- `page_count`, and for the page: MediaBox as written, rotation, size name,
  `has_text_layer: false`, `has_image: true`, and the image's pixel size,
  resolution and colour space.
- `rendered_text_lines`: every line exactly as drawn into the image, in order
  from top to bottom, including the padding spaces between item names and
  amounts (text plus Unicode code points). The yen sign is always U+FFE5
  FULLWIDTH YEN SIGN.
- `fonts`: empty, because the PDF contains no fonts.

These lines are the source text that was drawn, **not** the output of any OCR
engine. How a tool should normalise spaces, the yen sign or digit widths when
comparing its output is left to the tool under test.

## How it was generated

`python tools/gen/ocr_001.py` (Pillow 12.3.0, ReportLab 5.0.1 with
`invariant=1`). Pillow draws the lines with the bundled font at 40 px on a
white background and applies a slight blur. ReportLab places the image over
the whole page. The script reads the file back with pypdf and checks that no
text can be extracted, that the content has no text operators and no fonts,
the image size and colour space, and the absence of active content before it
writes `expected.json`.

## Notes

- Everything on the receipt is fictional. The shop, address (架空県見本市) and
  phone number (000-0000-0000) do not exist; the postcode is 〒000-0000. The
  last line says it is a fictional receipt for testing.
- The image is rendered from the font into a clean image. It is not a photo
  or a real scan.
- Font used to draw the image: BIZ UDGothic Regular (Morisawa), SIL Open Font
  License 1.1. See `fonts/OFL.txt` in the repository. The font is not present
  in the PDF.
