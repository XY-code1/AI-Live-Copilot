"""Content sufficiency rules for fetched/uploaded sources.

Pure rules - no model involved. Determines whether a source has enough content
to be useful, and flags restricted pages instead of silently returning empty.
"""

from dataclasses import dataclass

MIN_USEFUL_CHARS = 200

RESTRICTED_MARKERS = (
    "登录后查看",
    "请登录",
    "验证码",
    "访问受限",
    "页面不存在",
    "内容不存在",
    "商品已下架",
    "security verification",
    "are you a robot",
)


@dataclass(frozen=True)
class Assessment:
    sufficiency: str  # sufficient | insufficient | restricted
    reason: str


def assess(text: str, *, is_url: bool = False) -> Assessment:
    cleaned = (text or "").strip()
    lowered = cleaned.lower()

    if any(marker.lower() in lowered for marker in RESTRICTED_MARKERS):
        return Assessment("restricted", "页面提示需要登录/验证或内容不可见（受限页面）")

    if len(cleaned) < MIN_USEFUL_CHARS:
        if is_url:
            return Assessment(
                "insufficient",
                "抓取内容过少，可能需要浏览器渲染或手动上传页面快照",
            )
        return Assessment("insufficient", "内容过少，建议补充资料或上传快照")

    return Assessment("sufficient", "内容充分")
