from functools import lru_cache
from io import BytesIO

import numpy as np
from PIL import Image


@lru_cache(maxsize=1)
def _engine():
    try:
        from paddleocr import PaddleOCR
    except ImportError as exc:
        raise RuntimeError("OCR 组件未安装，请使用 OCR 依赖组部署") from exc
    return PaddleOCR(
        lang="ch",
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )


def extract_image_text(data: bytes) -> str:
    try:
        image = Image.open(BytesIO(data)).convert("RGB")
        image.load()
    except Exception as exc:
        raise ValueError("图片格式无效或已经损坏") from exc
    results = _engine().predict(np.asarray(image))
    lines: list[str] = []
    for result in results:
        payload = getattr(result, "json", result)
        if callable(payload):
            payload = payload()
        if isinstance(payload, dict):
            payload = payload.get("res", payload)
            texts = payload.get("rec_texts", []) if isinstance(payload, dict) else []
            lines.extend(str(text).strip() for text in texts if str(text).strip())
    if not lines:
        raise ValueError("图片中没有识别到文字")
    return "\n".join(lines)

