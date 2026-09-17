"""Editorial relevance filtering for the NOVA newsroom.

An item is only accepted when it matches at least one STRONG term — an unambiguous signal
for NOVA's editorial fields. WEAK terms never qualify an item on their own; they only add
to the score. This keeps general news agency feeds from leaking unrelated stories in.
"""

import re

STRONG_TERMS = {
    "EXHIBITIONS": [
        "exhibition", "retrospective", "biennial", "biennale", "art fair", "triennial",
        "art basel", "documenta", "pavilion of", "sergi", "sergisi", "bienal",
        "retrospektif", "sanat fuarı", "küratörlüğünde",
    ],
    "GALLERIES_AND_MUSEUMS": [
        "museum", "museums", "gallery", "galleries", "curator", "curatorial",
        "permanent collection", "acquires", "acquisition of", "art institution",
        "müze", "müzesi", "galeri", "galerisi", "koleksiyonu", "küratör",
    ],
    "ART": [
        "artist", "artists", "artwork", "artworks", "sculpture", "painter", "paintings",
        "contemporary art", "art world", "art prize", "art history", "installation art",
        "photographer", "sanatçı", "sanat eseri", "heykel", "çağdaş sanat", "sanat tarihi",
        "ressam", "fotoğraf sanatçısı",
    ],
    "ARCHITECTURE_AND_DESIGN": [
        "architecture", "architect", "architects", "architectural", "interior design",
        "industrial design", "design studio", "adaptive reuse", "masterplan", "master plan",
        "landscape architecture", "facade design", "mimarlık", "mimarı", "mimarlar",
        "mimari", "iç mimarlık", "endüstriyel tasarım", "peyzaj mimarlığı", "tasarım stüdyosu",
    ],
    "CONSTRUCTION": [
        "construction sector", "construction industry", "construction project",
        "contractor", "contractors", "building materials", "structural engineering",
        "housing supply", "residential development", "building site",
        "inşaat sektörü", "inşaat firması", "müteahhit", "yapı malzemesi", "betonarme",
        "şantiye", "yapı sektörü", "konut üretimi", "konut projesi", "inşaat projesi",
    ],
    "URBAN_TRANSFORMATION": [
        "urban transformation", "urban renewal", "urban regeneration", "urban planning",
        "zoning plan", "planning permission", "city master plan", "densification",
        "public realm", "kentsel dönüşüm", "kentsel yenileme", "imar planı", "imar durumu",
        "riskli yapı", "rezerv yapı alanı", "şehir planlama", "nazım imar",
    ],
    "KADIKOY": [
        "kadıköy", "kadikoy", "bağdat caddesi", "bagdat caddesi", "fikirtepe",
        "çiftehavuzlar", "göztepe", "selamiçeşme", "caddebostan", "kalamış", "suadiye",
    ],
    "TECHNICAL_AND_LEGAL": [
        "building code", "building regulation", "seismic code", "earthquake regulation",
        "construction legislation", "planning legislation", "technical standard",
        "resmî gazete", "resmi gazete", "yönetmelik", "yönetmeliği", "mevzuat",
        "kanun teklifi", "tebliğ", "genelge", "yapı denetim", "deprem yönetmeliği",
        "imar kanunu", "iskan ruhsatı", "yapı ruhsatı",
    ],
}

WEAK_TERMS = [
    "design", "tasarım", "gallery space", "heritage", "restoration", "restorasyon",
    "concrete", "beton", "steel", "çelik", "engineering", "mühendislik", "housing",
    "konut", "planning", "planlama", "city", "kent", "şehir", "istanbul", "i̇stanbul",
    "biennial pavilion", "exhibition space", "sanat", "kültür", "culture",
]

GEO_TERMS = [
    "türkiye", "turkiye", "turkey", "istanbul", "i̇stanbul", "anadolu", "kadıköy",
    "ankara", "izmir", "marmara",
]

EXCLUDE_TERMS = [
    "crypto", "bitcoin", "ethereum", "nft drop", "memecoin", "token sale",
    "celebrity", "gossip", "reality show", "dizi", "magazin", "sevgilisi", "ünlü oyuncu",
    "transfer", "maç", "futbol", "basketbol", "şampiyonlar ligi", "premier lig", "süper lig",
    "goal", "striker", "fixture", "match report", "world cup", "olympics",
    "cinayet", "tutuklandı", "gözaltına", "operasyonu", "silahlı", "yakalandı",
    "murder", "arrested", "police raid", "shooting", "verdict", "lawsuit against",
    "faiz kararı", "borsa", "döviz kuru", "enflasyon", "hisse", "kredi faizi",
    "sponsored", "advertorial", "promoted content", "advertisement feature",
    "satılık", "kiralık", "fırsat konut", "kampanyası", "indirim", "taksitle",
    "horoscope", "burç", "lottery", "piyango", "yks", "lgs", "sınav sonuç",
    "seçim kampanyası", "milletvekili", "koalisyon", "parti kongresi",
]

CULTURE_CATEGORIES = {"ART", "EXHIBITIONS", "GALLERIES_AND_MUSEUMS"}
BUILT_CATEGORIES = {
    "ARCHITECTURE_AND_DESIGN", "CONSTRUCTION", "URBAN_TRANSFORMATION", "KADIKOY",
    "TECHNICAL_AND_LEGAL",
}

_PUNCT = re.compile(r"[^\w\sğüşıöçİĞÜŞÖÇ]+", re.UNICODE)
_CACHE: dict[tuple[str, bool], re.Pattern] = {}


def normalise(text: str) -> str:
    return _PUNCT.sub(" ", (text or "").lower()).strip()


def _matches(haystack: str, term: str, prefix: bool) -> bool:
    """Word-boundary match. `prefix=True` also matches inflected Turkish endings."""
    key = (term, prefix)
    pattern = _CACHE.get(key)
    if pattern is None:
        tail = "" if prefix else r"\b"
        pattern = re.compile(rf"\b{re.escape(term)}{tail}", re.UNICODE)
        _CACHE[key] = pattern
    return bool(pattern.search(haystack))


def classify(title: str, summary: str, source: dict) -> tuple[str, int, list[str]]:
    """Return (category, strong_hits, matched_strong_terms)."""
    haystack = normalise(f"{title} {summary}")
    scores: dict[str, int] = {}
    matched: list[str] = []
    for category, terms in STRONG_TERMS.items():
        hits = [t for t in terms if _matches(haystack, t, True)]
        if hits:
            scores[category] = len(hits)
            matched.extend(hits)
    if not scores:
        return source["default_category"], 0, []
    if "KADIKOY" in scores:
        category = "KADIKOY"
    elif scores.get("TECHNICAL_AND_LEGAL", 0) >= 2:
        category = "TECHNICAL_AND_LEGAL"
    else:
        category = max(scores, key=lambda k: (scores[k], k == source["default_category"]))
    return category, sum(scores.values()), sorted(set(matched))


def is_excluded(title: str, summary: str) -> str | None:
    haystack = normalise(f"{title} {summary}")
    for term in EXCLUDE_TERMS:
        if _matches(haystack, term, False):
            return term
    return None


def relevance_score(title: str, summary: str, source: dict, age_days: float) -> tuple[int, str, list[str]]:
    category, strong_hits, matched = classify(title, summary, source)
    if not matched:
        return 0, category, []
    haystack = normalise(f"{title} {summary}")
    score = min(strong_hits, 5) * 3
    score += int(source.get("weight", 1))
    score += min(sum(1 for w in WEAK_TERMS if _matches(haystack, w, True)), 4)
    if any(_matches(haystack, g, True) for g in GEO_TERMS):
        score += 2
    if source.get("region") == "TR":
        score += 1
    if age_days <= 3:
        score += 3
    elif age_days <= 10:
        score += 2
    elif age_days <= 30:
        score += 1
    if category in ("KADIKOY", "TECHNICAL_AND_LEGAL"):
        score += 2
    return score, category, matched
