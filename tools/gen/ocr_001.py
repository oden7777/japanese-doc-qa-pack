"""Generate cases/ocr-001: an image-only PDF of a fictional Japanese receipt.

The receipt is rendered with the bundled font into a 300 dpi greyscale image
and placed on an 80 mm x 160 mm page. The PDF has no text layer at all: no
text operators and no font resources.

Usage: python tools/gen/ocr_001.py
"""

from __future__ import annotations

import re
import unicodedata

import pypdf
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pypdf.generic import ArrayObject, DictionaryObject, IndirectObject
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from common import FONT_PATH, case_dir, text_value, write_expected

CASE_ID = "ocr-001"
FONT_NAME = "BIZUDGothic-Regular"
PAGE_SIZE = (80 * mm, 160 * mm)
DPI = 300
IMAGE_SIZE = (945, 1890)  # 80 mm x 160 mm at 300 dpi, rounded to whole pixels
FONT_PX = 40
CELLS = 36  # line width in half-width cells; BIZ UDGothic is fixed-pitch
TOP_PX = 140
LINE_STEP_PX = 62
FORBIDDEN_KEYS = {"/JavaScript", "/JS", "/OpenAction", "/AA", "/EmbeddedFiles", "/URI", "/Launch"}


def cells(s: str) -> int:
    return sum(2 if unicodedata.east_asian_width(ch) in ("F", "W") else 1 for ch in s)


def row(left: str, right: str) -> str:
    """Left text and right-aligned amount, padded with ASCII spaces."""
    return left + " " * (CELLS - cells(left) - cells(right)) + right


RULE = "-" * CELLS
# (line text, centred?). Every value is fictional; numbers are zero-filled.
LINES = [
    ("サンプル商店 テスト店", True),
    ("〒000-0000 架空県見本市1-2-3", True),
    ("TEL 000-0000-0000", True),
    ("2026年1月1日 10:00", False),
    (RULE, False),
    (row("りんご", "￥120"), False),
    (row("牛乳", "￥198"), False),
    (row("食パン", "￥158"), False),
    (RULE, False),
    (row("小計", "￥476"), False),
    (row("消費税等(8%)", "￥38"), False),
    (row("合計", "￥514"), False),
    (row("お預り", "￥1,000"), False),
    (row("お釣り", "￥486"), False),
    (RULE, False),
    ("ありがとうございました", True),
    ("※テスト用の架空のレシートです", True),
]


def render_image() -> Image.Image:
    font = ImageFont.truetype(str(FONT_PATH), FONT_PX)
    image = Image.new("L", IMAGE_SIZE, 255)
    draw = ImageDraw.Draw(image)
    line_px = CELLS * FONT_PX // 2
    left = (IMAGE_SIZE[0] - line_px) // 2
    for i, (line, centred) in enumerate(LINES):
        assert cells(line) <= CELLS, line
        x = left + (line_px - int(font.getlength(line))) // 2 if centred else left
        draw.text((x, TOP_PX + i * LINE_STEP_PX), line, font=font, fill=0, anchor="ls")
    return image.filter(ImageFilter.GaussianBlur(0.5))


def build(path) -> None:
    # A TTFont as the initial font keeps ReportLab from writing any text
    # operator or font resource on a page that has no text.
    pdfmetrics.registerFont(TTFont(FONT_NAME, str(FONT_PATH)))
    c = canvas.Canvas(str(path), pagesize=PAGE_SIZE, invariant=1, initialFontName=FONT_NAME)
    c.drawImage(ImageReader(render_image()), 0, 0, width=PAGE_SIZE[0], height=PAGE_SIZE[1])
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
    reader = pypdf.PdfReader(path)
    assert len(reader.pages) == 1
    page = reader.pages[0]
    assert page.rotation == 0
    mediabox = [float(v) for v in page.mediabox]
    assert abs(mediabox[2] - PAGE_SIZE[0]) < 0.01 and abs(mediabox[3] - PAGE_SIZE[1]) < 0.01
    assert page.extract_text() == "", "page must have no text layer"
    content = page.get_contents().get_data().decode("latin-1")
    assert not re.search(r"\b(BT|ET|Tf|Tj|TJ)\b", content), "text operators present"
    # ReportLab always writes a /Font entry; it must be an empty dictionary.
    assert not page["/Resources"].get("/Font", DictionaryObject()).get_object(), "font resource present"
    images = list(page.images)
    assert len(images) == 1 and images[0].image.size == IMAGE_SIZE
    assert images[0].image.mode == "L", "image must be greyscale (DeviceGray)"
    bad = pdf_keys(reader.trailer) & FORBIDDEN_KEYS
    assert not bad, f"forbidden PDF keys: {bad}"
    return {
        "index": 1,
        "mediabox": mediabox,
        "width_pt": mediabox[2] - mediabox[0],
        "height_pt": mediabox[3] - mediabox[1],
        "rotate": 0,
        "size_name": "80x160mm",
        "has_text_layer": False,
        "has_image": True,
        "image": {"width_px": IMAGE_SIZE[0], "height_px": IMAGE_SIZE[1], "dpi": DPI, "colorspace": "DeviceGray"},
    }


def main() -> None:
    directory = case_dir(CASE_ID)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "input.pdf"
    build(path)
    page = self_check(path)
    write_expected(
        CASE_ID,
        category="ocr",
        description=(
            "Image-only PDF of a fictional Japanese receipt (80 x 160 mm page, 300 dpi "
            "greyscale image). There is no text layer at all: no text operators and no "
            "font resources. The ground truth is the text that was drawn into the image."
        ),
        input_file="input.pdf",
        mime_type="application/pdf",
        encoding=None,
        features=["image-only-pdf", "no-text-layer", "receipt", "fixed-pitch-layout", "fullwidth-yen-sign"],
        ground_truth={
            "page_count": 1,
            "pages": [page],
            "rendered_text_lines": [text_value(line) for line, _ in LINES],
            "fonts": [],
        },
    )


if __name__ == "__main__":
    main()
