"""Static site HTTP & content tests for TR/EN bilingual NOVA site."""
import re
import requests
import pytest

BASE = "https://darg-clone-1.preview.emergentagent.com"

TR_PAGES = [
    "index.html","projeler.html","hakkimizda.html","iletisim.html","organizasyon.html",
    "partnerler.html","tasarim.html","muhendislik.html","leed.html","build-beyond-living.html",
    "medya.html","kariyer.html","santiye-muduru-mimar.html","bildirim.html",
    "gizlilik-bildirimi.html","cerez-bildirimi.html","etik-ilkeler.html","aday-aydinlatma-metni.html",
    "the-residences-east-west.html","the-apartments-tac.html","the-apartments-ana.html",
    "finance-nova.html","mercan-bosphorus.html","nisbetiye-on.html","falcon-plaza.html",
    "falcon-lojistik-merkezi.html","gebze-osb-yonetim-binasi.html","konelsis-merkezi.html",
    "marti-residence.html","bahar-residence.html","dogan-residence.html","mehtap-residence.html",
    "haber.html",
]

EN_PAGES = [
    "index.html","projects.html","about.html","contact.html","team.html","partners.html",
    "design.html","construction.html","leed.html","build-beyond-living.html","newsroom.html",
    "careers.html","construction-site-manager-architect.html","speak-up.html",
    "privacy-notice.html","cookie-notice.html","ethical-principles.html","applicant-privacy-notice.html",
    "the-residences-east-west.html","the-apartments-tac.html","the-apartments-ana.html",
    "finance-nova.html","mercan-bosphorus.html","nisbetiye-on.html","falcon-plaza.html",
    "falcon-logistic.html","gebze-osb-management.html","konelsis-center.html",
    "marti-residence.html","bahar-residence.html","dogan-residence.html","mehtap-residence.html",
    "news-detail.html",
]

# Legacy EN root -> /en/ redirects
LEGACY_REDIRECTS = {
    "/projects.html": "/en/projects.html",
    "/about.html": "/en/about.html",
    "/contact.html": "/en/contact.html",
    "/careers.html": "/en/careers.html",
    "/design.html": "/en/design.html",
}

@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    s.headers["User-Agent"] = "pytest-static-test/1.0"
    return s

def test_root_redirects_to_tr(session):
    r = session.get(BASE + "/", allow_redirects=False)
    assert r.status_code in (301, 302)
    assert "/tr" in r.headers.get("location", "")

@pytest.mark.parametrize("src,dst", LEGACY_REDIRECTS.items())
def test_legacy_redirects(session, src, dst):
    r = session.get(BASE + src, allow_redirects=False)
    assert r.status_code in (301, 302), f"{src} status={r.status_code}"
    assert dst in r.headers.get("location", ""), f"{src} -> {r.headers.get('location')}"

@pytest.mark.parametrize("page", TR_PAGES)
def test_tr_page_loads(session, page):
    r = session.get(f"{BASE}/tr/{page}")
    assert r.status_code == 200, f"/tr/{page} => {r.status_code}"
    assert 'lang="tr"' in r.text, f"/tr/{page} missing lang=tr"
    # ensure lang-switch exists
    assert 'data-testid="lang-switch"' in r.text, f"/tr/{page} missing lang-switch"

@pytest.mark.parametrize("page", EN_PAGES)
def test_en_page_loads(session, page):
    r = session.get(f"{BASE}/en/{page}")
    assert r.status_code == 200, f"/en/{page} => {r.status_code}"
    assert 'lang="en"' in r.text, f"/en/{page} missing lang=en"
    assert 'data-testid="lang-switch"' in r.text, f"/en/{page} missing lang-switch"

# Hreflang checks
@pytest.mark.parametrize("page", TR_PAGES[:5])
def test_tr_has_hreflang_en(session, page):
    r = session.get(f"{BASE}/tr/{page}")
    assert re.search(r'hreflang="en"', r.text), f"/tr/{page} missing hreflang en"
    assert re.search(r'hreflang="tr"', r.text), f"/tr/{page} missing hreflang tr"

# Ana hero poster path (recently fixed)
def test_ana_hero_poster_tr(session):
    r = session.get(f"{BASE}/tr/the-apartments-ana.html")
    assert "media/images/ana/ana-render.webp" in r.text

def test_ana_hero_poster_en(session):
    r = session.get(f"{BASE}/en/the-apartments-ana.html")
    assert "media/images/ana/ana-render.webp" in r.text

# Verify the hero poster asset itself resolves
def test_ana_poster_asset(session):
    r = session.head(f"{BASE}/media/images/ana/ana-render.webp", allow_redirects=True)
    assert r.status_code == 200

# No runtime translation / no JSON fetch
@pytest.mark.parametrize("page", ["index.html","projeler.html","tasarim.html","the-apartments-ana.html"])
def test_tr_no_runtime_translation(session, page):
    r = session.get(f"{BASE}/tr/{page}")
    txt = r.text.lower()
    # should not fetch i18n JSON
    assert "i18n_tr" not in txt
    assert "translations.json" not in txt
    assert "/i18n/" not in txt

# In-language internal links
def test_tr_links_stay_in_tr(session):
    r = session.get(f"{BASE}/tr/index.html")
    # find all href values pointing to html pages
    hrefs = re.findall(r'href="([^"#?]+\.html)"', r.text)
    cross = [h for h in hrefs if h.startswith("/en/") or re.match(r"^(?!/tr/)(?!https?://)/[a-z-]+\.html$", h)]
    # It's OK for hreflang alt to point to /en/ - exclude via link rel. Check more precisely.
    # Re-parse excluding hreflang alternate links
    body = r.text.split("</head>",1)[-1]
    body_hrefs = re.findall(r'href="([^"#?]+\.html)"', body)
    bad = [h for h in body_hrefs if h.startswith("/en/")]
    # The lang-switch EN link in header is in body - allow it
    # Filter: only flag non-lang-switch EN links. Simple heuristic: at most a couple of /en/ links (lang switches).
    assert len(bad) <= 3, f"TR homepage body has too many /en/ links: {bad}"

def test_en_links_stay_in_en(session):
    r = session.get(f"{BASE}/en/index.html")
    body = r.text.split("</head>",1)[-1]
    body_hrefs = re.findall(r'href="([^"#?]+\.html)"', body)
    bad = [h for h in body_hrefs if h.startswith("/tr/")]
    assert len(bad) <= 3, f"EN homepage body has too many /tr/ links: {bad}"

# Lang-switch targets correct cross-language page
LANG_PAIRS_TR_TO_EN = {
    "/tr/projeler.html": "/en/projects.html",
    "/tr/muhendislik.html": "/en/construction.html",
    "/tr/the-apartments-tac.html": "/en/the-apartments-tac.html",
    "/tr/kariyer.html": "/en/careers.html",
    "/tr/bildirim.html": "/en/speak-up.html",
    "/tr/tasarim.html": "/en/design.html",
}

@pytest.mark.parametrize("tr_url,en_url", LANG_PAIRS_TR_TO_EN.items())
def test_lang_switch_tr_to_en(session, tr_url, en_url):
    r = session.get(BASE + tr_url)
    # lang-switch block
    m = re.search(r'data-testid="lang-switch".*?</div>', r.text, re.S)
    assert m, f"{tr_url} missing lang-switch block"
    block = m.group(0)
    assert en_url in block, f"{tr_url} lang-switch does not point to {en_url}. Found: {block[:400]}"

LANG_PAIRS_EN_TO_TR = {
    "/en/build-beyond-living.html": "/tr/build-beyond-living.html",
    "/en/careers.html": "/tr/kariyer.html",
    "/en/projects.html": "/tr/projeler.html",
    "/en/construction.html": "/tr/muhendislik.html",
}

@pytest.mark.parametrize("en_url,tr_url", LANG_PAIRS_EN_TO_TR.items())
def test_lang_switch_en_to_tr(session, en_url, tr_url):
    r = session.get(BASE + en_url)
    m = re.search(r'data-testid="lang-switch".*?</div>', r.text, re.S)
    assert m, f"{en_url} missing lang-switch block"
    block = m.group(0)
    assert tr_url in block, f"{en_url} lang-switch does not point to {tr_url}"

# Canonical/hreflang alignment
def test_canonical_tr(session):
    r = session.get(f"{BASE}/tr/projeler.html")
    assert '<link rel="canonical"' in r.text
    assert "/tr/projeler.html" in re.search(r'<link rel="canonical"[^>]*href="([^"]+)"', r.text).group(1)

# Sitemap
def test_sitemap_exists(session):
    r = session.get(f"{BASE}/sitemap.xml")
    assert r.status_code == 200
    assert "/tr/" in r.text and "/en/" in r.text
