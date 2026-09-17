"""Server-side newsroom ingestion: fetch -> parse -> sanitise -> dedupe -> score -> store."""

import asyncio
import hashlib
import ipaddress
import logging
import os
import re
import socket
import unicodedata
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import bleach
import html as html_lib
import httpx
from defusedxml import ElementTree as DefusedET
from email.utils import parsedate_to_datetime

from . import summarise
from .filters import is_excluded, normalise, relevance_score
from .sources import ALLOWED_HOSTS, enabled_sources

logger = logging.getLogger(__name__)

USER_AGENT = "NovaKonutNewsroomBot/1.0 (+https://nova.istanbul; newsroom aggregation)"
MAX_BYTES = 4 * 1024 * 1024
MAX_REDIRECTS = 3
FETCH_TIMEOUT = 20.0
MAX_AGE_DAYS = 30
MIN_SCORE = 8
TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "utm_id",
    "fbclid", "gclid", "mc_cid", "mc_eid", "igshid", "ref", "ref_src", "CMP", "cmp",
}
ATOM = "{http://www.w3.org/2005/Atom}"
MEDIA = "{http://search.yahoo.com/mrss/}"
CONTENT = "{http://purl.org/rss/1.0/modules/content/}"
DC = "{http://purl.org/dc/elements/1.1/}"


# ---------------------------------------------------------------- safe fetching
def _host_allowed(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "https" and parsed.hostname in ALLOWED_HOSTS


def _public_ip(host: str) -> bool:
    try:
        infos = socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        return False
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            return False
    return True


async def fetch_feed(url: str, etag: str | None, modified: str | None) -> tuple[int, bytes | None, dict]:
    """Fetch an allowlisted feed. Returns (status, body, response headers)."""
    if not _host_allowed(url):
        raise ValueError("source host is not allowlisted")
    if not _public_ip(urlparse(url).hostname):
        raise ValueError("source host resolves to a non-public address")
    headers = {"User-Agent": USER_AGENT, "Accept": "application/rss+xml, application/atom+xml, application/xml;q=0.9"}
    if etag:
        headers["If-None-Match"] = etag
    if modified:
        headers["If-Modified-Since"] = modified
    async with httpx.AsyncClient(timeout=FETCH_TIMEOUT, follow_redirects=False) as http:
        current = url
        for _ in range(MAX_REDIRECTS + 1):
            res = await http.get(current, headers=headers)
            if res.status_code in (301, 302, 303, 307, 308):
                target = res.headers.get("location", "")
                target = str(httpx.URL(current).join(target))
                if not _host_allowed(target):
                    raise ValueError("redirect target is not allowlisted")
                current = target
                continue
            break
        else:
            raise ValueError("too many redirects")
    if res.status_code == 304:
        return 304, None, dict(res.headers)
    if res.status_code != 200:
        raise ValueError(f"unexpected status {res.status_code}")
    body = res.content[:MAX_BYTES]
    return 200, body, dict(res.headers)


# ---------------------------------------------------------------- parsing
def _text(node) -> str:
    return (node.text or "").strip() if node is not None else ""


def _clean(html: str) -> str:
    """Strip every tag, script, iframe, handler and tracking markup from feed HTML."""
    text = bleach.clean(html or "", tags=[], attributes={}, strip=True, strip_comments=True)
    text = html_lib.unescape(text)
    text = bleach.clean(text, tags=[], attributes={}, strip=True, strip_comments=True)
    text = html_lib.unescape(text)
    return re.sub(r"[\s\u00a0]+", " ", text).strip()


def _parse_date(value: str) -> datetime | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).astimezone(timezone.utc)
    except Exception:
        pass
    try:
        cleaned = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(cleaned)
        return parsed.astimezone(timezone.utc) if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def canonical_url(url: str) -> str:
    parsed = urlparse((url or "").strip())
    if parsed.scheme not in ("http", "https"):
        return ""
    query = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=False) if k not in TRACKING_PARAMS]
    return urlunparse((
        parsed.scheme, parsed.netloc.lower(), parsed.path.rstrip("/") or "/",
        "", urlencode(query), "",
    ))


def _image_from(node) -> tuple[str, str]:
    for media in list(node.findall(f"{MEDIA}content")) + list(node.findall(f"{MEDIA}thumbnail")):
        url = media.get("url", "")
        if url.startswith("https://"):
            credit = _text(node.find(f"{MEDIA}credit")) or ""
            return url, credit
    enclosure = node.find("enclosure")
    if enclosure is not None and (enclosure.get("type", "").startswith("image/")):
        url = enclosure.get("url", "")
        if url.startswith("https://"):
            return url, ""
    return "", ""


def parse_items(body: bytes) -> list[dict]:
    """Parse RSS or Atom with entity expansion disabled."""
    body = body.lstrip(b"\xef\xbb\xbf").lstrip()
    root = DefusedET.fromstring(body, forbid_dtd=False, forbid_entities=True, forbid_external=True)
    items: list[dict] = []
    for node in root.iter("item"):
        items.append({
            "title": _clean(_text(node.find("title"))),
            "link": _text(node.find("link")),
            "guid": _text(node.find("guid")) or _text(node.find(f"{DC}identifier")),
            "description": _clean(_text(node.find("description")) or _text(node.find(f"{CONTENT}encoded"))),
            "published": _text(node.find("pubDate")) or _text(node.find(f"{DC}date")),
            "image": _image_from(node),
        })
    for node in root.iter(f"{ATOM}entry"):
        link = ""
        for candidate in node.findall(f"{ATOM}link"):
            if candidate.get("rel", "alternate") == "alternate":
                link = candidate.get("href", "")
                break
        items.append({
            "title": _clean(_text(node.find(f"{ATOM}title"))),
            "link": link,
            "guid": _text(node.find(f"{ATOM}id")),
            "description": _clean(_text(node.find(f"{ATOM}summary")) or _text(node.find(f"{ATOM}content"))),
            "published": _text(node.find(f"{ATOM}published")) or _text(node.find(f"{ATOM}updated")),
            "image": _image_from(node),
        })
    return items


# ---------------------------------------------------------------- persistence helpers
def slugify(title: str, published: datetime) -> str:
    base = unicodedata.normalize("NFKD", title.lower())
    base = base.replace("ı", "i").replace("ğ", "g").replace("ş", "s").replace("ö", "o").replace("ü", "u").replace("ç", "c")
    base = re.sub(r"[^\w\s-]", "", base.encode("ascii", "ignore").decode())
    base = re.sub(r"[\s_-]+", "-", base).strip("-")[:70] or "nova-journal-item"
    return f"{base}-{published.strftime('%Y%m%d')}"


def content_hash(title: str, description: str) -> str:
    return hashlib.sha256(f"{normalise(title)}|{normalise(description)}".encode()).hexdigest()


async def ensure_indexes(db) -> None:
    await db.news_items.create_index("slug", unique=True)
    await db.news_items.create_index("canonical_url", unique=True)
    await db.news_items.create_index([("published_at", -1)])
    await db.news_items.create_index([("status", 1), ("category", 1), ("published_at", -1)])
    await db.news_items.create_index("content_hash")
    await db.news_items.create_index("title_key")
    await db.news_sources.create_index("key", unique=True)


# ---------------------------------------------------------------- ingestion
async def ingest_source(db, source: dict, ai_budget: list[int]) -> dict:
    state = await db.news_sources.find_one({"key": source["key"]}) or {}
    result = {"source": source["key"], "fetched": 0, "accepted": 0, "duplicates": 0,
              "rejected": 0, "status": "ok"}
    try:
        status, body, headers = await fetch_feed(source["url"], state.get("etag"), state.get("last_modified"))
    except Exception as exc:
        logger.warning("news: fetch failed for %s: %s", source["key"], exc)
        await db.news_sources.update_one(
            {"key": source["key"]},
            {"$set": {"key": source["key"], "name": source["name"], "url": source["url"],
                      "language": source["language"], "enabled": True,
                      "last_error": str(exc)[:200],
                      "last_attempt_at": datetime.now(timezone.utc).isoformat()}},
            upsert=True)
        result["status"] = "failed"
        return result

    now = datetime.now(timezone.utc)
    if status == 304:
        result["status"] = "not-modified"
    else:
        try:
            items = parse_items(body)
        except Exception as exc:
            logger.warning("news: parse failed for %s: %s", source["key"], exc)
            result["status"] = "parse-error"
            items = []
        result["fetched"] = len(items)
        for item in items:
            outcome = await _store_item(db, source, item, now, ai_budget)
            result[outcome] = result.get(outcome, 0) + 1

    await db.news_sources.update_one(
        {"key": source["key"]},
        {"$set": {"key": source["key"], "name": source["name"], "url": source["url"],
                  "language": source["language"], "enabled": True, "last_error": None,
                  "etag": headers.get("etag"), "last_modified": headers.get("last-modified"),
                  "last_attempt_at": now.isoformat(), "last_success_at": now.isoformat()}},
        upsert=True)
    return result


async def _store_item(db, source: dict, item: dict, now: datetime, ai_budget: list[int]) -> str:
    title = item["title"]
    description = item["description"]
    url = canonical_url(item["link"])
    if not title or not url:
        return "rejected"

    published = _parse_date(item["published"]) or now
    if published > now + timedelta(hours=12):
        return "rejected"
    age_days = max((now - published).total_seconds() / 86400.0, 0.0)
    if age_days > MAX_AGE_DAYS:
        return "rejected"

    if is_excluded(title, description):
        return "rejected"

    score, category, matched = relevance_score(title, description, source, age_days)
    if score < MIN_SCORE or not matched:
        return "rejected"

    digest = content_hash(title, description)
    title_key = normalise(title)[:120]
    existing = await db.news_items.find_one({
        "$or": [
            {"canonical_url": url},
            {"content_hash": digest},
            {"feed_guid": item["guid"] or "__none__", "source_name": source["name"]},
            {"title_key": title_key},
        ]
    })
    if existing:
        await db.news_items.update_one(
            {"_id": existing["_id"]},
            {"$set": {"fetched_at": now.isoformat(), "relevance_score": score,
                      "updated_at": now.isoformat()}})
        return "duplicates"

    image_url, image_credit = item["image"]
    summary_text, summary_origin = summarise.deterministic_summary(title, description, source["name"])
    display_title = title

    if summarise.is_configured() and ai_budget[0] > 0:
        ai_budget[0] -= 1
        ai = await summarise.gemini_summary(title, description, source["name"], published.date().isoformat())
        if ai:
            summary_text = ai["summary"]
            summary_origin = "gemini"
            if source["language"] != "en" and ai["translated_title"]:
                display_title = ai["translated_title"]
            if ai["category"]:
                category = ai["category"]

    slug = slugify(display_title, published)
    if await db.news_items.find_one({"slug": slug}):
        slug = f"{slug}-{digest[:6]}"

    doc = {
        "id": digest[:24],
        "slug": slug,
        "title": display_title,
        "original_title": title,
        "summary": summary_text,
        "summary_origin": summary_origin,
        "source_name": source["name"],
        "source_url": item["link"],
        "canonical_url": url,
        "source_language": source["language"],
        "category": category,
        "region": source["region"],
        "published_at": published.isoformat(),
        "fetched_at": now.isoformat(),
        "image_url": image_url,
        "image_credit": image_credit,
        "feed_guid": item["guid"],
        "content_hash": digest,
        "title_key": title_key,
        "relevance_score": score,
        "matched_terms": matched[:8],
        "status": "published",
        "is_featured": False,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }
    try:
        await db.news_items.insert_one(doc)
    except Exception as exc:  # unique index race
        logger.info("news: insert skipped (%s)", type(exc).__name__)
        return "duplicates"
    return "accepted"


async def run_ingestion(db) -> dict:
    """Ingest every enabled source. One failing source never stops the others."""
    await ensure_indexes(db)
    budget = [int(os.environ.get("NEWS_AI_MAX_REQUESTS_PER_RUN", "10"))]
    started = datetime.now(timezone.utc)
    results = await asyncio.gather(
        *(ingest_source(db, source, budget) for source in enabled_sources()),
        return_exceptions=True,
    )
    report = {"started_at": started.isoformat(), "sources": [], "accepted": 0, "duplicates": 0,
              "rejected": 0, "failed": 0}
    for item in results:
        if isinstance(item, Exception):
            report["failed"] += 1
            continue
        report["sources"].append(item)
        report["accepted"] += item.get("accepted", 0)
        report["duplicates"] += item.get("duplicates", 0)
        report["rejected"] += item.get("rejected", 0)
        if item.get("status") == "failed":
            report["failed"] += 1
    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    report["ai_requests_used"] = max(0, int(os.environ.get("NEWS_AI_MAX_REQUESTS_PER_RUN", "10")) - budget[0])
    await db.news_runs.insert_one(dict(report))
    report.pop("_id", None)
    await _refresh_featured(db)
    logger.info("news: ingestion finished accepted=%s duplicates=%s rejected=%s failed=%s",
                report["accepted"], report["duplicates"], report["rejected"], report["failed"])
    return report


async def _refresh_featured(db) -> None:
    """Mark the strongest recent item in each editorial area as featured."""
    await db.news_items.update_many({"is_featured": True}, {"$set": {"is_featured": False}})
    for categories in (["ART", "EXHIBITIONS", "GALLERIES_AND_MUSEUMS"],
                       ["ARCHITECTURE_AND_DESIGN", "CONSTRUCTION", "URBAN_TRANSFORMATION",
                        "KADIKOY", "TECHNICAL_AND_LEGAL"]):
        doc = await db.news_items.find_one(
            {"status": "published", "category": {"$in": categories}},
            sort=[("published_at", -1), ("relevance_score", -1)])
        if doc:
            await db.news_items.update_one({"_id": doc["_id"]}, {"$set": {"is_featured": True}})
