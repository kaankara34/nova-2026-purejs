"""Server-side news image validation, local WebP derivatives and category fallbacks.

Nothing is displayed unless it is either (a) a locally cached, decoded, sharp derivative of a
publisher-syndicated feed image, or (b) a local NOVA editorial category cover.
"""

import hashlib
import ipaddress
import logging
import os
import socket
from io import BytesIO
from urllib.parse import urlparse

import httpx
from PIL import Image, ImageFilter, ImageStat

logger = logging.getLogger(__name__)

MEDIA_ROOT = os.environ.get("NEWS_MEDIA_ROOT", "/app/frontend/media/news")
CACHE_DIR = os.path.join(MEDIA_ROOT, "cache")
PUBLIC_BASE = "media/news"

CARD_SIZE = (1200, 750)     # 16 / 10
DETAIL_SIZE = (1600, 900)   # 16 / 9
MIN_SOURCE_WIDTH = 720
PREFERRED_SOURCE_WIDTH = 900
MAX_DOWNLOAD = 8 * 1024 * 1024
MIN_BYTES = 12 * 1024
MIN_SHARPNESS = 6.0
USER_AGENT = "NovaKonutNewsroomBot/1.0 (+https://nova.istanbul; newsroom image cache)"
LOGO_HINTS = ("logo", "sprite", "icon", "favicon", "avatar", "placeholder", "default-", "1x1",
              "pixel", "badge", "watermark")


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


def fallback_for(category: str) -> dict:
    slug = (category or "ART").lower().replace("_", "-")
    return {
        "image_kind": "fallback",
        "image_card": f"{PUBLIC_BASE}/fallback/{slug}-card.webp",
        "image_detail": f"{PUBLIC_BASE}/fallback/{slug}-detail.webp",
        "image_card_width": CARD_SIZE[0],
        "image_card_height": CARD_SIZE[1],
        "image_detail_width": DETAIL_SIZE[0],
        "image_detail_height": DETAIL_SIZE[1],
        "image_credit": "",
        "image_alt_suffix": "NOVA Journal category cover",
    }


def _sharpness(img: Image.Image) -> float:
    small = img.convert("L")
    if small.width > 900:
        small = small.resize((900, max(1, int(small.height * 900 / small.width))))
    edges = small.filter(ImageFilter.FIND_EDGES)
    return ImageStat.Stat(edges).stddev[0]


def _rejects(url: str, raw: bytes, img: Image.Image) -> str | None:
    lowered = url.lower()
    if any(hint in lowered for hint in LOGO_HINTS):
        return "logo-or-icon-url"
    if len(raw) < MIN_BYTES:
        return "file-too-small"
    w, h = img.size
    if w < MIN_SOURCE_WIDTH:
        return f"source-too-narrow ({w}px)"
    ratio = w / h if h else 0
    if ratio < 0.75 or ratio > 3.2:
        return f"extreme-aspect-ratio ({ratio:.2f})"
    if w * h < 300 * 300:
        return "too-few-pixels"
    if _sharpness(img) < MIN_SHARPNESS:
        return "fails-sharpness-check"
    return None


OG_RE = None


async def _og_image(article_url: str) -> str:
    """Read a permitted Open Graph image reference from the article page (no scraping of body)."""
    import re as _re
    parsed = urlparse(article_url or "")
    if parsed.scheme != "https" or not parsed.hostname or not _public_host(parsed.hostname):
        return ""
    try:
        async with httpx.AsyncClient(timeout=12, follow_redirects=True, max_redirects=3) as http:
            res = await http.get(article_url, headers={"User-Agent": USER_AGENT,
                                                       "Accept": "text/html"})
        if res.status_code != 200 or "text/html" not in res.headers.get("content-type", ""):
            return ""
        head = res.text[:400_000]
    except Exception:
        return ""
    match = _re.search(
        r'<meta[^>]+(?:property|name)=["\']og:image(?::secure_url)?["\'][^>]+content=["\']([^"\']+)',
        head, _re.IGNORECASE)
    if not match:
        match = _re.search(
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']og:image',
            head, _re.IGNORECASE)
    url = match.group(1).strip() if match else ""
    return url if url.startswith("https://") else ""


async def pick_image(candidates: list[str], category: str, article_url: str,
                     og_budget: list[int]) -> dict:
    """Feed media -> enclosure -> feed HTML image -> permitted Open Graph -> local fallback."""
    for candidate in candidates or []:
        result = await cache_image(candidate, category)
        if result["image_kind"] == "cached":
            result["image_origin"] = candidate
            return result
    if og_budget and og_budget[0] > 0:
        og_budget[0] -= 1
        og_url = await _og_image(article_url)
        if og_url:
            result = await cache_image(og_url, category)
            if result["image_kind"] == "cached":
                result["image_origin"] = og_url
                return result
    return fallback_for(category)


async def cache_image(url: str, category: str) -> dict:
    """Validate a feed image and store local card/detail WebP derivatives.

    Returns a dict of image fields; falls back to the local category cover on any failure.
    """
    parsed = urlparse(url or "")
    if parsed.scheme != "https" or not parsed.hostname or not _public_host(parsed.hostname):
        return fallback_for(category)

    digest = hashlib.sha256(url.encode()).hexdigest()[:20]
    os.makedirs(CACHE_DIR, exist_ok=True)
    card_path = os.path.join(CACHE_DIR, f"{digest}-card.webp")
    detail_path = os.path.join(CACHE_DIR, f"{digest}-detail.webp")

    if os.path.exists(card_path) and os.path.exists(detail_path):
        return _fields(digest, card_path, detail_path)

    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True, max_redirects=3) as http:
            res = await http.get(url, headers={"User-Agent": USER_AGENT, "Accept": "image/*"})
        if res.status_code != 200:
            return fallback_for(category)
        if not res.headers.get("content-type", "").startswith("image/"):
            return fallback_for(category)
        raw = res.content[:MAX_DOWNLOAD]
        img = Image.open(BytesIO(raw))
        img.load()
    except Exception as exc:
        logger.info("news image rejected (%s): %s", type(exc).__name__, url[:120])
        return fallback_for(category)

    reason = _rejects(url, raw, img)
    if reason:
        logger.info("news image rejected (%s): %s", reason, url[:120])
        return fallback_for(category)

    try:
        base = img.convert("RGB")
        _crop_to(base, CARD_SIZE).save(card_path, "WEBP", quality=86, method=5)
        _crop_to(base, DETAIL_SIZE).save(detail_path, "WEBP", quality=86, method=5)
    except Exception as exc:
        logger.info("news image derivative failed (%s)", type(exc).__name__)
        return fallback_for(category)
    return _fields(digest, card_path, detail_path)


def _crop_to(img: Image.Image, target: tuple[int, int]) -> Image.Image:
    tw, th = target
    # Never upscale beyond the source: cap the target at the source width.
    scale = min(1.0, img.width / tw)
    tw, th = max(1, int(tw * scale)), max(1, int(th * scale))
    src_ratio = img.width / img.height
    dst_ratio = tw / th
    if src_ratio > dst_ratio:
        new_w = int(img.height * dst_ratio)
        left = (img.width - new_w) // 2
        box = (left, 0, left + new_w, img.height)
    else:
        new_h = int(img.width / dst_ratio)
        top = int((img.height - new_h) * 0.35)
        box = (0, top, img.width, top + new_h)
    return img.crop(box).resize((tw, th), Image.LANCZOS)


def _fields(digest: str, card_path: str, detail_path: str) -> dict:
    with Image.open(card_path) as card, Image.open(detail_path) as detail:
        card_size, detail_size = card.size, detail.size
    return {
        "image_kind": "cached",
        "image_card": f"{PUBLIC_BASE}/cache/{digest}-card.webp",
        "image_detail": f"{PUBLIC_BASE}/cache/{digest}-detail.webp",
        "image_card_width": card_size[0],
        "image_card_height": card_size[1],
        "image_detail_width": detail_size[0],
        "image_detail_height": detail_size[1],
        "image_alt_suffix": "",
    }
