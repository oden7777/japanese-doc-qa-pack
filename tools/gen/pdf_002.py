"""Generate cases/pdf-002: a rotated page and mixed page sizes.

Page 1 is A4 portrait, page 2 is A4 with /Rotate 90 (its MediaBox stays
portrait, so it is displayed as landscape), page 3 is A5 portrait. Each page
carries one short Japanese label in the bundled BIZ UDGothic font.

Usage: python tools/gen/pdf_002.py
"""

from __future__ import annotations

import pypdf
from pypdf.generic import ArrayObject, DictionaryObject, IndirectObject
from reportlab.lib.pagesizes import A4, A5, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from common import FONT_PATH, case_dir, text_value, write_expected

CASE_ID = "pdf-002"
FONT_NAME = "BIZUDGothic-Regular"
FONT_SIZE = 18
MARGIN = 72
# (size name, page size before rotation, /Rotate, label)
PAGES = [
    ("A4", A4, 0, "1ページ目 A4 回転0度"),
    ("A4", A4, 90, "2ページ目 A4 回転90度"),
    ("A5", A5, 0, "3ページ目 A5 回転0度"),
]
FORBIDDEN_KEYS = {"/JavaScript", "/JS", "/OpenAction", "/AA", "/EmbeddedFiles", "/URI", "/Launch"}


def build(path) -> None:
    pdfmetrics.registerFont(TTFont(FONT_NAME, str(FONT_PATH)))
    c = canvas.Canvas(str(path), pagesize=A4, invariant=1,
                      initialFontName=FONT_NAME, initialFontSize=FONT_SIZE)
    for _, size, rotate, label in PAGES:
        width, height = size
        if rotate == 90:
            # ReportLab swaps width and height in the MediaBox of a page with
            # /Rotate 90, so pass the landscape size to get a portrait MediaBox.
            c.setPageSize(landscape(size))
        else:
            c.setPageSize(size)
        c.setPageRotation(rotate)
        c.setFont(FONT_NAME, FONT_SIZE)
        if rotate == 90:
            # Viewers turn the page 90 degrees clockwise, so text running up
            # the portrait page reads left to right on screen.
            c.saveState()
            c.translate(MARGIN + FONT_SIZE, MARGIN)
            c.rotate(90)
            c.drawString(0, 0, label)
            c.restoreState()
        else:
            c.drawString(MARGIN, height - MARGIN, label)
        c.showPage()
    c.save()


def pdf_keys(obj, seen: set[int] | None = None) -> set[str]:
    """Collect every dictionary key reachable from obj."""
    seen = set() if seen is None else seen
    if isinstance(obj, IndirectObject):
        if obj.idnum in seen:
            return set()
        seen.add(obj.idnum)
        obj = obj.get_object()
    keys: set[str] = set()
    if isinstance(obj, DictionaryObject):
        for k, v in obj.items():
            keys.add(str(k))
            keys |= pdf_keys(v, seen)
    elif isinstance(obj, ArrayObject):
        for v in obj:
            keys |= pdf_keys(v, seen)
    return keys


def self_check(path) -> list[dict[str, object]]:
    reader = pypdf.PdfReader(path)
    assert len(reader.pages) == len(PAGES)
    pages = []
    for i, (page, (name, size, rotate, label)) in enumerate(zip(reader.pages, PAGES), start=1):
        assert page.rotation == rotate, (i, page.rotation)
        mediabox = [float(v) for v in page.mediabox]
        assert abs(mediabox[2] - size[0]) < 0.01 and abs(mediabox[3] - size[1]) < 0.01, (i, mediabox)
        assert label in page.extract_text(), (i, label)
        fonts = {str(f.get_object()["/BaseFont"]) for f in page["/Resources"]["/Font"].values()}
        assert all("/FontFile2" in f.get_object()["/FontDescriptor"] for f in page["/Resources"]["/Font"].values()), "font not embedded"
        assert len(fonts) == 1 and fonts.pop().endswith(f"+{FONT_NAME}"), (i, fonts)
        assert "/XObject" not in page["/Resources"], (i, "unexpected image")
        pages.append({
            "index": i,
            "mediabox": mediabox,
            "width_pt": mediabox[2] - mediabox[0],
            "height_pt": mediabox[3] - mediabox[1],
            "rotate": rotate,
            "size_name": name,
            "has_text_layer": True,
            "has_image": False,
            "text": text_value(label),
        })
    bad = pdf_keys(reader.trailer) & FORBIDDEN_KEYS
    assert not bad, f"forbidden PDF keys: {bad}"
    return pages


def main() -> None:
    directory = case_dir(CASE_ID)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "input.pdf"
    build(path)
    pages = self_check(path)
    write_expected(
        CASE_ID,
        category="pdf",
        description=(
            "Three-page PDF mixing page sizes and rotation: A4 portrait, A4 with /Rotate 90 "
            "(portrait MediaBox, displayed as landscape) and A5 portrait. Each page has one "
            "short Japanese text label in an embedded font."
        ),
        input_file="input.pdf",
        mime_type="application/pdf",
        encoding=None,
        features=["page-rotation", "mixed-page-sizes", "a4", "a5", "text-layer", "embedded-font"],
        ground_truth={
            "page_count": len(pages),
            "pages": pages,
            "fonts": [{"name": FONT_NAME, "embedded": True, "subset": True}],
        },
    )


if __name__ == "__main__":
    main()
