from fastapi import FastAPI, APIRouter, HTTPException, Response
from dotenv import load_dotenv
import httpx
import time
import asyncio
from curl_cffi import requests as cffi_requests
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List
import uuid
from datetime import datetime, timezone


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

IG_USERNAME = "novakonut"
IG_APP_ID = "936619743392459"
IG_UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
_ig_cache: dict = {"at": 0.0, "posts": []}
_ig_image_urls: dict = {}
IG_TTL = 1800


async def _fetch_instagram_posts(limit: int = 4) -> List[dict]:
    url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={IG_USERNAME}"
    edges = None
    for attempt in range(3):
        res = await asyncio.to_thread(
            cffi_requests.get, url,
            headers={"x-ig-app-id": IG_APP_ID}, impersonate="safari17_0", timeout=20)
        if res.status_code == 200:
            edges = res.json()["data"]["user"]["edge_owner_to_timeline_media"]["edges"]
            break
        await asyncio.sleep(0.6 * (attempt + 1))
    if edges is None:
        raise RuntimeError("instagram profile fetch failed")
    posts = []
    for edge in edges[:limit]:
        node = edge["node"]
        caption_edges = node["edge_media_to_caption"]["edges"]
        caption = caption_edges[0]["node"]["text"].split("\n")[0] if caption_edges else ""
        _ig_image_urls[node["shortcode"]] = node["display_url"]
        posts.append({
            "shortcode": node["shortcode"],
            "permalink": f"https://www.instagram.com/p/{node['shortcode']}/",
            "image": f"/api/instagram/image/{node['shortcode']}",
            "caption": caption[:140],
            "is_video": node.get("is_video", False),
        })
    return posts


@api_router.get("/instagram/latest")
async def instagram_latest():
    now = time.time()
    if _ig_cache["posts"] and now - _ig_cache["at"] < IG_TTL:
        return {"posts": _ig_cache["posts"], "cached": True}
    try:
        posts = await _fetch_instagram_posts()
        _ig_cache.update({"at": now, "posts": posts})
        await db.ig_cache.update_one(
            {"_id": IG_USERNAME},
            {"$set": {"posts": posts, "images": _ig_image_urls,
                      "saved_at": datetime.now(timezone.utc).isoformat()}},
            upsert=True)
        return {"posts": posts, "cached": False}
    except Exception as exc:
        logger.warning("instagram fetch failed: %s", exc)
        if _ig_cache["posts"]:
            return {"posts": _ig_cache["posts"], "cached": True, "stale": True}
        saved = await db.ig_cache.find_one({"_id": IG_USERNAME})
        if saved:
            _ig_cache.update({"at": now, "posts": saved["posts"]})
            _ig_image_urls.update(saved.get("images", {}))
            return {"posts": saved["posts"], "cached": True, "stale": True}
        raise HTTPException(status_code=503, detail="instagram unavailable")


@api_router.get("/instagram/image/{shortcode}")
async def instagram_image(shortcode: str):
    if not _ig_cache["posts"] or time.time() - _ig_cache["at"] >= IG_TTL:
        try:
            _ig_cache.update({"at": time.time(), "posts": await _fetch_instagram_posts(12)})
        except Exception as exc:
            logger.warning("instagram refresh failed: %s", exc)
    src = _ig_image_urls.get(shortcode)
    if not src:
        saved = await db.ig_cache.find_one({"_id": IG_USERNAME})
        if saved:
            _ig_image_urls.update(saved.get("images", {}))
            src = _ig_image_urls.get(shortcode)
    if not src:
        raise HTTPException(status_code=404, detail="unknown post")
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as http:
        res = await http.get(src, headers={"User-Agent": IG_UA})
    if res.status_code != 200:
        res = await asyncio.to_thread(cffi_requests.get, src, impersonate="safari17_0", timeout=20)
    if res.status_code != 200:
        raise HTTPException(status_code=502, detail="image unavailable")
    return Response(content=res.content,
                    media_type=res.headers.get("content-type", "image/jpeg"),
                    headers={"Cache-Control": "public, max-age=3600"})


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()