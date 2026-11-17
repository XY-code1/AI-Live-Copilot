"""Securely fetch a public product page and extract readable text."""

import ipaddress
import re
import socket
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from app.core.config import settings

USER_AGENT = "AI-Live-Copilot/1.1 (+https://github.com/XY-code1/AI-Live-Copilot)"
TIMEOUT = 15.0
MAX_CHARS = 50_000
MAX_REDIRECTS = 5
URL_PATTERN = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)


def normalize_shared_url(value: str) -> str:
    """Extract an HTTP URL from copied share text, including escaped separators."""
    match = URL_PATTERN.search(value.replace(r"\://", "://"))
    if match is None:
        raise ValueError("未在分享内容中找到有效的 HTTP/HTTPS 链接")
    return match.group(0).rstrip(".,;:!?，。；：！？）)]}")


def _validate_public_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("只允许有效的 HTTP/HTTPS 链接")
    if parsed.username or parsed.password:
        raise ValueError("链接中不能包含账号信息")
    try:
        addresses = socket.getaddrinfo(parsed.hostname, parsed.port or 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError("链接域名无法解析") from exc
    for address in addresses:
        if not ipaddress.ip_address(address[4][0]).is_global:
            raise ValueError("不允许访问本机、内网或保留地址")


def fetch_url_text(url: str) -> tuple[str, str]:
    current = url
    try:
        with httpx.Client(timeout=TIMEOUT, follow_redirects=False, headers={"User-Agent": USER_AGENT}) as client:
            for _ in range(MAX_REDIRECTS + 1):
                _validate_public_url(current)
                with client.stream("GET", current) as response:
                    if response.is_redirect:
                        location = response.headers.get("location")
                        if not location:
                            raise ValueError("重定向缺少目标地址")
                        current = urljoin(current, location)
                        continue
                    response.raise_for_status()
                    content_type = response.headers.get("content-type", "").lower()
                    if not any(item in content_type for item in ("text/html", "text/plain", "application/xhtml")):
                        raise ValueError("链接返回的不是可解析网页")
                    chunks: list[bytes] = []
                    size = 0
                    for chunk in response.iter_bytes():
                        size += len(chunk)
                        if size > settings.max_url_response_bytes:
                            raise ValueError("网页内容超过大小限制")
                        chunks.append(chunk)
                    body = b"".join(chunks).decode(response.encoding or "utf-8", errors="replace")
                    break
            else:
                raise ValueError("链接重定向次数过多")
    except httpx.HTTPError as exc:
        raise ValueError(f"无法抓取链接：{exc}") from exc

    soup = BeautifulSoup(body, "html.parser")
    for element in soup(["script", "style", "noscript", "iframe"]):
        element.decompose()
    title = soup.title.get_text(strip=True) if soup.title else current
    return title[:255], soup.get_text("\n", strip=True)[:MAX_CHARS]
