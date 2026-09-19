"""Editorial relevance filtering and multi-category classification.

An item is only accepted when it matches at least one STRONG term — an unambiguous signal
for NOVA's editorial fields. WEAK terms never qualify an item on their own; they only add
to the score. Categories are multi-valued: a Kadıköy renewal regulation story can be
KADIKOY + URBAN_TRANSFORMATION + TECHNICAL_AND_LEGAL, but a category is only attached when
the text genuinely supports it.
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
        "construction firm", "contractor", "contractors", "building materials",
        "structural engineering", "housing supply", "residential development",
        "building site", "groundbreaking", "topping out", "site works",
        "inşaat sektörü", "inşaat firması", "müteahhit", "yapı malzemesi", "betonarme",
        "şantiye", "yapı sektörü", "konut üretimi", "konut projesi", "inşaat projesi",
        "temeli atıldı", "teslim edildi", "inşaat maliyeti", "yapım işi", "ihalesi",
    ],
    "URBAN_TRANSFORMATION": [
        "urban transformation", "urban renewal", "urban regeneration", "urban planning",
        "zoning plan", "planning permission", "city master plan", "densification",
        "public realm", "regeneration scheme", "kentsel dönüşüm", "kentsel yenileme",
        "imar planı", "imar durumu", "riskli yapı", "riskli ilan", "rezerv yapı alanı",
        "şehir planlama", "nazım imar", "istanbul yenileniyor", "yenileme projesi",
        "hak sahibi", "hak sahipleri", "yıkım", "dönüşüm projesi",
    ],
    "KADIKOY": [
        "kadıköy", "kadikoy", "bağdat caddesi", "bagdat caddesi", "fikirtepe",
        "çiftehavuzlar", "göztepe", "selamiçeşme", "caddebostan", "kalamış", "suadiye",
        "feneryolu", "acıbadem", "koşuyolu", "erenköy", "bostancı", "fenerbahçe mahallesi",
        "haydarpaşa",
    ],
    "TECHNICAL_AND_LEGAL": [
        "building code", "building regulation", "seismic code", "earthquake regulation",
        "construction legislation", "planning legislation", "technical standard",
        "court ruling", "regulatory amendment", "energy performance regulation",
        "resmî gazete", "resmi gazete", "yönetmelik", "yönetmeliği", "mevzuat",
        "kanun teklifi", "tebliğ", "genelge", "yapı denetim", "deprem yönetmeliği",
        "imar kanunu", "iskan ruhsatı", "yapı ruhsatı", "danıştay", "yargı kararı",
        "enerji kimlik belgesi", "deprem yönetmeliğine",
    ],
}

WEAK_TERMS = [
    "design", "tasarım", "gallery space", "heritage", "restoration", "restorasyon",
    "concrete", "beton", "steel", "çelik", "engineering", "mühendislik", "housing",
    "konut", "planning", "planlama", "city", "kent", "şehir", "istanbul", "i̇stanbul",
    "biennial pavilion", "exhibition space", "sanat", "kültür", "culture", "deprem",
    "earthquake", "sustainability", "sürdürülebilir", "belediye", "municipality",
]

GEO_TERMS = [
    "türkiye", "turkiye", "turkey", "istanbul", "i̇stanbul", "anadolu", "kadıköy",
    "ankara", "izmir", "marmara",
]

# Context a Kadıköy mention must have before the KADIKOY category is attached.
KADIKOY_CONTEXT = [
    "kentsel dönüşüm", "imar", "riskli", "yenileme", "inşaat", "konut", "proje",
    "belediye", "meclis", "yıkım", "ruhsat", "plan", "mimari", "mimarlık", "sergi",
    "müze", "galeri", "kültür", "iskele", "metro", "cadde", "mahalle", "ilçe",
    "urban", "construction", "housing", "exhibition", "museum", "gallery", "district",
    "municipality", "regeneration", "renovation", "architecture",
]

EXCLUDE_TERMS = [
    "crypto", "bitcoin", "ethereum", "nft drop", "memecoin", "token sale",
    "celebrity", "gossip", "reality show", "dizi", "magazin", "sevgilisi", "ünlü oyuncu",
    "transfer", "maç", "futbol", "basketbol", "şampiyonlar ligi", "premier lig", "süper lig",
    "goal", "striker", "fixture", "match report", "world cup", "olympics",
    "cinayet", "tutuklandı", "gözaltına", "operasyonu", "silahlı", "yakalandı",
    "murder", "arrested", "police raid", "shooting", "verdict against",
    "faiz kararı", "borsa", "döviz kuru", "enflasyon oranı", "hisse", "kredi faizi",
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


def classify(title: str, summary: str, source: dict) -> tuple[str, list[str], int, list[str]]:
    """Return (primary category, all categories, strong hit count, matched terms)."""
    haystack = normalise(f"{title} {summary}")
    scores: dict[str, int] = {}
    matched: list[str] = []
    for category, terms in STRONG_TERMS.items():
        hits = [t for t in terms if _matches(haystack, t, True)]
        if hits:
            scores[category] = len(hits)
            matched.extend(hits)

    # A Kadıköy mention alone is not a Kadıköy story: it needs district-level context.
    if "KADIKOY" in scores:
        other = {k for k in scores if k != "KADIKOY"}
        has_context = any(_matches(haystack, term, True) for term in KADIKOY_CONTEXT)
        if not other and not has_context:
            scores.pop("KADIKOY")

    if not scores:
        return source["default_category"], [source["default_category"]], 0, []

    categories = sorted(scores, key=lambda k: (-scores[k], k))
    # Only keep a category with a single weak hit when it is the strongest signal.
    strongest = scores[categories[0]]
    categories = [c for c in categories if scores[c] >= 2 or scores[c] == strongest
                  or c in ("KADIKOY", "TECHNICAL_AND_LEGAL")]
    if "KADIKOY" in scores:
        primary = "KADIKOY"
    elif scores.get("TECHNICAL_AND_LEGAL", 0) >= 2:
        primary = "TECHNICAL_AND_LEGAL"
    else:
        primary = max(scores, key=lambda k: (scores[k], k == source["default_category"]))
    if primary in categories:
        categories.remove(primary)
    categories.insert(0, primary)
    return primary, categories[:4], sum(scores.values()), sorted(set(matched))


def is_excluded(title: str, summary: str) -> str | None:
    haystack = normalise(f"{title} {summary}")
    for term in EXCLUDE_TERMS:
        if _matches(haystack, term, False):
            return term
    return None


def relevance_score(title: str, summary: str, source: dict,
                    age_days: float) -> tuple[int, str, list[str], list[str]]:
    primary, categories, strong_hits, matched = classify(title, summary, source)
    if not matched:
        return 0, primary, categories, []
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
    if primary in ("KADIKOY", "TECHNICAL_AND_LEGAL", "URBAN_TRANSFORMATION", "CONSTRUCTION"):
        score += 2
    return score, primary, categories, matched
