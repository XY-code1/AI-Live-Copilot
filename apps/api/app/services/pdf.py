"""PDF text extraction. Kept separate so OCR/multimodal can be added later."""

import fitz  # PyMuPDF


def extract_pdf_text(data: bytes) -> tuple[str, int]:
    """Return (extracted text, page count) from PDF bytes."""
    with fitz.open(stream=data, filetype="pdf") as document:
        pages = [page.get_text("text") for page in document]
        page_count = len(pages)
    text = "\n\n".join(page.strip() for page in pages if page.strip())
    return text, page_count
