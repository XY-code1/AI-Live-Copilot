"""Structured segments for static sources (PDF pages/tables, HTML blocks, JSON-LD)."""

from dataclasses import dataclass
from typing import Any

import fitz
from bs4 import BeautifulSoup, Tag


@dataclass
class SegmentDraft:
    kind: str
    position: int
    content: str = ""
    page_no: int | None = None
    structured: Any = None
    locator: str | None = None
    heading_level: int | None = None


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


def _locator(element: Tag) -> str:
    parts: list[str] = []
    current: Tag | None = element
    while current is not None and current.name != "[document]":
        part = current.name
        element_id = current.get("id")
        if element_id:
            part += f"#{element_id}"
        elif isinstance(current.parent, Tag):
            siblings = current.parent.find_all(current.name, recursive=False)
            if len(siblings) > 1:
                part += f":nth-of-type({siblings.index(current) + 1})"
        parts.append(part)
        current = current.parent if isinstance(current.parent, Tag) else None
    return " > ".join(reversed(parts))


def url_segments(html: str) -> list[SegmentDraft]:
    """JSON-LD, headings, paragraphs, lists and tables from a fetched page, with locators."""
    soup = BeautifulSoup(html, "html.parser")

    drafts: list[SegmentDraft] = []
    position = 0
    # JSON-LD must be collected before other elements are walked.
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        payload = script.string or script.get_text()
        if payload and payload.strip():
            drafts.append(
                SegmentDraft(kind="jsonld", position=position, content=payload.strip())
            )
            position += 1

    for element in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "ul", "ol", "table"]):
        if element.find_parent(["script", "style", "noscript", "iframe"]):
            continue
        if element.name in {"ul", "ol"}:
            items = [
                item for item in (
                    li.get_text(" ", strip=True) for li in element.find_all("li", recursive=False)
                ) if item
            ]
            if not items:
                continue
            draft = SegmentDraft(
                kind="list",
                position=position,
                content="\n".join(f"- {item}" for item in items),
                structured={"list_type": element.name, "item_count": len(items)},
                locator=_locator(element),
            )
        elif element.name == "table":
            rows = []
            for row in element.find_all("tr"):
                cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"])]
                if cells:
                    rows.append(cells)
            if not rows:
                continue
            draft = SegmentDraft(
                kind="table",
                position=position,
                structured={"rows": rows},
                locator=_locator(element),
            )
        else:
            text = element.get_text(" ", strip=True)
            if not text:
                continue
            is_heading = element.name.startswith("h")
            draft = SegmentDraft(
                kind="heading" if is_heading else "paragraph",
                position=position,
                content=text,
                locator=_locator(element),
                heading_level=int(element.name[1]) if is_heading else None,
            )
        drafts.append(draft)
        position += 1

    return drafts


def image_segments(text: str) -> list[SegmentDraft]:
    return [SegmentDraft(kind="page", position=0, content=text, structured={"ocr": True})]
