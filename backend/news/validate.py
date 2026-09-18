"""Editorial text normalisation and source-URL validation."""

import logging
import re
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)

BROWSER_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/125.0 Safari/537.36 NovaKonutNewsroomBot/1.0")
TIMEOUT = 7.0

# Brands that are deliberately lowercase: keep their styling mid-sentence, but a NOVA
# headline still has to open with a capital letter.
ACRONYMS = {
    "AI", "LEED", "UNESCO", "İBB", "IBB", "TMMOB", "TÜİK", "TUIK", "AFAD", "MoMA", "V&A",
    "UK", "US", "USA", "EU", "UAE", "OSB", "TOKİ", "TOKI", "BIM", "HVAC", "LED", "3D", "2D",
    "MIT", "RIBA", "AIA", "CO2", "ESG", "NFT", "UN", "PhD", "CEO", "SALT", "İKSV", "IKSV",
}
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])(\s+)")
_FIRST_ALPHA = re.compile(r"[^\W\d_]", re.UNICODE)


def _upper_first(text: str) -> str:
    match = _FIRST_ALPHA.search(text)
    if not match:
        return text
    i = match.start()
    first = text[i]
    upper = "İ" if first == "i" and _looks_turkish(text) else first.upper()
    return text[:i] + upper + text[i + 1:]


def _looks_turkish(text: str) -> bool:
    return any(ch in text for ch in "ğşıöüçĞŞİÖÜÇ")


def _protected(word: str) -> bool:
    bare = word.strip("“”\"'()[].,:;!?—–-")
    return bare in ACRONYMS or bare.upper() in ACRONYMS


def normalise_editorial(text: str) -> str:
    """Capitalise the first letter of the text and of every sentence, without touching
    acronyms, proper names or intentional internal casing."""
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text:
        return text
    parts = _SENTENCE_SPLIT.split(text)
    rebuilt = []
    for part in parts:
        if part.strip() and not part.isspace():
            first_word = part.strip().split(" ", 1)[0]
            rebuilt.append(part if _protected(first_word) else _upper_first(part))
        else:
            rebuilt.append(part)
    return "".join(rebuilt).strip()


def _bad_final_url(final_url: str, original: str) -> bool:
    parsed = urlparse(final_url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return True
    path = (parsed.path or "/").rstrip("/")
    # A redirect to the publisher homepage or a generic error path is not the article.
    if not path or path in ("/index.html", "/home"):
        return True
    if re.search(r"/(404|error|not-found|page-not-found|gone|expired)(/|$)", path, re.I):
        return True
    original_host = urlparse(original).hostname or ""
    if original_host and parsed.hostname != original_host:
        # allow www/non-www and simple subdomain moves within the same registrable domain
        a = ".".join(original_host.split(".")[-2:])
        b = ".".join(parsed.hostname.split(".")[-2:])
        if a != b:
            return True
    return False


async def validate_source_url(url: str) -> tuple[bool, str]:
    """Confirm an article URL resolves to a real article page.

    Returns (ok, resolved_url). HEAD is attempted first; a blocked or inconclusive HEAD
    is never treated as proof of unavailability, so a lightweight GET is used as well.
    """
    parsed = urlparse(url or "")
    if parsed.scheme not in ("http", "https") or not parsed.hostname or " " in (url or ""):
        return False, url
    headers = {"User-Agent": BROWSER_UA, "Accept": "text/html,application/xhtml+xml"}
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True,
                                     max_redirects=5, headers=headers) as http:
            try:
                res = await http.head(url)
                if res.status_code < 400 and not _bad_final_url(str(res.url), url):
                    return True, str(res.url)
            except Exception:
                pass
            res = await http.get(url, headers={**headers, "Range": "bytes=0-40960"})
            if res.status_code >= 400:
                return False, url
            final = str(res.url)
            if _bad_final_url(final, url):
                return False, final
            body = res.text[:40_000].lower()
            if "<title" in body and re.search(
                    r"<title[^>]*>[^<]*(404|page not found|not found|sayfa bulunamad)", body):
                return False, final
            return True, final
    except Exception as exc:
        logger.info("source url validation failed (%s): %s", type(exc).__name__, url[:120])
        return False, url
