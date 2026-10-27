"""Focused EDSAA regression checks: menu insertion, content scope, SEO/schema, routing contract."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest
import requests
from bs4 import BeautifulSoup
from dotenv import dotenv_values


ROOT = Path("/app/frontend")
BASE = dotenv_values(ROOT / ".env")["REACT_APP_BACKEND_URL"].rstrip("/")
BASELINE_ROOT = Path("/tmp/nova-before-edsaa/frontend")

sys.path.insert(0, str(Path("/app/scripts")))
from edsaa_data import CONTENT, IMAGE, ORIGIN, PAGE, PARENT_NAME  # noqa: E402


def _all_pages():
    return sorted((ROOT / "tr").glob("*.html")) + sorted((ROOT / "en").glob("*.html"))


def _lang_pages(lang: str):
    return sorted((ROOT / lang).glob("*.html"))


def _read(path: Path):
    return path.read_text(encoding="utf-8")


def _soup(path: Path):
    return BeautifulSoup(_read(path), "html.parser")


def _remove_edsaa_li(html: str) -> str:
    return re.sub(
        r"<li>\s*<a[^>]*href=\"edsaa\.html\"[^>]*>\s*<span class=\"subitem\">EDSAA</span>\s*</a>\s*</li>",
        "",
        html,
        flags=re.S,
    )


def _canonicalize_for_diff(html: str) -> str:
    html = re.sub(r"\n+", "\n", html)
    html = re.sub(r">\s+<", "><", html)
    return html.strip()


@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    s.headers["User-Agent"] = "pytest-edsaa-regression/1.0"
    return s


def test_menu_has_exactly_one_edsaa_item_in_nova_submenu_on_all_68_pages():
    pages = _all_pages()
    assert len(pages) == 68

    for page in pages:
        soup = _soup(page)
        submenu = soup.select_one("#sideMenu ul.submenu[data-id='nova-konut']")
        assert submenu is not None, f"{page}: missing NOVA submenu"

        links = submenu.select("a[href='edsaa.html']")
        assert len(links) == 1, f"{page}: expected 1 edsaa link, found {len(links)}"

        link = links[0]
        spans = link.select("span.subitem")
        assert len(spans) == 1, f"{page}: EDSAA link must use one span.subitem"
        assert spans[0].get_text(strip=True) == "EDSAA", f"{page}: EDSAA label mismatch"


def test_edsaa_menu_item_is_active_only_on_edsaa_pages():
    for lang in ("tr", "en"):
        edsaa = _soup(ROOT / lang / "edsaa.html")
        current = edsaa.select("#sideMenu ul.submenu[data-id='nova-konut'] a[href='edsaa.html'][aria-current='page']")
        assert len(current) == 1, f"{lang}/edsaa.html: missing aria-current page"


def test_edsaa_pages_have_no_forms_or_register_sections_or_forms_script():
    for lang in ("tr", "en"):
        page = ROOT / lang / "edsaa.html"
        html = _read(page)
        soup = BeautifulSoup(html, "html.parser")

        assert soup.find("form") is None, f"{page}: form element should not exist"
        assert soup.select_one("#register") is None, f"{page}: #register must be removed"
        scripts = [s.get("src", "") for s in soup.select("script[src]")]
        assert not any("nova-forms.js" in src for src in scripts), f"{page}: nova-forms.js should not load"
        assert any(src.endswith("/js/script.js") or src.endswith("../js/script.js") for src in scripts), f"{page}: shared script.js missing"


def test_edsaa_h1_is_present_once_and_appears_before_cookie_banner_in_html_source():
    for lang in ("tr", "en"):
        html = _read(ROOT / lang / "edsaa.html")
        assert html.count("<h1") == 1, f"{lang}/edsaa.html: expected exactly one h1"
        h1_index = html.find("<h1")
        cookie_index = html.find('id="cookieBanner"')
        assert h1_index != -1 and cookie_index != -1 and h1_index < cookie_index, f"{lang}/edsaa.html: h1 must appear before cookie banner"


def test_edsaa_metadata_and_open_graph_match_approved_copy():
    expected_locale = {"tr": "tr_TR", "en": "en_GB"}
    alt_locale = {"tr": "en_GB", "en": "tr_TR"}

    for lang in ("tr", "en"):
        soup = _soup(ROOT / lang / "edsaa.html")
        content = CONTENT[lang]
        canonical = f"{ORIGIN}/{lang}/{PAGE}"

        assert soup.title and soup.title.get_text(strip=True) == content["title"]
        assert soup.select_one("meta[name='description']").get("content") == content["description"]
        assert soup.select_one("link[rel='canonical']").get("href") == canonical
        assert soup.select_one("link[rel='alternate'][hreflang='tr']").get("href") == f"{ORIGIN}/tr/{PAGE}"
        assert soup.select_one("link[rel='alternate'][hreflang='en']").get("href") == f"{ORIGIN}/en/{PAGE}"
        assert soup.select_one("link[rel='alternate'][hreflang='x-default']").get("href") == f"{ORIGIN}/tr/{PAGE}"

        assert soup.select_one("meta[property='og:title']").get("content") == content["title"]
        assert soup.select_one("meta[property='og:description']").get("content") == content["description"]
        assert soup.select_one("meta[property='og:url']").get("content") == canonical
        assert soup.select_one("meta[property='og:locale']").get("content") == expected_locale[lang]
        assert soup.select_one("meta[property='og:locale:alternate']").get("content") == alt_locale[lang]
        assert soup.select_one("meta[property='og:image']").get("content") == f"{ORIGIN}/{IMAGE}"
        assert soup.select_one("meta[property='og:image:width']").get("content") == "1901"
        assert soup.select_one("meta[property='og:image:height']").get("content") == "1070"
        assert soup.select_one("meta[property='og:image:alt']").get("content") == content["alt"]
        assert soup.select_one("meta[name='twitter:title']").get("content") == content["title"]
        assert soup.select_one("meta[name='twitter:description']").get("content") == content["description"]


def test_edsaa_jsonld_is_limited_to_aboutpage_and_organization_contract():
    for lang in ("tr", "en"):
        soup = _soup(ROOT / lang / "edsaa.html")
        node = soup.select_one("script[type='application/ld+json']")
        assert node is not None, f"{lang}/edsaa.html: missing JSON-LD"
        data = json.loads(node.string)
        graph = data.get("@graph") or []
        assert len(graph) == 2
        types = sorted(item.get("@type") for item in graph)
        assert types == ["AboutPage", "Organization"]

        org = next(item for item in graph if item.get("@type") == "Organization")
        assert org.get("name") == "EDSAA"
        assert org.get("url") == f"{ORIGIN}/tr/{PAGE}"
        parent = org.get("parentOrganization", {})
        assert parent.get("name") == PARENT_NAME
        assert parent.get("url") == f"{ORIGIN}/"
        assert "logo" not in org and "video" not in org


def test_canonical_edsaa_pages_are_http_200_and_preview_is_noindex(session):
    for path in ("/tr/edsaa.html", "/en/edsaa.html"):
        r = session.get(BASE + path, timeout=20)
        assert r.status_code == 200, f"{path} -> {r.status_code}"
        robots = (r.headers.get("X-Robots-Tag") or "").replace(" ", "").lower()
        assert robots == "noindex,nofollow", f"{path}: unexpected X-Robots-Tag={robots}"


def test_extensionless_preview_routes_are_not_required_but_must_not_be_advertised(session):
    for path in ("/tr/edsaa", "/en/edsaa"):
        r = session.get(BASE + path, allow_redirects=False, timeout=20)
        assert r.status_code in (301, 404), f"{path}: unexpected status {r.status_code}"

    for page in _all_pages():
        html = _read(page)
        assert 'href="/tr/edsaa"' not in html and 'href="/en/edsaa"' not in html


def test_sitemap_contains_exactly_two_edsaa_urls_with_correct_alternates():
    xml = _read(ROOT / "sitemap.xml")
    assert xml.count("<loc>https://nova.istanbul/tr/edsaa.html</loc>") == 1
    assert xml.count("<loc>https://nova.istanbul/en/edsaa.html</loc>") == 1
    assert "hreflang=\"x-default\" href=\"https://nova.istanbul/tr/edsaa.html\"" in xml


def test_htaccess_has_production_only_extensionless_to_html_rule_and_servejson_has_no_edsaa_aliases():
    htaccess = _read(ROOT / ".htaccess")
    assert "RewriteRule ^(tr|en)/edsaa/?$ /$1/edsaa.html [R=301,L]" in htaccess

    serve_json = json.loads(_read(ROOT / "serve.json"))
    redirects = serve_json.get("redirects", [])
    sources = {entry.get("source") for entry in redirects}
    assert "/tr/edsaa" not in sources and "/en/edsaa" not in sources


def test_original_66_pages_match_pre_edsaa_baseline_except_new_menu_item():
    if not BASELINE_ROOT.exists():
        pytest.skip("No pre-EDSAA baseline available at /tmp/nova-before-edsaa/frontend")

    for lang in ("tr", "en"):
        for page in _lang_pages(lang):
            if page.name == "edsaa.html":
                continue
            baseline_page = BASELINE_ROOT / lang / page.name
            assert baseline_page.exists(), f"Missing baseline file: {baseline_page}"

            current = _canonicalize_for_diff(_remove_edsaa_li(_read(page)))
            baseline = _canonicalize_for_diff(_read(baseline_page))
            assert current == baseline, f"{page}: content changed beyond EDSAA menu insertion"
