#!/usr/bin/env python3

"""Create the two-page Morrow Tide Journal source PDF."""

from __future__ import annotations

import argparse
from io import BytesIO
import json
from pathlib import Path

from PIL import Image, ImageOps
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


PAGE_WIDTH = 210 * mm
PAGE_HEIGHT = 270 * mm
MARGIN = 14 * mm

INK = HexColor("#15212A")
OCEAN = HexColor("#126B73")
RUST = HexColor("#C26046")
SAND = HexColor("#F1ECE2")
PAPER = HexColor("#FCFBF8")
MUTED = HexColor("#68747C")
PALE_OCEAN = HexColor("#DDE9E7")

FONT_HEADING = "Montserrat-SemiBold"
FONT_BODY = "Lato-Regular"
FONT_BODY_BOLD = "Lato-Bold"


def load_content(source_dir: Path) -> dict:
    with (source_dir / "content.json").open(encoding="utf-8") as stream:
        return json.load(stream)


def register_fonts(source_dir: Path) -> None:
    font_dir = source_dir / "assets" / "fonts"
    pdfmetrics.registerFont(TTFont(
        FONT_HEADING, str(font_dir / "Montserrat-SemiBold.ttf")))
    pdfmetrics.registerFont(TTFont(
        FONT_BODY, str(font_dir / "Lato-Regular.ttf")))
    pdfmetrics.registerFont(TTFont(
        FONT_BODY_BOLD, str(font_dir / "Lato-Bold.ttf")))


def wrap_text(text: str, font_name: str, font_size: float, width: float) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if pdfmetrics.stringWidth(candidate, font_name, font_size) <= width:
            current = candidate
            continue
        if not current:
            raise ValueError(f"Word is wider than the text area: {word}")
        lines.append(current)
        current = word
    if current:
        lines.append(current)
    return lines


def draw_paragraphs(
        pdf: canvas.Canvas,
        paragraphs: list[str],
        x: float,
        top: float,
        width: float,
        font_name: str = FONT_BODY,
        font_size: float = 8.8,
        leading: float = 11.2,
        color=INK,
        paragraph_gap: float = 5.0) -> float:
    text = pdf.beginText(x, top)
    text.setFont(font_name, font_size)
    text.setLeading(leading)
    text.setFillColor(color)
    cursor = top
    for index, paragraph in enumerate(paragraphs):
        if index:
            text.moveCursor(0, paragraph_gap)
            cursor -= paragraph_gap
        for line in wrap_text(paragraph, font_name, font_size, width):
            text.textLine(line)
            cursor -= leading
    pdf.drawText(text)
    return cursor


def draw_drop_cap_paragraph(
        pdf: canvas.Canvas,
        paragraph: str,
        x: float,
        top: float,
        width: float) -> float:
    first_letter = paragraph[0]
    remaining = paragraph[1:].lstrip()
    font_size = 8.8
    leading = 11.2
    cap_size = 28
    cap_width = pdfmetrics.stringWidth(
        first_letter, FONT_HEADING, cap_size) + 7
    cap_baseline = (
        top
        + pdfmetrics.getAscent(FONT_BODY, font_size)
        - pdfmetrics.getAscent(FONT_HEADING, cap_size))

    pdf.setFillColor(INK)
    pdf.setFont(FONT_HEADING, cap_size)
    pdf.drawString(x, cap_baseline, first_letter)

    first_width = width - cap_width
    first_lines = wrap_text(remaining, FONT_BODY, font_size, first_width)
    text = pdf.beginText(x + cap_width, top)
    text.setFont(FONT_BODY, font_size)
    text.setLeading(leading)
    text.setFillColor(INK)
    line_count = min(3, len(first_lines))
    for line in first_lines[:line_count]:
        text.textLine(line)
    pdf.drawText(text)

    rest_words = " ".join(first_lines[line_count:])
    cursor = top - line_count * leading
    if rest_words:
        cursor = draw_paragraphs(pdf, [rest_words], x, cursor, width)
    return cursor


def draw_cover_image(
        pdf: canvas.Canvas,
        image_path: Path,
        x: float,
        y: float,
        width: float,
        height: float) -> None:
    target_size = (
        round(width * 300 / 72),
        round(height * 300 / 72))
    with Image.open(image_path) as source:
        prepared = ImageOps.fit(
            source.convert("RGB"),
            target_size,
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5))
        buffer = BytesIO()
        prepared.save(
            buffer,
            format="JPEG",
            quality=90,
            optimize=False,
            progressive=False,
            subsampling=0)
    buffer.seek(0)
    pdf.drawImage(
        ImageReader(buffer),
        x,
        y,
        width,
        height,
        preserveAspectRatio=False,
        mask="auto")


def draw_kicker(pdf: canvas.Canvas, text: str, y: float) -> None:
    pdf.setStrokeColor(RUST)
    pdf.setLineWidth(2.2)
    pdf.line(MARGIN, y + 2.5, MARGIN + 8 * mm, y + 2.5)
    pdf.setFillColor(RUST)
    pdf.setFont(FONT_BODY_BOLD, 7.2)
    pdf.drawString(MARGIN + 11 * mm, y, text)


def draw_caption(
        pdf: canvas.Canvas,
        label: str,
        text: str,
        x: float,
        y: float,
        width: float) -> None:
    label_width = pdfmetrics.stringWidth(label, FONT_BODY_BOLD, 6.3)
    pdf.setFillColor(RUST)
    pdf.setFont(FONT_BODY_BOLD, 6.3)
    pdf.drawString(x, y, label)
    pdf.setFillColor(MUTED)
    pdf.setFont(FONT_BODY, 6.3)
    pdf.drawString(x + label_width + 6, y, text)


def draw_header(pdf: canvas.Canvas, publication: str, issue: str, page_number: int) -> None:
    top = PAGE_HEIGHT - MARGIN
    pdf.setFillColor(RUST)
    pdf.rect(MARGIN, top - 1.2, 5, 5, stroke=0, fill=1)
    pdf.setFillColor(INK)
    pdf.setFont(FONT_HEADING, 8.8)
    pdf.drawString(MARGIN + 10, top, publication)
    pdf.setFillColor(MUTED)
    pdf.setFont(FONT_BODY_BOLD, 7.4)
    pdf.drawRightString(PAGE_WIDTH - MARGIN, top, issue)
    pdf.setStrokeColor(INK)
    pdf.setLineWidth(0.55)
    pdf.line(MARGIN, top - 8, PAGE_WIDTH - MARGIN, top - 8)

    footer_y = 14 * mm
    pdf.setStrokeColor(PALE_OCEAN)
    pdf.setLineWidth(0.45)
    pdf.line(MARGIN, footer_y, PAGE_WIDTH - MARGIN, footer_y)
    pdf.setFillColor(MUTED)
    pdf.setFont(FONT_BODY_BOLD, 6.6)
    pdf.drawString(MARGIN, 8.5 * mm, "MORROW TIDE JOURNAL / VOL. 01")
    pdf.setFillColor(RUST)
    pdf.setFont(FONT_BODY_BOLD, 7.0)
    pdf.drawRightString(PAGE_WIDTH - MARGIN, 8.5 * mm, str(page_number))


def draw_page_one(pdf: canvas.Canvas, content: dict, source_dir: Path) -> None:
    page = content["pageOne"]
    draw_header(pdf, content["publication"], content["issue"], 1)

    draw_kicker(pdf, "ATLANTIC FIELD NOTES", PAGE_HEIGHT - 27 * mm)

    pdf.setFillColor(INK)
    pdf.setFont(FONT_HEADING, 29)
    pdf.drawString(MARGIN, PAGE_HEIGHT - 42 * mm, page["headline"])
    pdf.setFont(FONT_BODY, 11)
    pdf.setFillColor(MUTED)
    pdf.drawString(MARGIN, PAGE_HEIGHT - 51 * mm, page["deck"])
    pdf.setFont(FONT_BODY_BOLD, 7.2)
    pdf.setFillColor(INK)
    pdf.drawString(MARGIN, PAGE_HEIGHT - 58 * mm, page["byline"])

    image_y = PAGE_HEIGHT - 159 * mm
    image_height = 94 * mm
    image_width = PAGE_WIDTH - 2 * MARGIN
    draw_cover_image(
        pdf,
        source_dir / "assets" / "photos" / "hero-cliffs.jpg",
        MARGIN,
        image_y,
        image_width,
        image_height)
    draw_caption(pdf, "FIG. 01", page["caption"], MARGIN, image_y - 9, image_width)

    gap = 5 * mm
    usable_width = PAGE_WIDTH - 2 * MARGIN
    main_width = 58 * mm
    sidebar_width = usable_width - 2 * main_width - 2 * gap
    text_top = image_y - 20
    first_x = MARGIN
    second_x = first_x + main_width + gap
    sidebar_x = second_x + main_width + gap

    cursor = draw_drop_cap_paragraph(
        pdf, page["columnOne"][0], first_x, text_top, main_width)
    draw_paragraphs(
        pdf, page["columnOne"][1:], first_x, cursor - 5, main_width)
    draw_paragraphs(pdf, page["columnTwo"], second_x, text_top, main_width)

    sidebar_bottom = 19 * mm
    sidebar_top = text_top + 7
    pdf.setFillColor(SAND)
    pdf.roundRect(
        sidebar_x,
        sidebar_bottom,
        sidebar_width,
        sidebar_top - sidebar_bottom,
        2.5,
        stroke=0,
        fill=1)
    pdf.setFillColor(OCEAN)
    pdf.rect(
        sidebar_x,
        sidebar_top - 3,
        sidebar_width,
        3,
        stroke=0,
        fill=1)
    inset = 5 * mm
    sidebar_text_width = sidebar_width - 2 * inset
    pdf.setFillColor(PALE_OCEAN)
    pdf.setFont(FONT_HEADING, 24)
    pdf.drawRightString(
        sidebar_x + sidebar_width - inset,
        sidebar_top - 20,
        "01")
    pdf.setFillColor(OCEAN)
    pdf.setFont(FONT_HEADING, 10.5)
    pdf.drawString(sidebar_x + inset, sidebar_top - 15, page["sidebarTitle"])
    rule_y = sidebar_top - 23
    pdf.setStrokeColor(OCEAN)
    pdf.setLineWidth(1.2)
    pdf.line(sidebar_x + inset, rule_y, sidebar_x + sidebar_width - inset, rule_y)
    body_cursor = draw_paragraphs(
        pdf,
        [page["sidebarBody"]],
        sidebar_x + inset,
        rule_y - 11,
        sidebar_text_width,
        font_size=8.0,
        leading=10.1)
    facts_y = body_cursor - 9
    for label, value in page["sidebarFacts"]:
        pdf.setFillColor(RUST)
        pdf.setFont(FONT_BODY_BOLD, 6.5)
        pdf.drawString(sidebar_x + inset, facts_y, label)
        facts_y -= 9
        pdf.setFillColor(INK)
        pdf.setFont(FONT_BODY, 7.5)
        for line in wrap_text(value, FONT_BODY, 7.5, sidebar_text_width):
            pdf.drawString(sidebar_x + inset, facts_y, line)
            facts_y -= 9
        facts_y -= 4

    pdf.showPage()


def draw_page_two(pdf: canvas.Canvas, content: dict, source_dir: Path) -> None:
    page = content["pageTwo"]
    draw_header(pdf, content["publication"], content["issue"], 2)

    draw_kicker(pdf, "THREE STOPS / ONE DAY", PAGE_HEIGHT - 27 * mm)
    pdf.setFillColor(INK)
    pdf.setFont(FONT_HEADING, 27)
    pdf.drawString(MARGIN, PAGE_HEIGHT - 42 * mm, page["headline"])
    pdf.setFillColor(MUTED)
    pdf.setFont(FONT_BODY, 11)
    pdf.drawString(MARGIN, PAGE_HEIGHT - 51 * mm, page["deck"])

    image_y = PAGE_HEIGHT - 145 * mm
    image_height = 87 * mm
    image_width = PAGE_WIDTH - 2 * MARGIN
    draw_cover_image(
        pdf,
        source_dir / "assets" / "photos" / "dune-grass.jpg",
        MARGIN,
        image_y,
        image_width,
        image_height)
    draw_caption(
        pdf, "FIG. 01", page["duneCaption"], MARGIN, image_y - 9, image_width)

    gap = 5 * mm
    usable_width = PAGE_WIDTH - 2 * MARGIN
    column_width = (usable_width - 2 * gap) / 3
    text_top = image_y - 26
    for index, section in enumerate(page["sections"]):
        x = MARGIN + index * (column_width + gap)
        pdf.setFillColor(RUST)
        pdf.setFont(FONT_HEADING, 9.0)
        pdf.drawString(x, text_top, section["number"])
        pdf.setFillColor(INK)
        pdf.setFont(FONT_HEADING, 10.5)
        pdf.drawString(x + 18, text_top, section["title"])
        pdf.setStrokeColor(OCEAN)
        pdf.setLineWidth(1.1)
        pdf.line(x, text_top - 7, x + column_width, text_top - 7)
        draw_paragraphs(
            pdf,
            [section["body"]],
            x,
            text_top - 20,
            column_width,
            font_size=8.4,
            leading=10.7)

    inset_width = usable_width
    inset_height = 44 * mm
    inset_x = MARGIN
    inset_y = 32 * mm
    draw_cover_image(
        pdf,
        source_dir / "assets" / "photos" / "coastal-village.jpg",
        inset_x,
        inset_y,
        inset_width,
        inset_height)
    caption_height = 7 * mm
    pdf.setFillColor(SAND)
    pdf.rect(
        inset_x,
        inset_y - caption_height,
        inset_width,
        caption_height,
        stroke=0,
        fill=1)
    draw_caption(
        pdf,
        "FIG. 02",
        page["villageCaption"],
        inset_x + 4 * mm,
        inset_y - 4.5 * mm,
        inset_width - 8 * mm)

    pdf.showPage()


def create_pdf(output: Path) -> None:
    source_dir = Path(__file__).resolve().parent
    register_fonts(source_dir)
    content = load_content(source_dir)
    output.parent.mkdir(parents=True, exist_ok=True)

    pdf = canvas.Canvas(
        str(output),
        pagesize=(PAGE_WIDTH, PAGE_HEIGHT),
        pageCompression=1,
        invariant=1,
        initialFontName=FONT_BODY,
        initialFontSize=10,
        initialLeading=12)
    pdf.setTitle("Morrow Tide Journal - Atlantic Coast")
    pdf.setAuthor("Morrow Tide Studio")
    pdf.setSubject("Original fictional travel editorial")
    pdf.setCreator("Morrow Tide Journal source kit")

    pdf.setFillColor(PAPER)
    pdf.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_page_one(pdf, content, source_dir)
    pdf.setFillColor(PAPER)
    pdf.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_page_two(pdf, content, source_dir)
    pdf.save()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create the Morrow Tide Journal source PDF.")
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    create_pdf(parse_args().output.resolve())
