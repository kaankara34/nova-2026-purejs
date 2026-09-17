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
    "feed_guid": 0,
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


def _cache(response: Response, payload: dict) -> None:
    body = json.dumps(payload, sort_keys=True, default=str).encode()
    response.headers["ETag"] = hashlib.sha256(body).hexdigest()[:32]
    response.headers["Cache-Control"] = "public, max-age=300, stale-while-revalidate=600"


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
    """Latest published items with editorial balance: culture + built environment."""
    _rate_limit(request)
    db = get_db(request)
    culture = ["ART", "EXHIBITIONS", "GALLERIES_AND_MUSEUMS"]
    built = ["ARCHITECTURE_AND_DESIGN", "CONSTRUCTION", "URBAN_TRANSFORMATION",
             "KADIKOY", "TECHNICAL_AND_LEGAL"]

    async def newest(query, count):
        return await db.news_items.find({"status": "published", **query}, PUBLIC_FIELDS).sort(
            [("published_at", -1), ("relevance_score", -1)]).limit(count).to_list(length=count)

    picked: list[dict] = []
    seen_slugs: set[str] = set()
    per_source: dict[str, int] = {}
    per_category: dict[str, int] = {}

    def take(candidates, cap, cap_category=None):
        for doc in candidates:
            if len(picked) >= limit or cap <= 0:
                return
            if doc["slug"] in seen_slugs:
                continue
            if per_source.get(doc["source_name"], 0) >= 2:
                continue
            if cap_category and per_category.get(doc["category"], 0) >= cap_category:
                continue
            picked.append(doc)
            seen_slugs.add(doc["slug"])
            per_source[doc["source_name"]] = per_source.get(doc["source_name"], 0) + 1
            per_category[doc["category"]] = per_category.get(doc["category"], 0) + 1
            cap -= 1

    take(await newest({"category": "KADIKOY"}, 2), 1)
    take(await newest({"category": {"$in": culture}}, 10), 2, cap_category=2)
    take(await newest({"category": {"$in": built}}, 10), 2, cap_category=2)
    take(await newest({}, limit + 20), limit, cap_category=3)
    take(await newest({}, limit + 20), limit)

    payload = {"items": picked[:limit], "generated_at": datetime.now(timezone.utc).isoformat()}
    _cache(response, payload)
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
