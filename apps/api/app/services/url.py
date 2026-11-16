"""Fetch a product page and extract readable text."""

import httpx
from bs4 import BeautifulSoup

USER_AGENT = "AI-Live-Copilot/0.1 (+https://github.com/XY-code1/AI-Live-Copilot)"
TIMEOUT = 15.0
MAX_CHARS = 20_000


def fetch_url_text(url: str) -> tuple[str, str]:
    """Return (title, text) for a product URL."""
    try:
        response = httpx.get(
            url,
            timeout=TIMEOUT,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise ValueError(f"无法抓取链接：{exc}") from exc

    soup = BeautifulSoup(response.text, "html.parser")
    for element in soup(["script", "style", "noscript"]):
        element.decompose()

    title = soup.title.get_text(strip=True) if soup.title else url
    text = soup.get_text("\n", strip=True)
    return title[:255], text[:MAX_CHARS]
