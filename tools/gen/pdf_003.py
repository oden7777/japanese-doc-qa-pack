"""Generate cases/pdf-003: a scan-like image with an invisible text layer.

One A4 page holds a 150 dpi greyscale image of Japanese text (rendered with
the bundled font, plus fixed-seed speckle noise and a slight blur). The same
lines are laid over it as invisible text (render mode 3) at matching
positions, like the output of an OCR tool that makes a scan searchable.

Usage: python tools/gen/pdf_003.py
"""

from __future__ import annotations

import random
import re

import pypdf
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont
from pypdf.generic import ArrayObject, DictionaryObject, IndirectObject
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from common import FONT_PATH, case_dir, text_value, write_expected

CASE_ID = "pdf-003"
FONT_NAME = "BIZUDGothic-Regular"
DPI = 150
IMAGE_SIZE = (1240, 1754)  # A4 at 150 dpi
FONT_PX = 36
LEFT_PX = 150
FIRST_BASELINE_PX = 220
LINE_STEP_PX = 72
NOISE_SEED = 3
LINES = [
    "スキャン文書のサンプル",
    "この文書はテスト用の架空のデータです。",
    "文書番号：TEST-0003",
    "発行日：2026年1月1日",
    "検索可能なテキストレイヤーを重ねています。",
]
FORBIDDEN_KEYS = {"/JavaScript", "/JS", "/OpenAction", "/AA", "/EmbeddedFiles", "/URI", "/Launch"}


def baseline_px(i: int) -> int:
    return FIRST_BASELINE_PX + i * LINE_STEP_PX


def px_to_pt(px: float) -> float:
    return px * 72 / DPI


def render_image() -> Image.Image:
    font = ImageFont.truetype(str(FONT_PATH), FONT_PX)
    text = Image.new("L", IMAGE_SIZE, 255)
    draw = ImageDraw.Draw(text)
    for i, line in enumerate(LINES):
        draw.text((LEFT_PX, baseline_px(i)), line, font=font, fill=0, anchor="ls")
    text = text.filter(ImageFilter.GaussianBlur(0.6))
    rng = random.Random(NOISE_SEED)
    noise = Image.frombytes("L", IMAGE_SIZE, rng.randbytes(IMAGE_SIZE[0] * IMAGE_SIZE[1]))
    speckles = noise.point(lambda v: 60 if v == 0 else 255)
    paper = Image.new("L", IMAGE_SIZE, 248)
    return ImageChops.darker(ImageChops.darker(paper, text), speckles)


def build(path) -> None:
    pdfmetrics.registerFont(TTFont(FONT_NAME, str(FONT_PATH)))
    width, height = A4
    c = canvas.Canvas(str(path), pagesize=A4, invariant=1,
                      initialFontName=FONT_NAME, initialFontSize=px_to_pt(FONT_PX))
    c.drawImage(ImageReader(render_image()), 0, 0, width=width, height=height)
    t = c.beginText()
    t.setTextRenderMode(3)  # invisible: neither filled nor stroked
    t.setFont(FONT_NAME, px_to_pt(FONT_PX))
    for i, line in enumerate(LINES):
        t.setTextOrigin(px_to_pt(LEFT_PX), height - px_to_pt(baseline_px(i)))
        t.textOut(line)
    c.drawText(t)
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
    assert abs(mediabox[2] - A4[0]) < 0.01 and abs(mediabox[3] - A4[1]) < 0.01
    images = list(page.images)
    assert len(images) == 1 and images[0].image.size == IMAGE_SIZE
    assert images[0].image.mode == "L", "image must be greyscale (DeviceGray)"
    content = page.get_contents().get_data().decode("latin-1")
    assert re.findall(r"\b(\d) Tr\b", content) == ["3"], "text must be drawn in render mode 3 only"
    text = page.extract_text()
    for line in LINES:
        assert line in text, f"not extractable: {line}"
    fonts = {str(f.get_object()["/BaseFont"]) for f in page["/Resources"]["/Font"].values()}
    assert all("/FontFile2" in f.get_object()["/FontDescriptor"] for f in page["/Resources"]["/Font"].values()), "font not embedded"
    assert len(fonts) == 1 and fonts.pop().endswith(f"+{FONT_NAME}"), fonts
    bad = pdf_keys(reader.trailer) & FORBIDDEN_KEYS
    assert not bad, f"forbidden PDF keys: {bad}"
    return {
        "index": 1,
        "mediabox": mediabox,
        "width_pt": mediabox[2] - mediabox[0],
        "height_pt": mediabox[3] - mediabox[1],
        "rotate": 0,
        "size_name": "A4",
        "has_text_layer": True,
        "has_image": True,
        "image": {"width_px": IMAGE_SIZE[0], "height_px": IMAGE_SIZE[1], "dpi": DPI, "colorspace": "DeviceGray"},
        "text_render_mode": 3,
        "text_layer_lines": [text_value(line) for line in LINES],
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
            "One A4 page combining a scan-like 150 dpi greyscale image of Japanese text with "
            "an invisible (render mode 3) searchable text layer holding the same lines at "
            "matching positions, as produced by OCR tools that make scans searchable."
        ),
        input_file="input.pdf",
        mime_type="application/pdf",
        encoding=None,
        features=["scanned-image", "invisible-text-layer", "text-render-mode-3", "searchable-pdf", "embedded-font"],
        ground_truth={
            "page_count": 1,
            "pages": [page],
            "image_text_equals_text_layer": True,
            "fonts": [{"name": FONT_NAME, "embedded": True, "subset": True}],
        },
    )


if __name__ == "__main__":
    main()
