"""Parser/version metadata for ingestion evidence."""


def parser_version(kind: str) -> str:
    if kind == "pdf":
        try:
            import pymupdf

            return f"pymupdf {pymupdf.__version__}"
        except Exception:  # noqa: BLE001
            return "pymupdf unknown"
    if kind == "image":
        try:
            import PIL

            return f"pillow {PIL.__version__} (ocr optional)"
        except Exception:  # noqa: BLE001
            return "pillow unknown"
    return "url-fetcher 1.1"
