"""Server-side article extraction.

Fetches an allowlisted article page once during background ingestion, checks robots.txt,
and extracts the facts the editorial pipeline needs: canonical URL, publication date,
headline, main body text and a permitted Open Graph image. The extracted body text is
used as synthesis input and to build a well-formed excerpt — it is never published
verbatim as NOVA copy.
"""

import ipaddress
import logging
import re
import socket
import time
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup

from .sources import ALLOWED_HOSTS

logger = logging.getLogger(__name__)

USER_AGENT = ("NovaKonutNewsroomBot/1.0 (+https://nova.istanbul; newsroom aggregation; "
              "contact: info@novakonut.com)")
TIMEOUT = 15.0
MAX_BYTES = 2 * 1024 * 1024
DROP_TAGS = ("script", "style", "noscript", "nav", "header", "footer", "aside", "form",
             "figure", "figcaption", "iframe", "svg", "button")
PAYWALL_HINTS = ("subscribe to continue", "subscribers only", "abone olun",
                 "this article is for subscribers", "become a member to read",
                 "sign in to read the full", "paywall")
_ROBOTS: dict[str, tuple[float, RobotFileParser | None]] = {}
ROBOTS_TTL = 6 * 3600
_MONTHS_TR = {
    "ocak": 1, "şubat": 2, "subat": 2, "mart": 3, "nisan": 4, "mayıs": 5, "mayis": 5,
    "haziran": 6, "temmuz": 7, "ağustos": 8, "agustos": 8, "eylül": 9, "eylul": 9,
    "ekim": 10, "kasım": 11, "kasim": 11, "aralık": 12, "aralik": 12,
}


def host_allowed(url: str) -> bool:
    parsed = urlparse(url or "")
    return parsed.scheme == "https" and parsed.hostname in ALLOWED_HOSTS


def _public_host(host: str) -> bool:
    try:
        infos = socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        return False
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            return False
    return True


async def robots_allows(url: str) -> bool:
    """Honour robots.txt for our own user agent; a missing robots.txt means allowed."""
    parsed = urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    cached = _ROBOTS.get(origin)
    now = time.time()
    if not cached or now - cached[0] > ROBOTS_TTL:
        parser: RobotFileParser | None = None
        try:
            async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as http:
                res = await http.get(f"{origin}/robots.txt", headers={"User-Agent": USER_AGENT})
            if res.status_code == 200 and "html" not in res.headers.get("content-type", ""):
                parser = RobotFileParser()
                parser.parse(res.text.splitlines())
        except Exception:
            parser = None
        _ROBOTS[origin] = (now, parser)
        cached = _ROBOTS[origin]
    parser = cached[1]
    if parser is None:
        return True
    return parser.can_fetch(USER_AGENT, url) or parser.can_fetch("*", url)


async def fetch_html(url: str) -> str:
    """Fetch an allowlisted, robots-permitted HTML page. Returns '' when not permitted."""
    if not host_allowed(url) or not _public_host(urlparse(url).hostname):
        return ""
    if not await robots_allows(url):
        logger.info("news: robots.txt disallows %s", url[:120])
        return ""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True,
                                     max_redirects=4) as http:
            res = await http.get(url, headers={"User-Agent": USER_AGENT,
                                               "Accept": "text/html,application/xhtml+xml"})
        if res.status_code != 200 or "text/html" not in res.headers.get("content-type", ""):
            return ""
        return res.content[:MAX_BYTES].decode(res.encoding or "utf-8", errors="replace")
    except Exception as exc:
        logger.info("news: article fetch failed (%s) %s", type(exc).__name__, url[:120])
        return ""


def _meta(soup: BeautifulSoup, *keys: str) -> str:
    for key in keys:
        for attr in ("property", "name", "itemprop"):
            node = soup.find("meta", attrs={attr: key})
            if node and node.get("content"):
                return node["content"].strip()
    return ""


def _parse_date(value: str) -> datetime | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.astimezone(timezone.utc) if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except Exception:
        pass
    match = re.search(r"(\d{1,2})\s+([A-Za-zÇĞİÖŞÜçğıöşü]+)\s+(\d{4})", value)
    if match:
        month = _MONTHS_TR.get(match.group(2).lower())
        if month:
            try:
                return datetime(int(match.group(3)), month, int(match.group(1)), 9,
                                tzinfo=timezone.utc)
            except ValueError:
                return None
    match = re.search(r"(\d{4})-(\d{2})-(\d{2})", value)
    if match:
        return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)), 9,
                        tzinfo=timezone.utc)
    return None


def _published_at(soup: BeautifulSoup) -> datetime | None:
    for value in (_meta(soup, "article:published_time", "datePublished", "publish-date",
                        "pubdate", "date"),):
        parsed = _parse_date(value)
        if parsed:
            return parsed
    for node in soup.find_all("time"):
        parsed = _parse_date(node.get("datetime") or node.get_text(" ", strip=True))
        if parsed:
            return parsed
    return None


def _body_paragraphs(soup: BeautifulSoup) -> list[str]:
    for tag in soup.find_all(DROP_TAGS):
        tag.decompose()
    containers = soup.select("article, [itemprop=articleBody], .article-body, .post-content, "
                             ".entry-content, .article__body, .detay-icerik, .detay-metin, "
                             "main") or [soup]
    best: list[str] = []
    for container in containers:
        paragraphs = _paragraphs_in(container)
        if sum(len(p.split()) for p in paragraphs) > sum(len(p.split()) for p in best):
            best = paragraphs
    if not best:
        best = _paragraphs_in(soup, min_words=6)
    seen: set[str] = set()
    unique = []
    for text in best:
        key = text[:80].lower()
        if key not in seen:
            seen.add(key)
            unique.append(text)
    return unique[:60]


def _paragraphs_in(container, min_words: int = 8) -> list[str]:
    paragraphs = []
    for node in container.find_all(["p", "h2", "h3"]):
        text = re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip()
        if len(text.split()) >= min_words and not text.lower().startswith(("photo:", "image:")):
            paragraphs.append(text)
    return paragraphs


async def extract_article(url: str) -> dict:
    """Return extracted article facts. `ok` is False when nothing usable was retrieved."""
    html = await fetch_html(url)
    if not html:
        return {"ok": False, "reason": "not-retrievable", "paragraphs": [], "text": "",
                "word_count": 0}
    soup = BeautifulSoup(html, "html.parser")
    headline = _meta(soup, "og:title", "twitter:title") or (
        soup.title.get_text(strip=True) if soup.title else "")
    description = _meta(soup, "og:description", "description", "twitter:description")
    og_image = _meta(soup, "og:image:secure_url", "og:image")
    twitter_image = _meta(soup, "twitter:image", "twitter:image:src")
    json_ld_image = _json_ld_image(soup)
    canonical_node = soup.find("link", rel=lambda v: v and "canonical" in v)
    canonical = (canonical_node.get("href") if canonical_node else "") or ""
    published = _published_at(soup)
    paragraphs = _body_paragraphs(soup)
    text = " ".join(paragraphs)
    lowered = text.lower()
    return {
        "ok": True,
        "headline": headline,
        "description": description,
        "og_image": urljoin(url, og_image) if og_image else "",
        "twitter_image": urljoin(url, twitter_image) if twitter_image else "",
        "json_ld_image": urljoin(url, json_ld_image) if json_ld_image else "",
        "canonical": urljoin(url, canonical) if canonical else "",
        "published_at": published,
        "paragraphs": paragraphs,
        "text": text,
        "word_count": len(text.split()),
        "paywalled": any(hint in lowered for hint in PAYWALL_HINTS),
    }


def _json_ld_image(soup: BeautifulSoup) -> str:
    """First image reference declared in schema.org JSON-LD, if any."""
    import json

    def first_url(value):
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            return first_url(value.get("url") or value.get("contentUrl"))
        if isinstance(value, list):
            for entry in value:
                found = first_url(entry)
                if found:
                    return found
        return ""

    for node in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(node.get_text() or "{}")
        except Exception:
            continue
        blocks = data if isinstance(data, list) else [data]
        for block in blocks:
            if not isinstance(block, dict):
                continue
            graph = block.get("@graph") if isinstance(block.get("@graph"), list) else [block]
            for entry in graph:
                if isinstance(entry, dict):
                    url = first_url(entry.get("image") or entry.get("thumbnailUrl"))
                    if url and url.startswith("https://"):
                        return url
    return ""
