"""Best-effort, source-attributed preview images for public news links.

Only a small, diverse set of Google News publisher pages is inspected per
report. Existing RSS media remains preferred, YouTube uses its official
thumbnail host, and unavailable/unsafe metadata is simply omitted.
"""

from __future__ import annotations

import ipaddress
import re
import socket
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from app.domain.models import IntelligenceItem


class _ImageMetaParser(HTMLParser):
    """Extract only publisher-declared Open Graph/Twitter image URLs."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.image = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "meta" or self.image:
            return
        values = {key.lower(): value or "" for key, value in attrs}
        key = (values.get("property") or values.get("name") or "").lower()
        if key in {"og:image", "og:image:secure_url", "twitter:image", "twitter:image:src"}:
            self.image = values.get("content", "").strip()


def _public_https(url: str, *, resolve: bool = True) -> bool:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        return False
    host = parsed.hostname.rstrip(".").lower()
    if parsed.port not in (None, 443) or host == "localhost" or host.endswith((".localhost", ".local", ".internal")):
        return False
    try:
        address = ipaddress.ip_address(host)
        return address.is_global
    except ValueError:
        pass
    if not re.fullmatch(r"[a-z0-9.-]+", host):
        return False
    if resolve:
        try:
            addresses = {ipaddress.ip_address(result[4][0]) for result in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)}
        except (OSError, ValueError):
            return False
        return bool(addresses) and all(address.is_global for address in addresses)
    return True


class _PublicHttpsRedirects(HTTPRedirectHandler):
    """Do not follow publisher redirects to non-HTTPS or private destinations."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        if not _public_https(newurl):
            return None
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def publisher_image(url: str, timeout: int = 4) -> str:
    """Read a publisher-declared image from a Google News article URL.

    Network and markup failures are non-fatal. The dashboard never manufactures
    a stock image or guesses an image URL from an article title.
    """
    parsed = urlparse(url)
    if parsed.hostname != "news.google.com" or not _public_https(url):
        return ""
    request = Request(url, headers={
        "User-Agent": "DailyIntelligenceHub/0.9.29 (public article preview)",
        "Accept": "text/html,application/xhtml+xml;q=0.9",
        "Accept-Language": "zh-TW,zh;q=0.8,en;q=0.5",
    })
    try:
        with build_opener(_PublicHttpsRedirects()).open(request, timeout=timeout) as response:
            if "html" not in response.headers.get("Content-Type", "").lower():
                return ""
            final_url = response.geturl()
            if not _public_https(final_url):
                return ""
            markup = response.read(1_000_000).decode("utf-8", errors="replace")
    except Exception:  # Third-party pages are optional; isolate every network/parser failure.
        return ""
    parser = _ImageMetaParser()
    try:
        parser.feed(markup)
    except Exception:  # A malformed publisher page must not fail report generation.
        return ""
    candidate = urljoin(final_url, parser.image)
    return candidate if _public_https(candidate) else ""


def enrich_preview_images(items: list[IntelligenceItem], max_pages: int = 10) -> list[IntelligenceItem]:
    """Fetch at most one article image per category (up to ten pages) in parallel."""
    if max_pages <= 0:
        return items
    candidates: list[IntelligenceItem] = []
    categories: set[str] = set()
    for item in items:
        if item.source != "Google News" or item.image_url or item.category in {"冷知識", "每日充電"}:
            continue
        if item.category in categories or urlparse(item.url).hostname != "news.google.com":
            continue
        categories.add(item.category)
        candidates.append(item)
        if len(candidates) >= max_pages:
            break
    if not candidates:
        return items

    with ThreadPoolExecutor(max_workers=5, thread_name_prefix="preview-image") as pool:
        images = list(pool.map(lambda item: publisher_image(item.url), candidates))
    image_by_url = {item.url: image for item, image in zip(candidates, images) if image}
    return [replace(item, image_url=image_by_url[item.url]) if item.url in image_by_url else item for item in items]
