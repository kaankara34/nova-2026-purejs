"""Read-only public newsroom API plus a protected manual refresh endpoint."""

import hashlib
import json
import logging
import os
import re
import time
from datetime import datetime, timezone

from fastapi import APIRouter, Header, HTTPException, Query, Request, Response

from .ingest import run_ingestion
from .sources import CATEGORIES

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

PUBLIC_FIELDS = {
    "_id": 0, "title_key": 0, "matched_terms": 0, "relevance_score": 0, "content_hash": 0,
    "feed_guid": 0, "image_source_url": 0,
}
_RATE: dict[str, list[float]] = {}
RATE_LIMIT = 120          # requests
RATE_WINDOW = 60.0        # seconds


def _rate_limit(request: Request) -> None:
    client = request.client.host if request.client else "unknown"
    now = time.time()
    hits = [t for t in _RATE.get(client, []) if now - t < RATE_WINDOW]
    hits.append(now)
    _RATE[client] = hits
    if len(hits) > RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too many requests")


def _cache(response: Response, payload: dict, max_age: int = 300, swr: int = 600) -> None:
    body = json.dumps(payload, sort_keys=True, default=str).encode()
    response.headers["ETag"] = hashlib.sha256(body).hexdigest()[:32]
    response.headers["Cache-Control"] = f"public, max-age={max_age}, stale-while-revalidate={swr}"


def get_db(request: Request):
    return request.app.state.db


@router.get("/news")
async def list_news(
    request: Request,
    response: Response,
    category: str | None = Query(None, max_length=40),
    page: int = Query(1, ge=1, le=200),
    limit: int = Query(12, ge=1, le=24),
    search: str | None = Query(None, max_length=80),
    language: str | None = Query(None, pattern="^(en|tr)$"),
):
    _rate_limit(request)
    db = get_db(request)
    query: dict = {"status": "published"}
    if category:
        category = category.upper()
        if category not in CATEGORIES:
            raise HTTPException(status_code=400, detail="Unknown category")
        query["category"] = category
    if language:
        query["source_language"] = language
    if search:
        needle = re.escape(search.strip())
        if needle:
            query["$or"] = [
                {"title": {"$regex": needle, "$options": "i"}},
                {"summary": {"$regex": needle, "$options": "i"}},
                {"source_name": {"$regex": needle, "$options": "i"}},
            ]
    total = await db.news_items.count_documents(query)
    cursor = db.news_items.find(query, PUBLIC_FIELDS).sort(
        [("published_at", -1), ("fetched_at", -1)]).skip((page - 1) * limit).limit(limit)
    items = await cursor.to_list(length=limit)
    payload = {
        "items": items,
        "pagination": {
            "page": page, "limit": limit, "total": total,
            "pages": (total + limit - 1) // limit if total else 0,
            "has_more": page * limit < total,
        },
        "category": category,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    _cache(response, payload)
    return payload


@router.get("/news/featured")
async def featured_news(request: Request, response: Response, limit: int = Query(6, ge=1, le=12)):
    """Serves the pre-computed, materialised selection. Never fetches upstream sources."""
    _rate_limit(request)
    db = get_db(request)
    doc = await db.news_featured.find_one({"key": "homepage"}, {"_id": 0})
    if not doc:
        items = await db.news_items.find({"status": "published"}, PUBLIC_FIELDS).sort(
            [("published_at", -1)]).limit(limit).to_list(length=limit)
        payload = {"items": items, "generated_at": datetime.now(timezone.utc).isoformat(),
                   "source": "fallback-query"}
    else:
        payload = {"items": doc.get("items", [])[:limit],
                   "generated_at": doc.get("generated_at"), "source": "materialised"}
    _cache(response, payload, max_age=300, swr=86400)
    return payload


@router.get("/news/{slug}")
async def news_detail(request: Request, response: Response, slug: str):
    _rate_limit(request)
    if not re.fullmatch(r"[a-z0-9-]{3,120}", slug):
        raise HTTPException(status_code=400, detail="Invalid slug")
    db = get_db(request)
    item = await db.news_items.find_one({"slug": slug, "status": "published"}, PUBLIC_FIELDS)
    if not item:
        raise HTTPException(status_code=404, detail="Article not found")
    related = await db.news_items.find(
        {"status": "published", "slug": {"$ne": slug},
         "$or": [{"category": item["category"]}, {"region": item["region"]}]},
        PUBLIC_FIELDS,
    ).sort([("published_at", -1)]).limit(3).to_list(length=3)
    payload = {"item": item, "related": related}
    _cache(response, payload)
    return payload


@router.post("/admin/news/refresh")
async def refresh_news(request: Request, x_admin_token: str | None = Header(None)):
    expected = os.environ.get("NEWS_ADMIN_TOKEN")
    if not expected:
        raise HTTPException(status_code=503, detail="Manual refresh is not configured")
    if not x_admin_token or x_admin_token != expected:
        raise HTTPException(status_code=401, detail="Unauthorised")
    report = await run_ingestion(get_db(request))
    report.pop("_id", None)
    return report


@router.get("/news-sources/status")
async def sources_status(request: Request):
    """Operational health only — never exposes credentials or feed configuration."""
    _rate_limit(request)
    db = get_db(request)
    docs = await db.news_sources.find({}, {"_id": 0, "name": 1, "language": 1,
                                           "last_success_at": 1, "enabled": 1}).to_list(length=50)
    published = await db.news_items.count_documents({"status": "published"})
    return {"sources": docs, "published_items": published}
