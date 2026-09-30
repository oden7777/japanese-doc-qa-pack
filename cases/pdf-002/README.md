# pdf-002: rotated page and mixed page sizes

## Purpose

Tests how a PDF tool handles page geometry: a page with a `/Rotate` value and
pages of different sizes in one file. Typical things to check: reported page
size before and after applying rotation, landscape/portrait detection, text
position on a rotated page, and page-by-page rendering or splitting.

## Input

- `input.pdf`: three pages.

| Page | Size | MediaBox (pt, as written) | `/Rotate` | Displayed as | Label |
|------|------|---------------------------|-----------|--------------|-------|
| 1 | A4 | 0 0 595.2756 841.8898 | 0 | portrait | 1ページ目 A4 回転0度 |
| 2 | A4 | 0 0 595.2756 841.8898 | 90 | landscape | 2ページ目 A4 回転90度 |
| 3 | A5 | 0 0 419.5276 595.2756 | 0 | portrait | 3ページ目 A5 回転0度 |

- On page 2 the label is drawn running up the portrait page, so it reads
  left to right once a viewer applies the 90-degree clockwise rotation.
- Font: BIZ UDGothic Regular, embedded as a subset with a ToUnicode map.

## Features

`page-rotation`, `mixed-page-sizes`, `a4`, `a5`, `text-layer`,
`embedded-font`

## Ground truth

`expected.json` → `ground_truth` records:

- `page_count`.
- Per page: `mediabox` exactly as written in the file (before rotation is
  applied), `width_pt` / `height_pt` derived from it, the `/Rotate` value
  `rotate`, the paper size name `size_name`, `has_text_layer`, `has_image`,
  and the label `text` (text plus Unicode code points).
- `fonts`: the embedded subset font.

The ground truth does not state the displayed size of page 2 or where the
label should appear in extracted coordinates; those follow from the
MediaBox and `/Rotate` and are what the tool under test should work out.

## How it was generated

`python tools/gen/pdf_002.py` (ReportLab 5.0.1, `invariant=1`). ReportLab
swaps width and height in the MediaBox of a page whose rotation is 90, so the
script passes the landscape size for page 2 to end up with a portrait
MediaBox. The script reads the file back with pypdf and checks page count,
rotation, MediaBox, label extraction, the font in use and the absence of
images and active content before it writes `expected.json`.

## Notes

- Font: BIZ UDGothic Regular (Morisawa), SIL Open Font License 1.1. See
  `fonts/OFL.txt` in the repository.
- Only the page 2 content is rotated in page space; there is no rotation in
  the page tree or `/Rotate` inherited from a parent `/Pages` node.
