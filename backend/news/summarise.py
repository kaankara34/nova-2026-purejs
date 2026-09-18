"""Optional Gemini free-tier summarisation with a deterministic fallback.

The newsroom never depends on Gemini: when GEMINI_API_KEY is missing, the quota is
exhausted (429), the provider times out or the response fails validation, the deterministic
fallback chain is used instead and ingestion continues.
"""

import asyncio
import json
import logging
import os
import re

import httpx

logger = logging.getLogger(__name__)

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
DEFAULT_MODEL = "gemini-3.5-flash-lite"

PROMPT = (
    "You are an editorial assistant for an architecture and art newsroom. "
    "Using ONLY the public headline, public feed description, source name and date supplied below, "
    "produce a factual English summary.\n"
    "Hard rules: never invent dates, people, institutions, numbers or legal conclusions; never add "
    "facts that are not present in the supplied text; never turn an opinion or a proposal into an "
    "enacted fact; never describe a render, competition entry or announcement as a completed event; "
    "keep legally important qualifications (draft, proposed, pending) intact; keep Turkish proper "
    "nouns, institution names, regulation numbers and dates exactly as given.\n"
    "Tone: calm, corporate, editorial. No marketing language. 80-160 words.\n"
    "If the supplied text is too thin to summarise faithfully, set confidence to \"low\".\n"
    'Respond with JSON only: {"translated_title": string, "summary": string, '
    '"category": one of ART|EXHIBITIONS|GALLERIES_AND_MUSEUMS|ARCHITECTURE_AND_DESIGN|CONSTRUCTION|'
    'URBAN_TRANSFORMATION|KADIKOY|TECHNICAL_AND_LEGAL, "confidence": "high"|"medium"|"low"}'
)

_VALID_CATEGORIES = {
    "ART", "EXHIBITIONS", "GALLERIES_AND_MUSEUMS", "ARCHITECTURE_AND_DESIGN",
    "CONSTRUCTION", "URBAN_TRANSFORMATION", "KADIKOY", "TECHNICAL_AND_LEGAL",
}

_BACKOFF_STATE = {"until": 0.0, "delay": 0.0}


def is_configured() -> bool:
    return bool(os.environ.get("GEMINI_API_KEY"))


def model_name() -> str:
    return os.environ.get("GEMINI_MODEL") or DEFAULT_MODEL


ARTEFACTS = [
    r"continue reading.*$", r"read more.*$", r"read the full (story|article).*$",
    r"\[\s*…?\s*\]", r"\[\.{3}\]", r"the post .*appeared first on.*$",
    r"this article (first )?appeared.*$", r"sign up (to|for) .*newsletter.*$",
    r"subscribe (to|for) .*$", r"we use cookies.*$", r"support (our|independent) journalism.*$",
    r"share this article.*$", r"follow us on .*$", r"photo(graph)?s? by .*$",
    r"devamını oku.*$", r"haberin detayları.*$", r"abone ol.*$",
    r"all rights reserved.*$", r"©.*$",
]
_ARTEFACT_RE = [re.compile(p, re.IGNORECASE | re.DOTALL) for p in ARTEFACTS]
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def clean_source_text(text: str) -> str:
    """Remove feed artefacts, boilerplate and trailing fragments."""
    text = re.sub(r"\s+", " ", text or "").strip()
    for pattern in _ARTEFACT_RE:
        text = pattern.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip(" -–—·|")
    return text


def _complete_sentences(text: str, min_words: int, max_words: int) -> str:
    """Keep whole sentences only, up to max_words."""
    sentences = [s.strip() for s in _SENTENCE_END.split(text) if s.strip()]
    kept: list[str] = []
    words = 0
    for sentence in sentences:
        count = len(sentence.split())
        if kept and words + count > max_words:
            break
        kept.append(sentence)
        words += count
        if words >= max_words:
            break
    if not kept:
        return ""
    result = " ".join(kept).strip()
    if not result.endswith((".", "!", "?", "…", '"', "”")):
        # drop the trailing incomplete clause rather than showing a cut-off sentence
        if len(kept) > 1:
            result = " ".join(kept[:-1]).strip()
        else:
            return ""
    return result


def deterministic_summary(title: str, description: str, source_name: str, limit: int = 600) -> tuple[str, str]:
    """Fallback chain: cleaned feed description -> source excerpt -> headline + attribution."""
    text = clean_source_text(description)
    complete = _complete_sentences(text, 35, 160)
    if len(complete.split()) >= 30:
        return complete, "feed_description"
    if len(text.split()) >= 18:
        excerpt = _complete_sentences(text, 12, 160) or text[:limit].rsplit(" ", 1)[0]
        if not excerpt.endswith((".", "!", "?", "…")):
            excerpt = excerpt.rstrip(" ,;:") + "."
        return excerpt, "source_excerpt"
    return f"{title.strip().rstrip('.')}. Reported by {source_name}.", "headline_only"


def _validate(payload: dict, title: str, description: str) -> dict | None:
    summary = (payload.get("summary") or "").strip()
    translated = (payload.get("translated_title") or "").strip()
    category = (payload.get("category") or "").strip().upper()
    confidence = (payload.get("confidence") or "").strip().lower()
    if confidence == "low":
        return None
    words = len(summary.split())
    if words < 25 or words > 220:
        return None
    if category and category not in _VALID_CATEGORIES:
        category = ""
    # Reject numbers (years, figures) that do not appear in the supplied source material.
    source_text = f"{title} {description}"
    source_numbers = set(re.findall(r"\d{2,}", source_text))
    for number in set(re.findall(r"\d{2,}", summary)):
        if number not in source_numbers:
            return None
    return {
        "summary": summary,
        "translated_title": translated or title,
        "category": category,
        "confidence": confidence or "medium",
    }


async def gemini_summary(title: str, description: str, source_name: str, published: str) -> dict | None:
    """Return validated Gemini output, or None so the caller uses the deterministic fallback."""
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        return None
    loop = asyncio.get_event_loop()
    if loop.time() < _BACKOFF_STATE["until"]:
        return None
    body = {
        "contents": [{
            "parts": [{
                "text": (
                    f"{PROMPT}\n\nSOURCE NAME: {source_name}\nPUBLISHED: {published}\n"
                    f"HEADLINE: {title}\nFEED DESCRIPTION: {description}"
                )
            }]
        }],
        "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json", "maxOutputTokens": 700},
    }
    url = GEMINI_ENDPOINT.format(model=model_name())
    try:
        async with httpx.AsyncClient(timeout=25) as http:
            res = await http.post(url, json=body, headers={"x-goog-api-key": key})
    except Exception as exc:  # network / timeout
        logger.warning("gemini request failed: %s", type(exc).__name__)
        _back_off(loop)
        return None
    if res.status_code == 429 or res.status_code >= 500:
        logger.warning("gemini unavailable (status %s) — using deterministic fallback", res.status_code)
        _back_off(loop)
        return None
    if res.status_code != 200:
        logger.warning("gemini rejected request (status %s)", res.status_code)
        return None
    _BACKOFF_STATE["delay"] = 0.0
    try:
        raw = res.json()["candidates"][0]["content"]["parts"][0]["text"]
        payload = json.loads(raw)
    except Exception:
        logger.warning("gemini returned an unparsable response")
        return None
    if not isinstance(payload, dict):
        return None
    return _validate(payload, title, description)


def _back_off(loop) -> None:
    delay = min(max(_BACKOFF_STATE["delay"] * 2, 60.0), 3600.0)
    _BACKOFF_STATE["delay"] = delay
    _BACKOFF_STATE["until"] = loop.time() + delay
