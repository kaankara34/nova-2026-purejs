"""Robots-aware listing crawler for institutional sites that publish no feed.

Only configured, allowlisted hosts are read. For each listing page the crawler collects
article links matching the configured pattern, then extracts title, date, text and image
from the article page itself. The output is shaped exactly like a parsed feed item so the
ingestion pipeline treats both paths identically.
"""

import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .extract import extract_article, fetch_html

logger = logging.getLogger(__name__)

MAX_ARTICLES_PER_TARGET = 14


async def _listing_links(target: dict) -> list[str]:
    pattern = re.compile(target["link_pattern"])
    links: list[str] = []
    seen: set[str] = set()
    for list_url in target["list_urls"]:
        html = await fetch_html(list_url)
        if not html:
            logger.warning("news: crawl listing unavailable for %s (%s)", target["key"], list_url)
            continue
        soup = BeautifulSoup(html, "html.parser")
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"].split("?")[0].split("#")[0]
            if not pattern.match(href):
                continue
            absolute = urljoin(list_url, href)
            if absolute not in seen:
                seen.add(absolute)
                links.append(absolute)
    return links[:MAX_ARTICLES_PER_TARGET]


async def crawl_target(target: dict) -> list[dict]:
    """Return feed-shaped items for one institutional target."""
    items: list[dict] = []
    for url in await _listing_links(target):
        article = await extract_article(url)
        if not article.get("ok") or not article.get("published_at"):
            continue
        title = article.get("headline") or ""
        if not title:
            continue
        items.append({
            "title": re.sub(r"\s*\|\s*[^|]{2,40}$", "", title).strip(),
            "link": article.get("canonical") or url,
            "guid": url,
            "description": article.get("description") or " ".join(article["paragraphs"][:2]),
            "published": article["published_at"].isoformat(),
            "image": ([article["og_image"]] if article.get("og_image") else [], ""),
            "extracted": article,
        })
    return items
