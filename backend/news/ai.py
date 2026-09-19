"""Central Gemini configuration, provider and quality gate for NOVA Journal synthesis.

Design rules enforced here:
  * The API key is read only from GEMINI_API_KEY and never returned, logged or serialised.
  * The model is read only from GEMINI_MODEL. Nothing else in the codebase names a model.
  * Synthesis is optional: every caller must keep working when this module is disabled,
    out of quota or failing.
  * No paid tier, no automatic model substitution, no grounding tools.
  * Daily request and token budgets are tracked in MongoDB, not in process memory.
"""

import asyncio
import json
import logging
import os
import random
import re
from datetime import datetime, timezone

import httpx

logger = logging.getLogger(__name__)

API_BASE = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_MODEL = "gemini-2.5-flash-lite"      # free-tier eligible; override with GEMINI_MODEL
_SEMAPHORE: asyncio.Semaphore | None = None
_BACKOFF = {"until": 0.0, "delay": 0.0}

MIN_BODY_WORDS = 600
MAX_BODY_WORDS = 1400
MIN_SOURCE_WORDS = 180          # below this the source cannot support a long-form synthesis
PLACEHOLDERS = ("lorem ipsum", "as an ai", "i cannot", "insert ", "todo", "xxx",
                "[placeholder]", "tbd", "unknown author", "as a language model")

PROMPT = """You are a senior editor writing for NOVA Journal, the newsroom of a Turkish
architecture and construction company. Write an original, factual long-form editorial
synthesis of the supplied source material.

ABSOLUTE RULES
- Use ONLY facts contained in the supplied source material. Never add background,
  statistics, names, dates, regulations, prices or consequences that are not present.
- Never invent or paraphrase quotations. Do not use quotation marks around source wording.
- Never copy sentences or distinctive phrasing from the source. Rewrite everything in your
  own institutional prose.
- Keep every qualification intact: proposal, draft, tender, permit, approved plan, court
  ruling, political statement and completed work must never be blurred together.
- Keep Turkish proper nouns, institution names, district names, regulation numbers and
  dates exactly as supplied.
- For legal or regulatory material: cite the responsible authority as supplied, never give
  advice, never describe a proposal as active law.
- No marketing language, no rhetorical questions, no generic AI filler, no repetition to
  reach length. If the material does not support the required depth, set
  "sufficient" to false.

OUTPUT
Write {min_words}-{max_words} words of body text in English, in 6 to 9 short paragraphs
distributed across 4 to 6 sections with concise sentence-case headings suited to the
material (for example: What was announced, Who is involved, Location and timing,
Technical context, Why it matters, Confirmed next steps).

Respond with JSON only:
{{"standfirst": string (25-45 words),
  "sections": [{{"heading": string, "paragraphs": [string, ...]}}, ...],
  "categories": [one or more of ART, EXHIBITIONS, GALLERIES_AND_MUSEUMS,
                 ARCHITECTURE_AND_DESIGN, CONSTRUCTION, URBAN_TRANSFORMATION, KADIKOY,
                 TECHNICAL_AND_LEGAL],
  "sufficient": boolean,
  "confidence": "high"|"medium"|"low"}}
"""

VALID_CATEGORIES = {
    "ART", "EXHIBITIONS", "GALLERIES_AND_MUSEUMS", "ARCHITECTURE_AND_DESIGN",
    "CONSTRUCTION", "URBAN_TRANSFORMATION", "KADIKOY", "TECHNICAL_AND_LEGAL",
}


# ------------------------------------------------------------------ configuration
def _int_env(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name) or default)
    except ValueError:
        return default


def model_name() -> str:
    return (os.environ.get("GEMINI_MODEL") or DEFAULT_MODEL).strip()


def is_enabled() -> bool:
    return bool(os.environ.get("GEMINI_API_KEY")) and bool(model_name())


def limits() -> dict:
    return {
        "daily_requests": _int_env("GEMINI_DAILY_REQUEST_LIMIT", 180),
        "daily_input_tokens": _int_env("GEMINI_DAILY_INPUT_TOKEN_LIMIT", 600_000),
        "daily_output_tokens": _int_env("GEMINI_DAILY_OUTPUT_TOKEN_LIMIT", 250_000),
        "concurrency": _int_env("GEMINI_MAX_CONCURRENCY", 2),
        "timeout": _int_env("GEMINI_REQUEST_TIMEOUT_SECONDS", 90),
        "min_body_words": _int_env("NEWS_MIN_BODY_WORDS", MIN_BODY_WORDS),
        "max_body_words": _int_env("NEWS_MAX_BODY_WORDS", MAX_BODY_WORDS),
    }


def _semaphore() -> asyncio.Semaphore:
    global _SEMAPHORE
    if _SEMAPHORE is None:
        _SEMAPHORE = asyncio.Semaphore(max(1, limits()["concurrency"]))
    return _SEMAPHORE


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


async def usage_today(db) -> dict:
    doc = await db.news_ai_usage.find_one({"_id": _today()}) or {}
    return {"requests": doc.get("requests", 0), "input_tokens": doc.get("input_tokens", 0),
            "output_tokens": doc.get("output_tokens", 0), "day": _today()}


async def budget_available(db) -> tuple[bool, str]:
    caps = limits()
    used = await usage_today(db)
    if used["requests"] >= caps["daily_requests"]:
        return False, "daily-request-limit"
    if used["input_tokens"] >= caps["daily_input_tokens"]:
        return False, "daily-input-token-limit"
    if used["output_tokens"] >= caps["daily_output_tokens"]:
        return False, "daily-output-token-limit"
    return True, ""


async def _record_usage(db, input_tokens: int, output_tokens: int) -> None:
    await db.news_ai_usage.update_one(
        {"_id": _today()},
        {"$inc": {"requests": 1, "input_tokens": int(input_tokens),
                  "output_tokens": int(output_tokens)},
         "$set": {"updated_at": datetime.now(timezone.utc).isoformat(),
                  "model": model_name()}},
        upsert=True)


async def check_model() -> tuple[bool, str]:
    """Confirm the configured model is reachable. Never substitutes another model."""
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        return False, "no-api-key"
    name = model_name()
    try:
        async with httpx.AsyncClient(timeout=20) as http:
            res = await http.get(f"{API_BASE}/models/{name}", headers={"x-goog-api-key": key})
    except Exception as exc:
        return False, f"provider-unreachable:{type(exc).__name__}"
    if res.status_code == 200:
        return True, "ok"
    if res.status_code in (401, 403):
        return False, "invalid-or-revoked-key"
    if res.status_code == 404:
        return False, "model-not-found"
    return False, f"http-{res.status_code}"


# ------------------------------------------------------------------ quality gate
_SHINGLE = 11


def _shingles(text: str, size: int = _SHINGLE) -> set[str]:
    words = re.findall(r"[\w’']+", (text or "").lower())
    return {" ".join(words[i:i + size]) for i in range(max(0, len(words) - size + 1))}


def _sentence_case_ok(text: str) -> bool:
    for sentence in re.split(r"(?<=[.!?])\s+", text.strip()):
        stripped = sentence.strip()
        if not stripped:
            continue
        first = re.search(r"[^\W\d_]", stripped)
        if first and first.group(0).islower():
            return False
    return True


def validate_synthesis(payload: dict, source_text: str, min_words: int, max_words: int) -> tuple[dict | None, str]:
    """Return (article, '') or (None, reason). Nothing unverified is ever published."""
    if not isinstance(payload, dict):
        return None, "unparsable-response"
    if payload.get("sufficient") is False:
        return None, "source-insufficient"
    if (payload.get("confidence") or "").lower() == "low":
        return None, "low-confidence"
    standfirst = re.sub(r"\s+", " ", str(payload.get("standfirst") or "")).strip()
    sections_raw = payload.get("sections")
    if not standfirst or not isinstance(sections_raw, list) or len(sections_raw) < 3:
        return None, "missing-structure"

    sections = []
    paragraphs_all: list[str] = []
    for section in sections_raw:
        if not isinstance(section, dict):
            return None, "malformed-section"
        heading = re.sub(r"\s+", " ", str(section.get("heading") or "")).strip()
        paragraphs = [re.sub(r"\s+", " ", str(p)).strip()
                      for p in (section.get("paragraphs") or []) if str(p).strip()]
        if not heading or not paragraphs:
            return None, "empty-section"
        if re.search(r"<[a-z/][^>]*>", heading + " ".join(paragraphs), re.I):
            return None, "html-in-body"
        sections.append({"heading": heading, "paragraphs": paragraphs})
        paragraphs_all.extend(paragraphs)

    body = " ".join(paragraphs_all)
    words = len(body.split())
    if words < min_words:
        return None, f"too-short:{words}"
    if words > max_words:
        return None, f"too-long:{words}"
    if len(paragraphs_all) < 5:
        return None, "too-few-paragraphs"
    lowered = body.lower()
    if any(token in lowered for token in PLACEHOLDERS):
        return None, "placeholder-text"
    if not body.rstrip().endswith((".", "!", "?", "”", '"')):
        return None, "incomplete-final-sentence"
    if not _sentence_case_ok(body) or not _sentence_case_ok(standfirst):
        return None, "sentence-case"
    if '"' in body or "“" in body:
        return None, "quotation-marks"

    source_numbers = set(re.findall(r"\d[\d.,]*", source_text))
    normalised_source = {n.replace(".", "").replace(",", "") for n in source_numbers}
    for number in set(re.findall(r"\d[\d.,]*", body)):
        bare = number.replace(".", "").replace(",", "")
        if len(bare) >= 2 and bare not in normalised_source:
            return None, f"unsupported-number:{number}"

    overlap = _shingles(body) & _shingles(source_text)
    if overlap:
        return None, "verbatim-overlap"

    categories = [c.strip().upper() for c in (payload.get("categories") or [])
                  if isinstance(c, str) and c.strip().upper() in VALID_CATEGORIES]
    repetition = _repetition_ratio(paragraphs_all)
    if repetition > 0.34:
        return None, f"repetition:{repetition:.2f}"
    return {
        "standfirst": standfirst,
        "sections": sections,
        "body": body,
        "word_count": words,
        "categories": categories,
        "confidence": (payload.get("confidence") or "medium").lower(),
    }, ""


def _repetition_ratio(paragraphs: list[str]) -> float:
    seen: set[str] = set()
    duplicates = 0
    total = 0
    for paragraph in paragraphs:
        for shingle in _shingles(paragraph, 6):
            total += 1
            if shingle in seen:
                duplicates += 1
            seen.add(shingle)
    return duplicates / total if total else 0.0


# ------------------------------------------------------------------ provider call
def _back_off() -> None:
    delay = min(max(_BACKOFF["delay"] * 2, 90.0), 3600.0)
    _BACKOFF["delay"] = delay + random.uniform(0, 30)
    _BACKOFF["until"] = asyncio.get_event_loop().time() + _BACKOFF["delay"]


def _backing_off() -> bool:
    try:
        return asyncio.get_event_loop().time() < _BACKOFF["until"]
    except RuntimeError:
        return False


async def synthesise(db, article: dict) -> tuple[dict | None, str]:
    """Generate and validate a long-form synthesis. Returns (article, '') or (None, code)."""
    if not is_enabled():
        return None, "ai-disabled"
    if _backing_off():
        return None, "backing-off"
    source_text = article.get("source_text") or ""
    if len(source_text.split()) < MIN_SOURCE_WORDS:
        return None, "source-insufficient"
    ok, reason = await budget_available(db)
    if not ok:
        return None, reason

    caps = limits()
    prompt = PROMPT.format(min_words=max(caps["min_body_words"] + 100, 700),
                           max_words=min(caps["max_body_words"] - 200, 1200))
    payload_text = (
        f"{prompt}\n\nSOURCE PUBLISHER: {article['source_name']}\n"
        f"PUBLISHED: {article['published_at']}\n"
        f"SOURCE HEADLINE: {article['title']}\n"
        f"SOURCE LANGUAGE: {article.get('source_language', 'en')}\n"
        f"SOURCE MATERIAL:\n{source_text[:24000]}"
    )
    body = {
        "contents": [{"parts": [{"text": payload_text}]}],
        "generationConfig": {"temperature": 0.25, "topP": 0.9,
                             "responseMimeType": "application/json",
                             "maxOutputTokens": 4096},
    }
    url = f"{API_BASE}/models/{model_name()}:generateContent"
    key = os.environ["GEMINI_API_KEY"]
    try:
        async with _semaphore():
            async with httpx.AsyncClient(timeout=caps["timeout"]) as http:
                res = await http.post(url, json=body, headers={"x-goog-api-key": key})
    except Exception as exc:
        logger.warning("gemini request failed: %s", type(exc).__name__)
        _back_off()
        return None, f"request-failed:{type(exc).__name__}"

    if res.status_code == 429:
        _back_off()
        return None, "quota-exhausted"
    if res.status_code in (401, 403):
        return None, "invalid-or-revoked-key"
    if res.status_code == 404:
        return None, "model-not-found"
    if res.status_code >= 500:
        _back_off()
        return None, f"provider-error-{res.status_code}"
    if res.status_code != 200:
        return None, f"http-{res.status_code}"

    _BACKOFF["delay"] = 0.0
    try:
        data = res.json()
        meta = data.get("usageMetadata") or {}
        await _record_usage(db, meta.get("promptTokenCount", 0),
                            meta.get("candidatesTokenCount", 0))
        candidate = (data.get("candidates") or [{}])[0]
        if candidate.get("finishReason") in ("SAFETY", "RECITATION", "BLOCKLIST"):
            return None, f"blocked:{candidate['finishReason'].lower()}"
        raw = candidate["content"]["parts"][0]["text"]
        parsed = json.loads(raw)
    except Exception:
        return None, "unparsable-response"

    result, reason = validate_synthesis(parsed, source_text, caps["min_body_words"],
                                        caps["max_body_words"])
    if not result:
        return None, f"quality:{reason}"
    result["model"] = model_name()
    return result, ""
