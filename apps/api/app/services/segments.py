"""Structured segments for static sources (PDF pages/tables, HTML blocks, JSON-LD)."""

from dataclasses import dataclass
from typing import Any

import fitz
from bs4 import BeautifulSoup


@dataclass
class SegmentDraft:
    kind: str
    position: int
    content: str = ""
    page_no: int | None = None
    structured: Any = None


def pdf_segments(data: bytes) -> list[SegmentDraft]:
    """Per-page text plus extracted tables."""
    drafts: list[SegmentDraft] = []
    position = 0
    with fitz.open(stream=data, filetype="pdf") as document:
        for page_index, page in enumerate(document, start=1):
            text = page.get_text("text").strip()
            if text:
                drafts.append(
                    SegmentDraft(kind="page", position=position, content=text, page_no=page_index)
                )
                position += 1
            else:
                drafts.append(
                    SegmentDraft(
                        kind="page",
                        position=position,
                        content="",
                        page_no=page_index,
                        structured={"needs_ocr": True},
                    )
                )
                position += 1
            try:
                tables = page.find_tables()
            except Exception:  # noqa: BLE001 - table detection is best-effort
                tables = []
            for table in tables:
                rows = table.extract()
                if not rows:
                    continue
                drafts.append(
                    SegmentDraft(
                        kind="table",
                        position=position,
                        content="",
                        page_no=page_index,
                        structured={"rows": rows},
                    )
                )
                position += 1
    return drafts


def url_segments(html: str) -> list[SegmentDraft]:
    """Headings, paragraphs, tables and JSON-LD from a fetched page."""
    soup = BeautifulSoup(html, "html.parser")

    drafts: list[SegmentDraft] = []
    position = 0
    # JSON-LD must be collected before dropping <script> elements.
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        payload = script.string or script.get_text()
        if payload and payload.strip():
            drafts.append(
                SegmentDraft(kind="jsonld", position=position, content=payload.strip())
            )
            position += 1

    for element in soup(["script", "style", "noscript", "iframe"]):
        element.decompose()

    for node in soup.find_all(["h1", "h2", "h3", "h4", "p", "li"]):
        text = node.get_text(" ", strip=True)
        if not text:
            continue
        kind = "heading" if node.name.startswith("h") else "paragraph"
        drafts.append(SegmentDraft(kind=kind, position=position, content=text))
        position += 1

    for table in soup.find_all("table"):
        rows = []
        for row in table.find_all("tr"):
            cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"])]
            if cells:
                rows.append(cells)
        if rows:
            drafts.append(
                SegmentDraft(
                    kind="table",
                    position=position,
                    content="",
                    structured={"rows": rows},
                )
            )
            position += 1

    return drafts


def image_segments(text: str) -> list[SegmentDraft]:
    return [SegmentDraft(kind="page", position=0, content=text, structured={"ocr": True})]
