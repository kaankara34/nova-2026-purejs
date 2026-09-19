"""Allowlisted newsroom sources.

Every entry was checked with a real HTTP request from this environment (last verified
2026-06). Publishers with no lawful / working RSS, Atom or server-rendered listing are
recorded in DISABLED_SOURCES with the observed reason and are never requested. Only
hostnames in ALLOWED_HOSTS are ever fetched.
"""

CATEGORIES = [
    "ART",
    "EXHIBITIONS",
    "GALLERIES_AND_MUSEUMS",
    "ARCHITECTURE_AND_DESIGN",
    "CONSTRUCTION",
    "URBAN_TRANSFORMATION",
    "KADIKOY",
    "TECHNICAL_AND_LEGAL",
]

# Editorial coverage target per public category inside the rolling window.
CATEGORY_MIN_ITEMS = 3

# key, publisher, feed url, language, region, default category, editorial area, weight
SOURCES = [
    # ---------------------------------------------------------------- culture
    {
        "key": "hyperallergic",
        "name": "Hyperallergic",
        "url": "https://hyperallergic.com/feed/",
        "language": "en", "region": "INTERNATIONAL",
        "default_category": "ART", "area": "CULTURE", "weight": 3, "enabled": True,
    },
    {
        "key": "guardian-art",
        "name": "The Guardian — Art & Design",
        "url": "https://www.theguardian.com/artanddesign/rss",
        "language": "en", "region": "INTERNATIONAL",
        "default_category": "ART", "area": "CULTURE", "weight": 4, "enabled": True,
    },
    {
        "key": "artnet-news",
        "name": "Artnet News",
        "url": "https://news.artnet.com/feed",
        "language": "en", "region": "INTERNATIONAL",
        "default_category": "ART", "area": "CULTURE", "weight": 3, "enabled": True,
    },
    {
        "key": "artnews",
        "name": "ARTnews",
        "url": "https://www.artnews.com/feed/",
        "language": "en", "region": "INTERNATIONAL",
        "default_category": "ART", "area": "CULTURE", "weight": 3, "enabled": True,
    },
    {
        "key": "artforum",
        "name": "Artforum",
        "url": "https://www.artforum.com/feed/",
        "language": "en", "region": "INTERNATIONAL",
        "default_category": "ART", "area": "CULTURE", "weight": 3, "enabled": True,
    },
    {
        "key": "colossal",
        "name": "Colossal",
        "url": "https://www.thisiscolossal.com/feed/",
        "language": "en", "region": "INTERNATIONAL",
        "default_category": "ART", "area": "CULTURE", "weight": 2, "enabled": True,
    },
    {
        "key": "smithsonian-art",
        "name": "Smithsonian Magazine — Arts & Culture",
        "url": "https://www.smithsonianmag.com/rss/arts-culture/",
        "language": "en", "region": "INTERNATIONAL",
        "default_category": "GALLERIES_AND_MUSEUMS", "area": "CULTURE", "weight": 4,
        "enabled": True,
    },
    {
        "key": "labiennale",
        "name": "La Biennale di Venezia",
        "url": "https://www.labiennale.org/en/rss.xml",
        "language": "en", "region": "INTERNATIONAL",
        "default_category": "EXHIBITIONS", "area": "CULTURE", "weight": 5, "enabled": True,
    },
    {
        "key": "trt-kultur",
        "name": "TRT Haber — Kültür Sanat",
        "url": "https://www.trthaber.com/kultur_sanat_articles.rss",
        "language": "tr", "region": "TR",
        "default_category": "EXHIBITIONS", "area": "CULTURE", "weight": 4, "enabled": True,
    },
    {
        "key": "aa-kultur",
        "name": "Anadolu Ajansı — Kültür Sanat",
        "url": "https://www.aa.com.tr/tr/rss/default?cat=kultur",
        "language": "tr", "region": "TR",
        "default_category": "EXHIBITIONS", "area": "CULTURE", "weight": 4, "enabled": True,
    },

    # ---------------------------------------------------------------- built environment
    {
        "key": "dezeen",
        "name": "Dezeen",
        "url": "https://www.dezeen.com/feed/",
        "language": "en", "region": "INTERNATIONAL",
        "default_category": "ARCHITECTURE_AND_DESIGN", "area": "BUILT", "weight": 3,
        "enabled": True,
    },
    {
        "key": "dezeen-architecture",
        "name": "Dezeen — Architecture",
        "url": "https://www.dezeen.com/architecture/feed/",
        "language": "en", "region": "INTERNATIONAL",
        "default_category": "ARCHITECTURE_AND_DESIGN", "area": "BUILT", "weight": 3,
        "enabled": True,
    },
    {
        "key": "designboom",
        "name": "designboom",
        "url": "https://www.designboom.com/feed/",
        "language": "en", "region": "INTERNATIONAL",
        "default_category": "ARCHITECTURE_AND_DESIGN", "area": "BUILT", "weight": 2,
        "enabled": True,
    },
    {
        "key": "archdaily",
        "name": "ArchDaily",
        "url": "https://feeds.feedburner.com/Archdaily",
        "language": "en", "region": "INTERNATIONAL",
        "default_category": "ARCHITECTURE_AND_DESIGN", "area": "BUILT", "weight": 3,
        "enabled": True,
    },
    {
        "key": "architects-journal",
        "name": "The Architects' Journal",
        "url": "https://www.architectsjournal.co.uk/feed",
        "language": "en", "region": "INTERNATIONAL",
        "default_category": "ARCHITECTURE_AND_DESIGN", "area": "BUILT", "weight": 5,
        "enabled": True,
    },
    {
        "key": "construction-dive",
        "name": "Construction Dive",
        "url": "https://www.constructiondive.com/feeds/news/",
        "language": "en", "region": "INTERNATIONAL",
        "default_category": "CONSTRUCTION", "area": "BUILT", "weight": 6, "enabled": True,
    },
    {
        "key": "guardian-cities",
        "name": "The Guardian — Cities",
        "url": "https://www.theguardian.com/cities/rss",
        "language": "en", "region": "INTERNATIONAL",
        "default_category": "URBAN_TRANSFORMATION", "area": "BUILT", "weight": 4,
        "enabled": True,
    },
    {
        "key": "arkitera",
        "name": "Arkitera",
        "url": "https://www.arkitera.com/feed/",
        "language": "tr", "region": "TR",
        "default_category": "ARCHITECTURE_AND_DESIGN", "area": "BUILT", "weight": 4,
        "enabled": True,
    },
    {
        "key": "arkitektuel",
        "name": "Arkitektüel",
        "url": "https://www.arkitektuel.com/feed/",
        "language": "tr", "region": "TR",
        "default_category": "ARCHITECTURE_AND_DESIGN", "area": "BUILT", "weight": 2,
        "enabled": True,
    },
    {
        "key": "yapi-dergisi",
        "name": "YAPI Dergisi",
        "url": "https://www.yapidergisi.com/feed",
        "language": "tr", "region": "TR",
        "default_category": "CONSTRUCTION", "area": "BUILT", "weight": 6, "enabled": True,
    },
    {
        "key": "gayrimenkulhaber",
        "name": "Gayrimenkul Haber",
        "url": "https://www.gayrimenkulhaber.com/feed",
        "language": "tr", "region": "TR",
        "default_category": "CONSTRUCTION", "area": "BUILT", "weight": 4, "enabled": True,
    },
    {
        "key": "tmmob",
        "name": "TMMOB",
        "url": "https://www.tmmob.org.tr/rss.xml",
        "language": "tr", "region": "TR",
        "default_category": "TECHNICAL_AND_LEGAL", "area": "BUILT", "weight": 6,
        "enabled": True,
    },
    {
        "key": "kentsel-strateji",
        "name": "Kentsel Strateji",
        "url": "https://kentselstrateji.com/feed/",
        "language": "tr", "region": "TR",
        "default_category": "URBAN_TRANSFORMATION", "area": "BUILT", "weight": 5,
        "enabled": True,
    },
    {
        "key": "dunya-sektorler",
        "name": "Dünya — Sektörler",
        "url": "https://www.dunya.com/rss?sektorler",
        "language": "tr", "region": "TR",
        "default_category": "CONSTRUCTION", "area": "BUILT", "weight": 5, "enabled": True,
    },
    {
        "key": "ekonomim",
        "name": "Ekonomim",
        "url": "https://www.ekonomim.com/rss",
        "language": "tr", "region": "TR",
        "default_category": "CONSTRUCTION", "area": "BUILT", "weight": 4, "enabled": True,
    },
    {
        "key": "bloomberght",
        "name": "Bloomberg HT",
        "url": "https://www.bloomberght.com/rss",
        "language": "tr", "region": "TR",
        "default_category": "CONSTRUCTION", "area": "BUILT", "weight": 4, "enabled": True,
    },
    {
        "key": "trt-ekonomi",
        "name": "TRT Haber — Ekonomi",
        "url": "https://www.trthaber.com/ekonomi_articles.rss",
        "language": "tr", "region": "TR",
        "default_category": "CONSTRUCTION", "area": "BUILT", "weight": 4, "enabled": True,
    },
    {
        "key": "aa-guncel",
        "name": "Anadolu Ajansı — Güncel",
        "url": "https://www.aa.com.tr/tr/rss/default?cat=guncel",
        "language": "tr", "region": "TR",
        "default_category": "URBAN_TRANSFORMATION", "area": "BUILT", "weight": 4,
        "enabled": True,
    },
    {
        "key": "aa-ekonomi",
        "name": "Anadolu Ajansı — Ekonomi",
        "url": "https://www.aa.com.tr/tr/rss/default?cat=ekonomi",
        "language": "tr", "region": "TR",
        "default_category": "CONSTRUCTION", "area": "BUILT", "weight": 4, "enabled": True,
    },
]

# Institutional sites with no feed but a server-rendered, robots-permitted news listing.
# Only the listing page is read; each article is then fetched once for title, date and text.
CRAWL_TARGETS = [
    {
        "key": "kiptas",
        "name": "KİPTAŞ (İstanbul Büyükşehir Belediyesi)",
        "list_urls": ["https://www.kiptas.istanbul/haberler",
                      "https://www.kiptas.istanbul/haberler?page=2"],
        "link_pattern": r"^/haberler/[a-z0-9\-]{12,}$",
        "language": "tr", "region": "TR",
        "default_category": "URBAN_TRANSFORMATION", "area": "BUILT", "weight": 7,
        "enabled": True,
    },
]

# Publishers checked and left disabled — reason observed from this environment (2026-06).
DISABLED_SOURCES = [
    {"name": "Resmî Gazete", "reason": "host unreachable from the application network (connect error); no public RSS/Atom"},
    {"name": "Çevre, Şehircilik ve İklim Değişikliği Bakanlığı", "reason": "host unreachable (connect timeout)"},
    {"name": "Kentsel Dönüşüm Başkanlığı", "reason": "host unreachable (connect error)"},
    {"name": "İstanbul Büyükşehir Belediyesi (ibb.istanbul)", "reason": "no feed; news listing paths return 404, content served from a client-rendered app"},
    {"name": "Kadıköy Belediyesi", "reason": "no feed; listing is client-rendered (no article links or dates in the served HTML)"},
    {"name": "AFAD", "reason": "no RSS endpoint (404)"},
    {"name": "TÜİK", "reason": "bulletin RSS path returns HTML, not a feed"},
    {"name": "İnşaat Mühendisleri Odası", "reason": "rss.xml returns 404"},
    {"name": "Mimarlar Odası", "reason": "feed host unreachable from this environment"},
    {"name": "Türkiye İMSAD", "reason": "RSS path returns HTML"},
    {"name": "Türkiye Müteahhitler Birliği", "reason": "no RSS endpoint (404)"},
    {"name": "GYODER / KONUTDER", "reason": "no RSS endpoint (404)"},
    {"name": "Mimarizm / Arkiv", "reason": "automated access blocked (403)"},
    {"name": "yapi.com.tr", "reason": "automated access blocked (Cloudflare 403)"},
    {"name": "Emlak Kulisi", "reason": "RSS is readable but every article page returns 403, so no source link can be verified"},
    {"name": "Sözcü — Emlak", "reason": "feed works but contains no items matching NOVA's editorial fields"},
    {"name": "Gazete Kadıköy", "reason": "no RSS/Atom endpoint; article list is client-rendered, so no dated links are served"},
    {"name": "İstanbul Yenileniyor (İBB)", "reason": "robots.txt content signals declare ai-input=no; excluded on the publisher's terms"},
    {"name": "Engineering News-Record", "reason": "advertised RSS path returns 404"},
    {"name": "RIBA (architecture.com)", "reason": "no working RSS endpoint (404)"},
    {"name": "BD Online", "reason": "feed endpoint rejects GET (405)"},
    {"name": "Archinect / Next City / Hürriyet Emlak / İKSV", "reason": "endpoint returns HTML, not a parseable feed"},
    {"name": "The Art Newspaper", "reason": "advertised feed path returns 404"},
    {"name": "Apollo Magazine", "reason": "feed returns HTTP 500"},
    {"name": "Bloomberg CityLab", "reason": "feed path returns 404"},
    {"name": "Frieze", "reason": "automated access blocked (403)"},
    {"name": "Reuters", "reason": "public RSS discontinued; syndication requires a licence"},
    {"name": "İstanbul Modern / SALT / Pera / Arter / Sakıp Sabancı / Borusan Contemporary", "reason": "no public RSS, Atom or syndication endpoint"},
    {"name": "Tate / MoMA / Louvre / Centre Pompidou / Art Basel", "reason": "no public feed endpoint available"},
]

ALLOWED_HOSTS = sorted({
    "hyperallergic.com",
    "www.theguardian.com",
    "news.artnet.com",
    "www.artnews.com",
    "www.artforum.com",
    "www.thisiscolossal.com",
    "www.smithsonianmag.com",
    "www.labiennale.org",
    "www.trthaber.com",
    "www.aa.com.tr",
    "www.dezeen.com",
    "www.designboom.com",
    "feeds.feedburner.com",
    "www.archdaily.com",
    "www.architectsjournal.co.uk",
    "www.constructiondive.com",
    "www.arkitera.com",
    "www.arkitektuel.com",
    "www.yapidergisi.com",
    "www.tmmob.org.tr",
    "kentselstrateji.com",
    "www.gayrimenkulhaber.com",
    "gayrimenkulhaber.com",
    "yapidergisi.com",
    "www.dunya.com",
    "www.ekonomim.com",
    "www.bloomberght.com",
    "www.ntv.com.tr",
    "www.kiptas.istanbul",
    "kiptas.istanbul",
})


def enabled_sources():
    return [s for s in SOURCES if s.get("enabled")]


def enabled_crawl_targets():
    return [t for t in CRAWL_TARGETS if t.get("enabled")]
