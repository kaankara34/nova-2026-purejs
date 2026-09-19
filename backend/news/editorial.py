"""Editorial relevance and brand-safety gate.

Runs before any AI call so irrelevant or unsuitable material never consumes quota.
Two independent judgements are made:

  * relevance  — is the dominant subject inside NOVA's editorial scope at all?
  * suitability — is the framing acceptable for a corporate journal?

Nothing here rewrites a story. Unsuitable material is excluded, never distorted.
"""

import re

from .filters import BUILT_CATEGORIES, CULTURE_CATEGORIES, _matches, normalise

# Subjects permanently outside NOVA Journal, whatever regulation they concern.
HARD_EXCLUDE = [
    # livestock, agriculture, food, veterinary
    "canlı hayvan", "hayvan nakil", "hayvansal ürün", "besicilik", "hayvancılık",
    "büyükbaş", "küçükbaş", "kesimhane", "mezbaha", "veteriner", "şap hastalığı",
    "tarım bakanlığı", "tarımsal üretim", "çiftçi", "hasat", "gübre", "tohum",
    "buğday", "fındık", "zeytinyağı", "süt üretimi", "balıkçılık", "sera gazı emisyon ticareti",
    "livestock", "cattle", "poultry", "slaughterhouse", "veterinary", "farmers",
    "agriculture", "agricultural", "harvest", "fertiliser", "fertilizer", "crop yield",
    "food production", "fisheries",
    # sport, entertainment, celebrity
    "futbol", "basketbol", "maçı", "transfer dönemi", "milli takım", "şampiyona",
    "televizyon dizisi", "dizi bölümü", "sezon finali", "reality show", "magazin programı",
    # unrelated transport / consumer
    "uçak bileti", "otobüs bileti", "trafik cezası", "ehliyet", "araç muayene",
    "cep telefonu kampanyası", "akıllı telefon", "otomobil modeli", "elektrikli otomobil",
    # unrelated legal / political
    "cinayet davası", "uyuşturucu", "terör soruşturması", "seçim sonuçları",
    "milletvekili dokunulmazlığı", "boşanma davası",
]

# A regulation, court decision or ministry announcement only belongs in
# TECHNICAL & LEGAL when its subject is the built environment.
BUILT_SUBJECT_TERMS = [
    "imar", "yapı", "yapım", "inşaat", "bina", "konut", "kentsel dönüşüm", "iskan",
    "ruhsat", "yapı denetim", "deprem", "zemin", "betonarme", "çelik yapı", "mimarlık",
    "mimar", "mühendis", "şehir plan", "planlama", "kat karşılığı", "kat mülkiyeti",
    "tapu", "gayrimenkul", "emlak vergisi", "yangın güvenliği", "enerji kimlik belgesi",
    "yapı malzeme", "kamu ihale", "ihale", "altyapı", "metro", "köprü", "tünel",
    "sit alanı", "koruma amaçlı imar", "rezerv yapı", "riskli yapı", "güçlendirme",
    "building", "buildings", "construction", "housing", "zoning", "planning permission",
    "planning", "permit", "architect", "architecture", "engineering", "seismic",
    "earthquake", "structural", "fire safety", "procurement", "infrastructure",
    "real estate", "property law", "condominium", "title deed", "heritage site",
]

NEGATIVE_MARKERS = [
    "toparlanamadı", "düşüş sürdü", "daralma", "daraldı", "küçüldü", "gerileme",
    "gerilledi", "kriz", "iflas", "konkordato", "çöküş", "çöktü", "durgunluk",
    "resesyon", "zarar açıkladı", "işten çıkar", "işçi çıkar", "kayıp", "skandal",
    "yolsuzluk", "rüşvet", "usulsüzlük", "panik", "batık", "borç krizi", "yıkıldı",
    "göçük", "can kaybı", "ölü", "yaralı", "facia", "felaket",
    "downturn", "slump", "contraction", "contracted", "declined", "decline continued",
    "recession", "crisis", "collapse", "collapsed", "bankruptcy", "insolvency",
    "layoffs", "job cuts", "scandal", "corruption", "fraud", "plunged", "slowdown",
    "failure", "casualties", "fatalities", "disaster",
]

POSITIVE_MARKERS = [
    "temeli atıldı", "tamamlandı", "teslim edildi", "açıldı", "hizmete girdi",
    "yatırım", "yeni proje", "imzalandı", "onaylandı", "başlıyor", "büyüme",
    "ihale sonuçlandı", "ödül", "iyileştirme", "güçlendirme", "yenileniyor",
    "dönüşüm", "sürdürülebilir", "inovasyon", "ar-ge", "istihdam", "restorasyon",
    "kazandı", "rekor üretim", "kapasite artışı", "teknoloji",
    "groundbreaking", "completed", "delivered", "opens", "opened", "unveils",
    "unveiled", "approved", "investment", "wins", "award", "launch", "launches",
    "expansion", "growth", "innovation", "retrofit", "restoration", "adaptive reuse",
    "sustainable", "upgrade", "milestone", "breakthrough", "record output",
]


def _hits(haystack: str, terms: list[str]) -> list[str]:
    """Word-boundary matching: "magazine" must never match the Turkish word "magazin"."""
    return [term for term in terms if _matches(haystack, term, False)]


def _tone(title_hay: str, full_hay: str) -> tuple[str, str]:
    negative_title = _hits(title_hay, NEGATIVE_MARKERS)
    negative_body = _hits(full_hay, NEGATIVE_MARKERS)
    positive = _hits(full_hay, POSITIVE_MARKERS)
    if negative_title or len(negative_body) >= 2:
        return "negative", "negative framing: " + ", ".join((negative_title or negative_body)[:3])
    if positive:
        return "positive" if _hits(title_hay, POSITIVE_MARKERS) else "constructive", ""
    return "neutral_technical", ""


def assess(title: str, description: str, body: str, primary: str,
           categories: list[str], source: dict) -> dict:
    """Return the editorial verdict for one candidate article."""
    title_hay = normalise(title)
    head_hay = normalise(f"{title} {description}")
    full_hay = normalise(f"{title} {description} {body[:6000]}")

    excluded = _hits(head_hay, HARD_EXCLUDE)
    if excluded:
        return {"status": "irrelevant", "reason": f"excluded subject: {excluded[0]}",
                "tone": "irrelevant", "categories": categories}

    body_excluded = _hits(full_hay, HARD_EXCLUDE)
    kept_categories = list(categories)

    if primary == "TECHNICAL_AND_LEGAL" or "TECHNICAL_AND_LEGAL" in kept_categories:
        if not _hits(full_hay, BUILT_SUBJECT_TERMS):
            kept_categories = [c for c in kept_categories if c != "TECHNICAL_AND_LEGAL"]
            if not kept_categories:
                return {"status": "irrelevant",
                        "reason": "regulatory story with no built-environment subject",
                        "tone": "irrelevant", "categories": categories}
            primary = kept_categories[0]

    if body_excluded and not _hits(full_hay, BUILT_SUBJECT_TERMS):
        return {"status": "needs_review",
                "reason": f"ambiguous subject: {body_excluded[0]}",
                "tone": "needs_review", "categories": kept_categories}

    tone, tone_reason = _tone(title_hay, full_hay)
    built = bool(set(kept_categories) & BUILT_CATEGORIES)
    culture = bool(set(kept_categories) & CULTURE_CATEGORIES)
    if not built and not culture:
        return {"status": "needs_review", "reason": "no NOVA editorial category matched",
                "tone": tone, "categories": kept_categories}

    if tone == "negative":
        return {"status": "brand_unsafe_negative",
                "reason": tone_reason or "negative framing",
                "tone": tone, "categories": kept_categories}

    if primary == "CONSTRUCTION" and tone == "neutral_technical":
        # Accept a neutral construction story only when it is a genuine technical
        # development rather than general market reporting.
        if not _hits(full_hay, BUILT_SUBJECT_TERMS):
            return {"status": "needs_review",
                    "reason": "neutral construction story without a technical subject",
                    "tone": tone, "categories": kept_categories}

    return {"status": "ok", "reason": "", "tone": tone, "categories": kept_categories,
            "primary": primary}


NEGATIVE_TITLE_RE = re.compile("|".join(re.escape(t) for t in NEGATIVE_MARKERS))
