"""Generate cases/pdf-001: true PDF vertical writing (WMode 1) with ruby.

The text uses ReportLab's standard Japanese CID font HeiseiMin-W3 with the
vertical CMap UniJIS-UCS2-V. The font is referenced by name only: nothing is
embedded and no ToUnicode map is written.

Usage: python tools/gen/pdf_001.py
"""

from __future__ import annotations

import pypdf
from pypdf.generic import ArrayObject, DictionaryObject, IndirectObject
from reportlab.lib.pagesizes import A5
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas

from common import case_dir, text_value, write_expected

CASE_ID = "pdf-001"
FONT_NAME = "HeiseiMin-W3"
CMAP = "UniJIS-UCS2-V"
BODY_SIZE = 20
RUBY_SIZE = 10

# Columns are drawn right to left; each column reads top to bottom.
COLUMNS = [
    "雨上がりの庭に紫陽花が咲き、",
    "東雲の空が明るくなった。",
    "喫茶店でコーヒーを飲んだ。",
]
# (column index, start index in that column, base text, ruby text)
RUBY = [
    (0, 7, "紫陽花", "あじさい"),
    (1, 0, "東雲", "しののめ"),
]
FORBIDDEN_KEYS = {"/JavaScript", "/JS", "/OpenAction", "/AA", "/EmbeddedFiles", "/URI", "/Launch"}


def build(path) -> None:
    pdfmetrics.registerFont(UnicodeCIDFont(FONT_NAME, isVertical=True))
    width, height = A5
    # initialFontName keeps ReportLab from adding an unused Helvetica font resource.
    c = canvas.Canvas(str(path), pagesize=A5, invariant=1,
                      initialFontName=FONT_NAME, initialFontSize=BODY_SIZE)
    top = height - 60
    x0 = width - 80
    pitch = BODY_SIZE * 2.2
    c.setFont(FONT_NAME, BODY_SIZE)
    for i, column in enumerate(COLUMNS):
        c.drawString(x0 - i * pitch, top, column)
    # Ruby sits to the right of its base characters, centred along them.
    c.setFont(FONT_NAME, RUBY_SIZE)
    for col, start, base, ruby in RUBY:
        x = x0 - col * pitch + BODY_SIZE / 2 + RUBY_SIZE / 2
        y = top - start * BODY_SIZE - (len(base) * BODY_SIZE - len(ruby) * RUBY_SIZE) / 2
        c.drawString(x, y, ruby)
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


def self_check(path) -> dict[str, object]:
    raw = path.read_bytes()
    assert f"/{CMAP}".encode() in raw, "vertical CMap missing"
    assert b"/FontFile" not in raw and b"/ToUnicode" not in raw, "font must not be embedded"
    reader = pypdf.PdfReader(path)
    assert len(reader.pages) == 1
    page = reader.pages[0]
    assert page.rotation == 0
    fonts = {str(f.get_object()["/BaseFont"]) for f in page["/Resources"]["/Font"].values()}
    assert fonts == {f"/{FONT_NAME}"}, f"unexpected fonts: {fonts}"
    mediabox = [float(v) for v in page.mediabox]
    assert abs(mediabox[2] - A5[0]) < 0.01 and abs(mediabox[3] - A5[1]) < 0.01
    text = page.extract_text()
    for s in [*COLUMNS, *(r[3] for r in RUBY)]:
        assert s in text, f"not extractable: {s}"
    for col, start, base, _ in RUBY:
        assert COLUMNS[col][start:start + len(base)] == base
    bad = pdf_keys(reader.trailer) & FORBIDDEN_KEYS
    assert not bad, f"forbidden PDF keys: {bad}"
    return {
        "index": 1,
        "mediabox": mediabox,
        "width_pt": mediabox[2] - mediabox[0],
        "height_pt": mediabox[3] - mediabox[1],
        "rotate": 0,
        "size_name": "A5",
        "has_text_layer": True,
        "has_image": False,
    }


def main() -> None:
    directory = case_dir(CASE_ID)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "input.pdf"
    build(path)
    page = self_check(path)
    write_expected(
        CASE_ID,
        category="pdf",
        description=(
            "One A5 page of Japanese vertical text written with true PDF vertical writing "
            "(WMode 1, UniJIS-UCS2-V CMap), with ruby drawn as smaller vertical text beside "
            "its base characters. The standard CID font HeiseiMin-W3 is referenced by name "
            "only: it is not embedded and there is no ToUnicode map."
        ),
        input_file="input.pdf",
        mime_type="application/pdf",
        encoding=None,
        features=["vertical-writing", "pdf-wmode-1", "ruby", "text-layer", "cid-font", "non-embedded-font"],
        ground_truth={
            "page_count": 1,
            "pages": [page],
            "layout": {"visual_direction": "vertical-rl", "pdf_wmode": 1, "cmap": CMAP},
            "fonts": [{"name": FONT_NAME, "embedded": False, "to_unicode": False}],
            "body_text": text_value("".join(COLUMNS)),
            "columns": [text_value(s) for s in COLUMNS],
            "ruby": [{"base": text_value(base), "ruby": text_value(ruby)} for _, _, base, ruby in RUBY],
            "ruby_in_text_layer": True,
        },
    )


if __name__ == "__main__":
    main()
