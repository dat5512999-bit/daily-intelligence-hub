"""Small standard-library HTTP client with a safe timeout."""

from __future__ import annotations

import re
from collections.abc import Mapping
from urllib.request import Request, urlopen


def get_text(url: str, timeout: int = 12, headers: Mapping[str, str] | None = None) -> str:
    """Fetch a public endpoint using a clear, non-browser-spoofing identity."""
    request_headers = {
        "User-Agent": "DailyIntelligenceHub/0.9.12 (personal public research; contact: github.com/dat5512999-bit)",
        "Accept": "application/atom+xml, application/rss+xml, application/json, text/xml, application/xml, text/html;q=0.9, */*;q=0.5",
        "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.7",
    }
    if headers:
        request_headers.update(headers)
    request = Request(url, headers=request_headers)
    with urlopen(request, timeout=timeout) as response:  # nosec B310: URLs are fixed source endpoints.
        return response.read().decode("utf-8", errors="replace")


def clean_xml(text: str) -> str:
    """Tolerate invalid control characters occasionally returned inside RSS descriptions.

    Some public feeds contain a stray control character or an unescaped ampersand in
    a description.  The feed is still useful, so clean only those invalid XML
    characters before parsing; article titles and links are otherwise untouched.
    """
    without_controls = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    return re.sub(r"&(?!#\d+;|#x[0-9a-fA-F]+;|amp;|lt;|gt;|quot;|apos;)", "&amp;", without_controls)
