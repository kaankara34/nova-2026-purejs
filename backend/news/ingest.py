"""Server-side newsroom pipeline.

    scheduled refresh
      -> feeds + robots-permitted institutional listings
      -> sanitise, date-window, relevance, multi-category classification
      -> deduplicate
      -> source URL validation
      -> article extraction
      -> image validation and local derivatives
      -> excerpt
      -> optional Gemini long-form synthesis (background only) + quality gate
      -> MongoDB
      -> cached public API + homepage snapshot

Nothing in this module is called from a visitor request except the protected refresh
endpoint, which is lock-guarded and idempotent.
"""

import asyncio
import hashlib
import ipaddress
import json
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

from . import ai, crawl, editorial, extract, images, summarise
from .filters import BUILT_CATEGORIES, CULTURE_CATEGORIES, is_excluded, normalise, relevance_score
from .sources import (ALLOWED_HOSTS, CATEGORIES, CATEGORY_MIN_ITEMS, enabled_crawl_targets,
                      enabled_sources)
from .validate import normalise_editorial, validate_source_url

logger = logging.getLogger(__name__)

USER_AGENT = "NovaKonutNewsroomBot/1.0 (+https://nova.istanbul; newsroom aggregation)"
MAX_BYTES = 4 * 1024 * 1024
MAX_REDIRECTS = 3
FETCH_TIMEOUT = 20.0
MIN_SCORE = 8
EDITORIAL_TZ = "Europe/Istanbul"
TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "utm_id",
    "fbclid", "gclid", "mc_cid", "mc_eid", "igshid", "ref", "ref_src", "CMP", "cmp",
}
ATOM = "{http://www.w3.org/2005/Atom}"
MEDIA = "{http://search.yahoo.com/mrss/}"
CONTENT = "{http://purl.org/rss/1.0/modules/content/}"
DC = "{http://purl.org/dc/elements/1.1/}"

PUBLIC_PROJECTION = {"_id": 0, "title_key": 0, "matched_terms": 0, "relevance_score": 0,
                     "content_hash": 0, "feed_guid": 0, "image_source_url": 0,
                     "source_text": 0, "ai_error": 0, "attempt_count": 0}
SNAPSHOT_PATH = os.environ.get("NEWS_SNAPSHOT_PATH", "/app/frontend/data/news-featured.json")


def window_days() -> int:
    try:
        return max(1, int(os.environ.get("NEWS_WINDOW_DAYS") or 15))
    except ValueError:
        return 15


def window_cutoff() -> str:
    return (datetime.now(timezone.utc) - timedelta(days=window_days())).isoformat()


def publish_without_ai() -> bool:
    return (os.environ.get("NEWS_PUBLISH_WITHOUT_AI", "true").lower() == "true")


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
    """Fetch an allowlisted feed with conditional request support."""
    if not _host_allowed(url):
        raise ValueError("source host is not allowlisted")
    if not _public_ip(urlparse(url).hostname):
        raise ValueError("source host resolves to a non-public address")
    headers = {"User-Agent": USER_AGENT,
               "Accept": "application/rss+xml, application/atom+xml, application/xml;q=0.9"}
    if etag:
        headers["If-None-Match"] = etag
    if modified:
        headers["If-Modified-Since"] = modified
    async with httpx.AsyncClient(timeout=FETCH_TIMEOUT, follow_redirects=False) as http:
        current = url
        for _ in range(MAX_REDIRECTS + 1):
            res = await http.get(current, headers=headers)
            if res.status_code in (301, 302, 303, 307, 308):
                target = str(httpx.URL(current).join(res.headers.get("location", "")))
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
    return 200, res.content[:MAX_BYTES], dict(res.headers)


# ---------------------------------------------------------------- parsing
def _text(node) -> str:
    return (node.text or "").strip() if node is not None else ""


def _clean(html: str) -> str:
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
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.astimezone(timezone.utc) if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def canonical_url(url: str) -> str:
    parsed = urlparse((url or "").strip())
    if parsed.scheme not in ("http", "https"):
        return ""
    query = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=False)
             if k not in TRACKING_PARAMS]
    return urlunparse((parsed.scheme, parsed.netloc.lower(), parsed.path.rstrip("/") or "/",
                       "", urlencode(query), ""))


_IMG_SRC = re.compile(r"""<img[^>]+src=["\']([^"\']+)["\']""", re.IGNORECASE)


def _image_candidates(node, raw_description: str) -> tuple[list[str], str]:
    scored: list[tuple[int, str]] = []
    for media in list(node.findall(f"{MEDIA}content")) + list(node.findall(f"{MEDIA}thumbnail")):
        url = media.get("url", "")
        if not url.startswith("https://"):
            continue
        try:
            width = int(media.get("width") or 0)
        except ValueError:
            width = 0
        scored.append((width, url))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    candidates = [url for _, url in scored]

    enclosure = node.find("enclosure")
    if enclosure is not None and enclosure.get("type", "").startswith("image/"):
        url = enclosure.get("url", "")
        if url.startswith("https://"):
            candidates.append(url)

    for match in _IMG_SRC.findall(raw_description or ""):
        url = html_lib.unescape(match)
        if url.startswith("https://"):
            candidates.append(url)

    credit = _text(node.find(f"{MEDIA}credit")) or ""
    seen: set[str] = set()
    unique = [u for u in candidates if not (u in seen or seen.add(u))]
    return unique[:6], credit


def parse_items(body: bytes) -> list[dict]:
    """Parse RSS or Atom with entity expansion disabled."""
    body = body.lstrip(b"\xef\xbb\xbf").lstrip()
    root = DefusedET.fromstring(body, forbid_dtd=False, forbid_entities=True, forbid_external=True)
    items: list[dict] = []
    for node in root.iter("item"):
        raw_description = _text(node.find("description")) or _text(node.find(f"{CONTENT}encoded"))
        raw_content = _text(node.find(f"{CONTENT}encoded"))
        items.append({
            "title": _clean(_text(node.find("title"))),
            "link": _text(node.find("link")),
            "guid": _text(node.find("guid")) or _text(node.find(f"{DC}identifier")),
            "description": _clean(raw_description),
            "published": _text(node.find("pubDate")) or _text(node.find(f"{DC}date")),
            "image": _image_candidates(node, f"{raw_description} {raw_content}"),
        })
    for node in root.iter(f"{ATOM}entry"):
        link = ""
        for candidate in node.findall(f"{ATOM}link"):
            if candidate.get("rel", "alternate") == "alternate":
                link = candidate.get("href", "")
                break
        raw_description = _text(node.find(f"{ATOM}summary")) or _text(node.find(f"{ATOM}content"))
        items.append({
            "title": _clean(_text(node.find(f"{ATOM}title"))),
            "link": link,
            "guid": _text(node.find(f"{ATOM}id")),
            "description": _clean(raw_description),
            "published": _text(node.find(f"{ATOM}published")) or _text(node.find(f"{ATOM}updated")),
            "image": _image_candidates(node, raw_description),
        })
    return items


# ---------------------------------------------------------------- persistence helpers
def slugify(title: str, published: datetime) -> str:
    base = unicodedata.normalize("NFKD", title.lower())
    base = (base.replace("ı", "i").replace("ğ", "g").replace("ş", "s")
                .replace("ö", "o").replace("ü", "u").replace("ç", "c"))
    base = re.sub(r"[^\w\s-]", "", base.encode("ascii", "ignore").decode())
    base = re.sub(r"[\s_-]+", "-", base).strip("-")[:70] or "nova-journal-item"
    return f"{base}-{published.strftime('%Y%m%d')}"


def content_hash(title: str, description: str) -> str:
    return hashlib.sha256(f"{normalise(title)}|{normalise(description)}".encode()).hexdigest()


async def ensure_indexes(db) -> None:
    await db.news_items.create_index("slug", unique=True)
    await db.news_items.create_index("canonical_url", unique=True)
    await db.news_items.create_index([("published_at", -1)])
    await db.news_items.create_index([("status", 1), ("categories", 1), ("published_at", -1)])
    await db.news_items.create_index([("status", 1), ("published_at", -1)])
    await db.news_items.create_index("content_hash")
    await db.news_items.create_index("title_key")
    await db.news_sources.create_index("key", unique=True)


# ---------------------------------------------------------------- distributed lock
async def acquire_lock(db, key: str = "news-refresh", ttl_minutes: int = 45) -> bool:
    now = datetime.now(timezone.utc)
    expires = (now + timedelta(minutes=ttl_minutes)).isoformat()
    result = await db.news_locks.update_one(
        {"_id": key, "$or": [{"expires_at": {"$lt": now.isoformat()}}, {"expires_at": None}]},
        {"$set": {"expires_at": expires, "acquired_at": now.isoformat()}},
        upsert=False)
    if result.modified_count:
        return True
    try:
        await db.news_locks.insert_one({"_id": key, "expires_at": expires,
                                        "acquired_at": now.isoformat()})
        return True
    except Exception:
        return False


async def release_lock(db, key: str = "news-refresh") -> None:
    await db.news_locks.update_one({"_id": key}, {"$set": {"expires_at": None}})


# ---------------------------------------------------------------- ingestion
async def ingest_source(db, source: dict, stats: dict) -> dict:
    state = await db.news_sources.find_one({"key": source["key"]}) or {}
    result = {"source": source["key"], "name": source["name"], "fetched": 0, "accepted": 0,
              "duplicates": 0, "rejected": 0, "status": "ok"}
    try:
        status, body, headers = await fetch_feed(source["url"], state.get("etag"),
                                                state.get("last_modified"))
    except Exception as exc:
        logger.warning("news: fetch failed for %s: %s", source["key"], exc)
        await _save_source_state(db, source, error=str(exc)[:200])
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
            outcome = await _store_item(db, source, item, now, stats)
            result[outcome] = result.get(outcome, 0) + 1
    await _save_source_state(db, source, headers=headers)
    return result


async def crawl_source(db, target: dict, stats: dict) -> dict:
    result = {"source": target["key"], "name": target["name"], "fetched": 0, "accepted": 0,
              "duplicates": 0, "rejected": 0, "status": "ok"}
    try:
        items = await crawl.crawl_target(target)
    except Exception as exc:
        logger.warning("news: crawl failed for %s: %s", target["key"], exc)
        await _save_source_state(db, target, error=str(exc)[:200])
        result["status"] = "failed"
        return result
    if not items:
        result["status"] = "empty"
    result["fetched"] = len(items)
    now = datetime.now(timezone.utc)
    for item in items:
        outcome = await _store_item(db, target, item, now, stats)
        result[outcome] = result.get(outcome, 0) + 1
    await _save_source_state(db, target)
    return result


async def _save_source_state(db, source: dict, headers: dict | None = None,
                             error: str | None = None) -> None:
    now = datetime.now(timezone.utc).isoformat()
    payload = {"key": source["key"], "name": source["name"],
               "url": source.get("url") or (source.get("list_urls") or [""])[0],
               "language": source["language"], "enabled": True,
               "last_error": error, "last_attempt_at": now}
    if error is None:
        payload["last_success_at"] = now
        if headers:
            payload["etag"] = headers.get("etag")
            payload["last_modified"] = headers.get("last-modified")
    await db.news_sources.update_one({"key": source["key"]}, {"$set": payload}, upsert=True)


async def _store_item(db, source: dict, item: dict, now: datetime, stats: dict) -> str:
    title = item["title"]
    description = item["description"]
    url = canonical_url(item["link"])
    if not title or not url:
        stats["rejected_malformed"] += 1
        return "rejected"

    published = _parse_date(item["published"])
    if published is None:
        stats["rejected_no_date"] += 1
        return "rejected"
    if published > now + timedelta(hours=6):
        stats["rejected_future"] += 1
        return "rejected"
    age_days = max((now - published).total_seconds() / 86400.0, 0.0)
    if age_days > window_days():
        stats["rejected_date"] += 1
        return "rejected"

    if is_excluded(title, description):
        stats["rejected_irrelevant"] += 1
        return "rejected"

    title = normalise_editorial(title)
    description = normalise_editorial(description)
    score, primary, categories, matched = relevance_score(title, description, source, age_days)
    if score < MIN_SCORE or not matched:
        stats["rejected_irrelevant"] += 1
        return "rejected"

    digest = content_hash(title, description)
    title_key = normalise(title)[:120]
    existing = await db.news_items.find_one({
        "$or": [
            {"canonical_url": url},
            {"content_hash": digest},
            {"feed_guid": item["guid"] or "__none__", "source_name": source["name"]},
            {"title_key": title_key},
        ]})
    if existing:
        await db.news_items.update_one(
            {"_id": existing["_id"]},
            {"$set": {"fetched_at": now.isoformat(), "relevance_score": score,
                      "updated_at": now.isoformat()}})
        stats["duplicates"] += 1
        return "duplicates"

    ok, resolved = await validate_source_url(item["link"] or url)
    if not ok:
        stats["rejected_source"] += 1
        return "rejected"
    url = canonical_url(resolved) or url

    article = item.get("extracted") or await extract.extract_article(url)
    source_text = ""
    if article.get("ok") and not article.get("paywalled"):
        source_text = article.get("text") or ""
    if article.get("ok") and article.get("canonical"):
        canonical_candidate = canonical_url(article["canonical"])
        if canonical_candidate and urlparse(canonical_candidate).hostname == urlparse(url).hostname:
            url = canonical_candidate

    image_candidates, image_credit = item["image"]
    ordered = [{"url": u, "type": "feed"} for u in image_candidates]
    for key, kind in (("json_ld_image", "json_ld"), ("og_image", "open_graph"),
                      ("twitter_image", "twitter")):
        url_candidate = article.get(key)
        if url_candidate:
            ordered.append({"url": url_candidate, "type": kind})
    seen_images: set[str] = set()
    ordered = [c for c in ordered if not (c["url"] in seen_images or seen_images.add(c["url"]))]
    image_fields = await images.pick_image(ordered, primary, url, [0])
    if image_credit and image_fields["image_kind"] == "cached":
        image_fields["image_credit"] = image_credit
    if image_fields["image_kind"] != "cached":
        stats["image_fallback"] += 1

    verdict = editorial.assess(title, description, source_text, primary, categories, source)
    if verdict["status"] == "irrelevant":
        stats["rejected_irrelevant"] += 1
        logger.info("news: rejected as irrelevant (%s) %s", verdict["reason"], title[:70])
        return "rejected"
    if verdict["status"] == "brand_unsafe_negative":
        stats["rejected_brand"] = stats.get("rejected_brand", 0) + 1
        logger.info("news: rejected on editorial policy (%s) %s", verdict["reason"], title[:70])
        return "rejected"
    categories = verdict.get("categories") or categories
    primary = verdict.get("primary") or (categories[0] if categories else primary)

    excerpt = summarise.build_excerpt(source_text, description, article.get("description") or "")
    summary_text, summary_origin = summarise.deterministic_summary(
        title, source_text or description, source["name"])
    if not excerpt:
        excerpt = summarise.build_excerpt(summary_text) or summary_text

    slug = slugify(title, published)
    if await db.news_items.find_one({"slug": slug}):
        slug = f"{slug}-{digest[:6]}"

    # Publication gate: an item is only publishable when the verified source material can
    # carry a NOVA article and a well-formed excerpt. Thin items stay out of public lists.
    ai_ready = len(source_text.split()) >= ai.MIN_SOURCE_WORDS
    excerpt_ok = (len(excerpt.split()) >= 35 and not re.search(r"[a-zçğıöşü][A-ZÇĞİÖŞÜ]", excerpt)
                  and excerpt.rstrip().endswith((".", "!", "?", "…", "”", '"')))
    if verdict["status"] == "needs_review":
        status = "needs_review"
        stats["needs_review"] = stats.get("needs_review", 0) + 1
    elif not ai_ready or not excerpt_ok:
        status = "insufficient_source"
        stats["rejected_thin"] = stats.get("rejected_thin", 0) + 1
    elif ai.is_enabled():
        status = "pending_editorial"
    elif publish_without_ai():
        status = "published"
    else:
        status = "pending_editorial"

    doc = {
        "id": digest[:24],
        "slug": slug,
        "title": title,
        "original_title": title,
        "standfirst": "",
        "excerpt": normalise_editorial(excerpt),
        "summary": normalise_editorial(summary_text),
        "summary_origin": summary_origin,
        "body": "",
        "body_sections": [],
        "body_word_count": 0,
        "synthesis_state": "pending" if status == "pending_editorial" else (
            "unavailable" if not ai.is_enabled() else "pending"),
        "publisher": source["name"],
        "source_name": source["name"],
        "source_url": item["link"],
        "canonical_url": url,
        "source_language": source["language"],
        "language": source["language"],
        "category": primary,
        "categories": categories,
        "region": source["region"],
        "published_at": published.isoformat(),
        "fetched_at": now.isoformat(),
        "ingested_at": now.isoformat(),
        "image_url": image_fields["image_card"],
        "image_source_url": image_fields.get("image_origin", ""),
        "image_credit": image_fields.get("image_credit") or (
            source["name"] if image_fields["image_kind"] == "cached" else ""),
        "image_kind": image_fields["image_kind"],
        "image_source_type": image_fields.get("image_source_type", "nova_fallback"),
        "image_width": image_fields["image_card_width"],
        "image_height": image_fields["image_card_height"],
        "editorial_tone": verdict.get("tone", "neutral_technical"),
        "brand_safety_status": "cleared" if verdict["status"] == "ok" else verdict["status"],
        "brand_safety_reason": verdict.get("reason", ""),
        "source_urls": [url],
        "image_card": image_fields["image_card"],
        "image_detail": image_fields["image_detail"],
        "image_card_width": image_fields["image_card_width"],
        "image_card_height": image_fields["image_card_height"],
        "image_detail_width": image_fields["image_detail_width"],
        "image_detail_height": image_fields["image_detail_height"],
        "image_validated_at": now.isoformat(),
        "feed_guid": item["guid"],
        "content_hash": digest,
        "content_fingerprint": digest,
        "title_key": title_key,
        "relevance_score": score,
        "matched_terms": matched[:8],
        "source_text": source_text[:40000],
        "source_word_count": len(source_text.split()),
        "status": status,
        "is_featured": False,
        "source_checked_at": now.isoformat(),
        "source_validated_at": now.isoformat(),
        "attempt_count": 0,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }
    try:
        await db.news_items.insert_one(doc)
    except Exception as exc:  # unique index race
        logger.info("news: insert skipped (%s)", type(exc).__name__)
        stats["duplicates"] += 1
        return "duplicates"
    stats["accepted"] += 1
    return "accepted"


# ---------------------------------------------------------------- synthesis pass
def _coverage_priority(counts: dict[str, int]) -> list[str]:
    return sorted(CATEGORIES, key=lambda c: counts.get(c, 0))


async def category_counts(db, status: str = "published") -> dict[str, int]:
    cutoff = window_cutoff()
    pipeline = [
        {"$match": {"status": status, "published_at": {"$gte": cutoff}}},
        {"$unwind": "$categories"},
        {"$group": {"_id": "$categories", "n": {"$sum": 1}}},
    ]
    counts = {category: 0 for category in CATEGORIES}
    async for row in db.news_items.aggregate(pipeline):
        if row["_id"] in counts:
            counts[row["_id"]] = row["n"]
    return counts


_STOPWORDS = {"the", "and", "for", "with", "from", "that", "this", "ile", "için", "olarak",
              "sonra", "daha", "üzerine", "ilişkin", "hakkında", "yeni", "büyük"}


async def enrich_sources(db, doc: dict) -> dict:
    """Add verified material from other stored reports of the same event.

    Only records that share several significant headline tokens, fall within three days
    of the same date and come from a different publisher are used. Nothing is invented and
    every contributing URL is stored.
    """
    text = doc.get("source_text") or ""
    urls = list(doc.get("source_urls") or [doc.get("canonical_url")])
    if len(text.split()) >= 400:
        return {"source_text": text, "source_urls": urls, "contributors": []}
    tokens = {t for t in normalise(doc.get("title", "")).split()
              if len(t) > 4 and t not in _STOPWORDS}
    if len(tokens) < 3:
        return {"source_text": text, "source_urls": urls, "contributors": []}
    published = doc.get("published_at", "")
    window_start = (datetime.fromisoformat(published) - timedelta(days=3)).isoformat()
    window_end = (datetime.fromisoformat(published) + timedelta(days=3)).isoformat()
    candidates = await db.news_items.find(
        {"slug": {"$ne": doc["slug"]},
         "source_name": {"$ne": doc.get("source_name")},
         "published_at": {"$gte": window_start, "$lte": window_end},
         "source_word_count": {"$gte": 80}},
        {"title": 1, "source_text": 1, "canonical_url": 1, "source_name": 1}
    ).limit(60).to_list(length=60)
    contributors = []
    for candidate in candidates:
        other = {t for t in normalise(candidate.get("title", "")).split()
                 if len(t) > 4 and t not in _STOPWORDS}
        if len(tokens & other) < 3:
            continue
        extra = candidate.get("source_text") or ""
        if len(extra.split()) < 80:
            continue
        text = f"{text}\n\n[Additional verified report — {candidate['source_name']}]\n{extra}"
        urls.append(candidate["canonical_url"])
        contributors.append(candidate["source_name"])
        if len(contributors) >= 2:
            break
    return {"source_text": text[:40000], "source_urls": urls, "contributors": contributors}


async def run_synthesis(db, max_items: int | None = None) -> dict:
    """Generate the long-form NOVA synthesis for pending articles (background only)."""
    report = {"attempted": 0, "published": 0, "quality_failed": 0, "deferred": 0,
              "insufficient": 0, "enabled": ai.is_enabled(), "errors": {}}
    if not ai.is_enabled():
        report["skipped"] = "gemini-not-configured"
        return report
    ok, model_state = await ai.check_model()
    report["model_state"] = model_state
    if not ok:
        logger.error("news: Gemini model unavailable (%s) — synthesis skipped", model_state)
        return report

    budget = max_items or int(os.environ.get("NEWS_SYNTHESIS_PER_RUN", "40"))
    counts = await category_counts(db)
    priority = _coverage_priority(counts)
    now_iso = datetime.now(timezone.utc).isoformat()

    for category in priority + [None]:
        while budget > 0:
            available, reason = await ai.budget_available(db)
            if not available:
                report["errors"][reason] = report["errors"].get(reason, 0) + 1
                return report
            query = {
                "status": "pending_editorial",
                "published_at": {"$gte": window_cutoff()},
                "source_word_count": {"$gte": ai.MIN_SOURCE_WORDS},
                "$or": [{"next_retry_at": {"$exists": False}}, {"next_retry_at": {"$lte": now_iso}}],
            }
            if category:
                query["categories"] = category
            doc = await db.news_items.find_one_and_update(
                query,
                {"$set": {"status": "generating", "synthesis_state": "generating",
                          "lease_until": (datetime.now(timezone.utc) +
                                          timedelta(minutes=10)).isoformat(),
                          "last_attempt_at": now_iso},
                 "$inc": {"attempt_count": 1}},
                sort=[("relevance_score", -1), ("published_at", -1)])
            if not doc:
                break
            budget -= 1
            report["attempted"] += 1
            enriched = await enrich_sources(db, doc)
            doc = {**doc, "source_text": enriched["source_text"]}
            result, error = await ai.synthesise(db, doc)
            if result:
                merged = list(dict.fromkeys(list(doc.get("categories", [])) +
                                            [c for c in result["categories"]
                                             if c in doc.get("categories", [])]))
                await db.news_items.update_one({"_id": doc["_id"]}, {"$set": {
                    "status": "published",
                    "synthesis_state": "generated",
                    "standfirst": result["standfirst"],
                    "body_sections": result["sections"],
                    "body": result["body"],
                    "body_word_count": result["word_count"],
                    "summary": result["standfirst"],
                    "excerpt": doc.get("excerpt") or summarise.build_excerpt(result["body"]),
                    "categories": merged or doc.get("categories", []),
                    "synthesis_model": result["model"],
                    "source_urls": enriched["source_urls"],
                    "contributing_sources": enriched["contributors"],
                    "rejection_reason": None,
                    "synthesis_at": datetime.now(timezone.utc).isoformat(),
                    "ai_error": None,
                    "lease_until": None,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }})
                report["published"] += 1
                continue

            report["errors"][error] = report["errors"].get(error, 0) + 1
            if error.startswith("quality:"):
                new_status, state, retry = "quality_failed", "quality_failed", None
                report["quality_failed"] += 1
            elif error == "source-insufficient":
                new_status, state, retry = "insufficient_source", "insufficient_source", None
                report["insufficient"] += 1
            else:
                new_status, state = "pending_editorial", "pending"
                retry = (datetime.now(timezone.utc) + timedelta(hours=6)).isoformat()
                report["deferred"] += 1
            update = {"status": new_status, "synthesis_state": state, "ai_error": error,
                      "lease_until": None,
                      "updated_at": datetime.now(timezone.utc).isoformat()}
            if retry:
                update["next_retry_at"] = retry
            await db.news_items.update_one({"_id": doc["_id"]}, {"$set": update})
            if error in ("quota-exhausted", "invalid-or-revoked-key", "model-not-found",
                         "daily-request-limit", "daily-input-token-limit",
                         "daily-output-token-limit"):
                return report
    return report


async def reclaim_leases(db) -> int:
    """Return abandoned 'generating' articles to the pending queue after a worker restart."""
    now = datetime.now(timezone.utc).isoformat()
    result = await db.news_items.update_many(
        {"status": "generating", "$or": [{"lease_until": None},
                                         {"lease_until": {"$lt": now}}]},
        {"$set": {"status": "pending_editorial", "synthesis_state": "pending",
                  "lease_until": None, "updated_at": now}})
    return result.modified_count


async def expire_old(db) -> int:
    """Public lists only ever show the rolling window; older records become 'expired'."""
    result = await db.news_items.update_many(
        {"status": {"$in": ["published", "pending_editorial", "generating", "quality_failed"]},
         "published_at": {"$lt": window_cutoff()}},
        {"$set": {"status": "expired", "synthesis_state": "expired",
                  "updated_at": datetime.now(timezone.utc).isoformat()}})
    return result.modified_count


async def revalidate_sources(db, batch: int = 40, max_age_hours: int = 24) -> dict:
    """Re-check published source links daily; unpublish dead links, restore recovered ones."""
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=max_age_hours)).isoformat()
    docs = await db.news_items.find(
        {"status": {"$in": ["published", "source_invalid"]},
         "published_at": {"$gte": window_cutoff()},
         "$or": [{"source_checked_at": {"$exists": False}},
                 {"source_checked_at": {"$lt": cutoff}}]},
        {"slug": 1, "canonical_url": 1, "status": 1, "body_word_count": 1}
    ).limit(batch).to_list(length=batch)
    checked = unpublished = restored = 0
    for doc in docs:
        ok, resolved = await validate_source_url(doc["canonical_url"])
        checked += 1
        now = datetime.now(timezone.utc).isoformat()
        if ok:
            update = {"source_checked_at": now, "source_validated_at": now,
                      "canonical_url": canonical_url(resolved) or doc["canonical_url"]}
            if doc["status"] == "source_invalid":
                update["status"] = "published"
                update["unpublished_reason"] = None
                restored += 1
            await db.news_items.update_one({"_id": doc["_id"]}, {"$set": update})
        elif doc["status"] == "published":
            unpublished += 1
            await db.news_items.update_one({"_id": doc["_id"]}, {"$set": {
                "status": "source_invalid", "source_checked_at": now,
                "unpublished_reason": "source-unreachable"}})
    if checked:
        logger.info("news: revalidated %s source links (unpublished %s, restored %s)",
                    checked, unpublished, restored)
    return {"checked": checked, "unpublished": unpublished, "restored": restored}


# ---------------------------------------------------------------- featured selection
CULTURE = sorted(CULTURE_CATEGORIES)
BUILT = sorted(BUILT_CATEGORIES)
HOMEPAGE_QUOTA = [
    ("KADIKOY", 1),
    ("URBAN_TRANSFORMATION", 1),
    ("CONSTRUCTION", 1),
    ("TECHNICAL_AND_LEGAL", 1),
    ("ARCHITECTURE_AND_DESIGN", 1),
]


async def build_featured(db, limit: int = 6) -> list[dict]:
    """Balanced homepage selection: Kadıköy, urban, construction/technical, architecture, culture."""
    cutoff = window_cutoff()

    async def newest(query, count):
        return await db.news_items.find(
            {"status": "published", "published_at": {"$gte": cutoff}, **query},
            PUBLIC_PROJECTION
        ).sort([("published_at", -1), ("relevance_score", -1)]).limit(count).to_list(length=count)

    picked: list[dict] = []
    slugs: set[str] = set()
    per_source: dict[str, int] = {}
    per_category: dict[str, int] = {}

    def take(candidates, cap, cap_category=None):
        nonlocal picked
        for doc in candidates:
            if len(picked) >= limit or cap <= 0:
                return
            if doc["slug"] in slugs or per_source.get(doc["source_name"], 0) >= 2:
                continue
            if cap_category and per_category.get(doc["category"], 0) >= cap_category:
                continue
            picked.append(doc)
            slugs.add(doc["slug"])
            per_source[doc["source_name"]] = per_source.get(doc["source_name"], 0) + 1
            per_category[doc["category"]] = per_category.get(doc["category"], 0) + 1
            cap -= 1

    for category, quota in HOMEPAGE_QUOTA:
        take(await newest({"categories": category}, 4), quota, cap_category=2)
        if len(picked) >= limit - 2:
            break
    take(await newest({"categories": {"$in": CULTURE}}, 12), 2, cap_category=2)
    take(await newest({"categories": {"$in": BUILT}}, 14), 2, cap_category=2)
    take(await newest({}, limit + 24), limit, cap_category=2)
    take(await newest({}, limit + 24), limit)
    return picked[:limit]


async def _refresh_featured(db) -> None:
    items = await build_featured(db)
    generated_at = datetime.now(timezone.utc).isoformat()
    await db.news_featured.update_one(
        {"key": "homepage"},
        {"$set": {"key": "homepage", "items": items, "generated_at": generated_at}},
        upsert=True)
    await db.news_items.update_many({"is_featured": True}, {"$set": {"is_featured": False}})
    if items:
        await db.news_items.update_many({"slug": {"$in": [i["slug"] for i in items[:2]]}},
                                        {"$set": {"is_featured": True}})
    try:
        os.makedirs(os.path.dirname(SNAPSHOT_PATH), exist_ok=True)
        with open(SNAPSHOT_PATH, "w", encoding="utf-8") as handle:
            json.dump({"generated_at": generated_at, "items": items}, handle,
                      ensure_ascii=False, indent=1)
    except OSError as exc:
        logger.warning("news: could not write homepage snapshot: %s", exc)


# ---------------------------------------------------------------- orchestration
async def reprocess_active(db, image_batch: int = 60) -> dict:
    """Re-apply the current editorial, image and body rules to every active record.

    Records that no longer qualify are unpublished with a stored reason rather than
    deleted, so the decision stays auditable.
    """
    report = {"checked": 0, "irrelevant": 0, "brand_unsafe": 0, "short_body": 0,
              "recategorised": 0, "images_upgraded": 0, "needs_review": 0}
    min_words = ai.limits()["min_body_words"]
    cutoff = window_cutoff()
    cursor = db.news_items.find(
        {"status": {"$in": ["published", "needs_review", "pending_editorial",
                            "quality_failed", "insufficient_source", "rejected"]},
         "published_at": {"$gte": cutoff}})
    image_budget = image_batch
    async for doc in cursor:
        report["checked"] += 1
        now = datetime.now(timezone.utc).isoformat()
        categories = doc.get("categories") or [doc.get("category")]
        source = {"default_category": doc.get("category") or "ART",
                  "weight": 1, "region": doc.get("region", "TR"),
                  "language": doc.get("source_language", "tr"), "name": doc.get("source_name", "")}
        verdict = editorial.assess(doc.get("title", ""), doc.get("excerpt", ""),
                                   doc.get("source_text", "") or doc.get("summary", ""),
                                   doc.get("category") or categories[0], categories, source)
        update = {"editorial_tone": verdict.get("tone"),
                  "brand_safety_status": "cleared" if verdict["status"] == "ok" else verdict["status"],
                  "brand_safety_reason": verdict.get("reason", ""),
                  "updated_at": now}

        if verdict["status"] == "irrelevant":
            report["irrelevant"] += 1
            update.update({"status": "rejected", "rejection_reason": "irrelevant_subject"})
            await db.news_items.update_one({"_id": doc["_id"]}, {"$set": update})
            continue
        if verdict["status"] == "brand_unsafe_negative":
            report["brand_unsafe"] += 1
            update.update({"status": "rejected", "rejection_reason": "brand_unsafe_negative"})
            await db.news_items.update_one({"_id": doc["_id"]}, {"$set": update})
            continue
        if verdict["status"] == "needs_review":
            report["needs_review"] += 1
            update["status"] = "needs_review"
        elif doc["status"] in ("rejected", "needs_review"):
            # Previously excluded by an older rule but cleared by the current one.
            report["restored"] = report.get("restored", 0) + 1
            update.update({"status": "pending_editorial", "synthesis_state": "pending",
                           "rejection_reason": None})

        new_categories = verdict.get("categories") or categories
        if new_categories != categories:
            report["recategorised"] += 1
            update["categories"] = new_categories
            update["category"] = verdict.get("primary") or new_categories[0]

        # Authentic source imagery takes precedence over a NOVA category cover.
        if doc.get("image_kind") != "cached" and image_budget > 0:
            image_budget -= 1
            article = await extract.extract_article(doc.get("canonical_url", ""))
            ordered = []
            for key, kind in (("json_ld_image", "json_ld"), ("og_image", "open_graph"),
                              ("twitter_image", "twitter")):
                if article.get(key):
                    ordered.append({"url": article[key], "type": kind})
            if ordered:
                fields = await images.pick_image(ordered, update.get("category") or doc["category"],
                                                 doc.get("canonical_url", ""), [0])
                if fields["image_kind"] == "cached":
                    report["images_upgraded"] += 1
                    update.update({
                        "image_kind": "cached",
                        "image_source_type": fields.get("image_source_type", "open_graph"),
                        "image_card": fields["image_card"], "image_detail": fields["image_detail"],
                        "image_url": fields["image_card"],
                        "image_card_width": fields["image_card_width"],
                        "image_card_height": fields["image_card_height"],
                        "image_detail_width": fields["image_detail_width"],
                        "image_detail_height": fields["image_detail_height"],
                        "image_width": fields["image_card_width"],
                        "image_height": fields["image_card_height"],
                        "image_credit": doc.get("source_name", ""),
                        "image_source_url": fields.get("image_origin", ""),
                        "image_validated_at": now})
            if article.get("ok") and article.get("text") and not doc.get("source_text"):
                update["source_text"] = article["text"][:40000]
                update["source_word_count"] = article["word_count"]

        # A detail page is never published with a body below the editorial minimum.
        body_words = len((doc.get("body") or "").split())
        if update.get("status", doc["status"]) == "published" and body_words < min_words:
            report["short_body"] += 1
            update.update({"status": "pending_editorial", "synthesis_state": "pending",
                           "rejection_reason": "short_body"})
        await db.news_items.update_one({"_id": doc["_id"]}, {"$set": update})
    logger.info("news: reprocess %s", report)
    return report


def _empty_stats() -> dict:
    return {"accepted": 0, "duplicates": 0, "rejected_date": 0, "rejected_future": 0,
            "rejected_no_date": 0, "rejected_source": 0, "rejected_irrelevant": 0,
            "rejected_malformed": 0, "rejected_thin": 0, "rejected_brand": 0,
            "needs_review": 0, "image_fallback": 0}


async def _gather_limited(tasks: list, limit: int = 6) -> list:
    """Run source tasks with bounded concurrency so no publisher sees a burst."""
    semaphore = asyncio.Semaphore(limit)

    async def run(coro):
        async with semaphore:
            return await coro

    return await asyncio.gather(*(run(task) for task in tasks), return_exceptions=True)


async def run_ingestion(db, with_synthesis: bool = True) -> dict:
    """One complete refresh cycle. Lock-guarded; one failing source never stops the rest."""
    if not await acquire_lock(db):
        logger.info("news: refresh already running — skipped")
        return {"skipped": "locked"}
    started = datetime.now(timezone.utc)
    stats = _empty_stats()
    try:
        await ensure_indexes(db)
        expired = await expire_old(db)
        reclaimed = await reclaim_leases(db)

        results = await _gather_limited(
            [ingest_source(db, source, stats) for source in enabled_sources()] +
            [crawl_source(db, target, stats) for target in enabled_crawl_targets()])

        report = {"started_at": started.isoformat(), "sources": [], "accepted": 0,
                  "duplicates": 0, "rejected": 0, "failed": 0, "expired": expired,
                  "reclaimed": reclaimed, "window_days": window_days(),
                  "editorial_timezone": EDITORIAL_TZ}
        for item in results:
            if isinstance(item, Exception):
                report["failed"] += 1
                logger.warning("news: source task raised %s", type(item).__name__)
                continue
            report["sources"].append(item)
            report["accepted"] += item.get("accepted", 0)
            report["duplicates"] += item.get("duplicates", 0)
            report["rejected"] += item.get("rejected", 0)
            if item.get("status") == "failed":
                report["failed"] += 1

        report["sources_checked"] = len(report["sources"])
        report["rejections"] = {k: v for k, v in stats.items() if k.startswith("rejected")}
        report["image_fallbacks"] = stats["image_fallback"]
        report["revalidation"] = await revalidate_sources(db)
        report["reprocess"] = await reprocess_active(db)
        report["synthesis"] = await run_synthesis(db) if with_synthesis else {"skipped": "disabled"}
        await _refresh_featured(db)

        counts = await category_counts(db)
        report["category_counts"] = counts
        report["categories_below_target"] = [c for c, n in counts.items()
                                             if n < CATEGORY_MIN_ITEMS]
        report["published_total"] = await db.news_items.count_documents(
            {"status": "published", "published_at": {"$gte": window_cutoff()}})
        report["ai_usage"] = await ai.usage_today(db)
        report["finished_at"] = datetime.now(timezone.utc).isoformat()
        await db.news_runs.insert_one(dict(report))
        report.pop("_id", None)
        await db.news_health.update_one({"_id": "latest"}, {"$set": report}, upsert=True)
        logger.info("news: refresh done accepted=%s dup=%s rejected=%s failed=%s published=%s "
                    "below_target=%s", report["accepted"], report["duplicates"],
                    report["rejected"], report["failed"], report["published_total"],
                    report["categories_below_target"])
        return report
    finally:
        await release_lock(db)


run_refresh = run_ingestion
