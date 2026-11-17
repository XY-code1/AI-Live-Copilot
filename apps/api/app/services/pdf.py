"""PDF text extraction. Kept separate so OCR/multimodal can be added later."""

import fitz  # PyMuPDF

from app.core.config import settings


def extract_pdf_text(data: bytes) -> tuple[str, int]:
    """Return (extracted text, page count) from PDF bytes."""
    try:
        with fitz.open(stream=data, filetype="pdf") as document:
            if document.needs_pass:
                raise ValueError("暂不支持加密 PDF")
            page_count = len(document)
            if page_count > settings.max_pdf_pages:
                raise ValueError(f"PDF 页数不能超过 {settings.max_pdf_pages} 页")
            pages = [page.get_text("text") for page in document]
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("PDF 格式无效或已经损坏") from exc
    text = "\n\n".join(page.strip() for page in pages if page.strip())
    return text, page_count
