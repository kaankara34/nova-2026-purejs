"""Read-only public newsroom API plus protected refresh and health endpoints.

Public endpoints only ever return published records inside the rolling editorial window,
with a validated source URL and a validated image. The window is enforced here, in the
database query — never only in the browser.
"""

import hashlib
import json
import logging
import os
import re
import time
from datetime import datetime, timezone

from fastapi import APIRouter, Header, HTTPException, Query, Request, Response

from . import ai
from .ingest import (PUBLIC_PROJECTION, category_counts, run_ingestion, run_synthesis,
                     window_cutoff, window_days)
from .sources import CATEGORIES, CATEGORY_MIN_ITEMS, DISABLED_SOURCES

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

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


def _require_admin(token: str | None) -> None:
    expected = os.environ.get("NEWS_ADMIN_TOKEN")
    if not expected:
        raise HTTPException(status_code=503, detail="Administrative access is not configured")
    if not token or token != expected:
        raise HTTPException(status_code=401, detail="Unauthorised")


def _public_query() -> dict:
    return {"status": "published", "published_at": {"$gte": window_cutoff()}}


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
    query: dict = _public_query()
    if category:
        category = category.upper()
        if category not in CATEGORIES:
            raise HTTPException(status_code=400, detail="Unknown category")
        query["categories"] = category
    if language:
        query["source_language"] = language
    if search:
        needle = re.escape(search.strip())
        if needle:
            query["$or"] = [
                {"title": {"$regex": needle, "$options": "i"}},
                {"excerpt": {"$regex": needle, "$options": "i"}},
                {"summary": {"$regex": needle, "$options": "i"}},
                {"source_name": {"$regex": needle, "$options": "i"}},
            ]
    total = await db.news_items.count_documents(query)
    cursor = db.news_items.find(query, PUBLIC_PROJECTION).sort(
        [("published_at", -1), ("id", -1)]).skip((page - 1) * limit).limit(limit)
    items = await cursor.to_list(length=limit)
    payload = {
        "items": items,
        "pagination": {
            "page": page, "limit": limit, "total": total,
            "pages": (total + limit - 1) // limit if total else 0,
            "has_more": page * limit < total,
        },
        "category": category,
        "window_days": window_days(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    _cache(response, payload)
    return payload


@router.get("/news/categories")
async def news_categories(request: Request, response: Response):
    """Public per-category counts for the current window (used for empty-state accuracy)."""
    _rate_limit(request)
    counts = await category_counts(get_db(request))
    payload = {"counts": counts, "window_days": window_days(),
               "generated_at": datetime.now(timezone.utc).isoformat()}
    _cache(response, payload)
    return payload


@router.get("/news/featured")
async def featured_news(request: Request, response: Response, limit: int = Query(6, ge=1, le=12)):
    """Serves the pre-computed, materialised selection. Never fetches upstream sources."""
    _rate_limit(request)
    db = get_db(request)
    cutoff = window_cutoff()
    doc = await db.news_featured.find_one({"key": "homepage"}, {"_id": 0})
    items = [i for i in (doc or {}).get("items", []) if (i.get("published_at") or "") >= cutoff]
    if len(items) < limit:
        fresh = await db.news_items.find(_public_query(), PUBLIC_PROJECTION).sort(
            [("published_at", -1)]).limit(limit * 3).to_list(length=limit * 3)
        seen = {i["slug"] for i in items}
        for item in fresh:
            if item["slug"] not in seen and len(items) < limit:
                items.append(item)
                seen.add(item["slug"])
    payload = {"items": items[:limit],
               "generated_at": (doc or {}).get("generated_at"),
               "source": "materialised" if doc else "query"}
    _cache(response, payload, max_age=300, swr=86400)
    return payload


@router.get("/news/{slug}")
async def news_detail(request: Request, response: Response, slug: str):
    _rate_limit(request)
    if not re.fullmatch(r"[a-z0-9-]{3,120}", slug):
        raise HTTPException(status_code=400, detail="Invalid slug")
    db = get_db(request)
    item = await db.news_items.find_one({"slug": slug, **_public_query()}, PUBLIC_PROJECTION)
    if not item:
        raise HTTPException(status_code=404, detail="Article not found")
    related = await db.news_items.find(
        {**_public_query(), "slug": {"$ne": slug},
         "$or": [{"categories": {"$in": item.get("categories") or [item["category"]]}},
                 {"region": item["region"]}]},
        PUBLIC_PROJECTION,
    ).sort([("published_at", -1)]).limit(3).to_list(length=3)
    payload = {"item": item, "related": related}
    _cache(response, payload)
    return payload


@router.post("/admin/news/refresh")
async def refresh_news(request: Request, x_admin_token: str | None = Header(None),
                       synthesis: bool = Query(True)):
    """Idempotent, lock-guarded refresh. Intended for the platform's daily scheduler."""
    _require_admin(x_admin_token)
    report = await run_ingestion(get_db(request), with_synthesis=synthesis)
    report.pop("_id", None)
    return report


@router.post("/admin/news/synthesise")
async def synthesise_pending(request: Request, x_admin_token: str | None = Header(None),
                             limit: int = Query(10, ge=1, le=60)):
    """Runs the editorial synthesis queue only — no upstream fetching."""
    _require_admin(x_admin_token)
    return await run_synthesis(get_db(request), max_items=limit)


@router.get("/admin/news/health")
async def news_health(request: Request, x_admin_token: str | None = Header(None)):
    """Operational diagnostics. Never exposed publicly and never returns credentials."""
    _require_admin(x_admin_token)
    db = get_db(request)
    latest = await db.news_health.find_one({"_id": "latest"}) or {}
    latest.pop("_id", None)
    sources = await db.news_sources.find(
        {}, {"_id": 0, "name": 1, "language": 1, "last_success_at": 1, "last_attempt_at": 1,
             "last_error": 1, "enabled": 1}).to_list(length=100)
    counts = await category_counts(db)
    statuses: dict[str, int] = {}
    async for row in db.news_items.aggregate(
            [{"$group": {"_id": "$status", "n": {"$sum": 1}}}]):
        statuses[row["_id"]] = row["n"]
    model_ok, model_state = (await ai.check_model()) if ai.is_enabled() else (False, "not-configured")
    return {
        "last_run": latest,
        "window_days": window_days(),
        "editorial_timezone": "Europe/Istanbul",
        "sources_checked": len(sources),
        "sources_failed": [s["name"] for s in sources if s.get("last_error")],
        "disabled_sources": DISABLED_SOURCES,
        "category_counts": counts,
        "category_minimum": CATEGORY_MIN_ITEMS,
        "categories_below_target": [c for c, n in counts.items() if n < CATEGORY_MIN_ITEMS],
        "status_counts": statuses,
        "ai": {"enabled": ai.is_enabled(), "model": ai.model_name() if ai.is_enabled() else None,
               "model_reachable": model_ok, "model_state": model_state,
               "limits": ai.limits(), "usage_today": await ai.usage_today(db)},
        "sources": sources,
    }


@router.get("/news-sources/status")
async def sources_status(request: Request):
    """Operational summary only — never exposes credentials or feed configuration."""
    _rate_limit(request)
    db = get_db(request)
    published = await db.news_items.count_documents(_public_query())
    return {"published_items": published, "window_days": window_days()}
