"""Iter68 frontend contract checks: 66-page chrome parity, language switch placement, favicon links."""

from __future__ import annotations

from pathlib import Path

import pytest
import requests
from bs4 import BeautifulSoup
from dotenv import dotenv_values


ROOT = Path("/app/frontend")
BASE = dotenv_values(ROOT / ".env")["REACT_APP_BACKEND_URL"].rstrip("/")
ICON_SET = [
    ("icon", "../favicon.ico"),
    ("icon", "../favicon-32.png"),
    ("icon", "../favicon-192.png"),
    ("apple-touch-icon", "../apple-touch-icon.png"),
]


def _pages_by_lang(lang: str):
    return sorted((ROOT / lang).glob("*.html"))


def _all_pages():
    return _pages_by_lang("tr") + _pages_by_lang("en")


def _soup(path: Path):
    return BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")


def _menu_signature(soup: BeautifulSoup):
    items = []
    for node in soup.select("#sideMenu .menu-list > li .menu-link"):
        label = " ".join(node.get_text(" ", strip=True).split())
        href = node.get("href", "")
        items.append((label, href))
    return items


def _footer_menu_signature(soup: BeautifulSoup):
    return [
        (" ".join(a.get_text(" ", strip=True).split()), a.get("href", ""))
        for a in soup.select(".footer-menu-links a")
    ]


def _discover_signature(soup: BeautifulSoup):
    out = []
    for a in soup.select(".footer-discover-row a"):
        name = " ".join((a.select_one(".fd-name") or a).get_text(" ", strip=True).split())
        meta = " ".join((a.select_one(".fd-meta") or a).get_text(" ", strip=True).split())
        out.append((name, meta, a.get("href", "")))
    return out


def _utility_signature(soup: BeautifulSoup):
    out = []
    for a in soup.select("#utilityBar .utility-left a"):
        out.append((" ".join(a.get_text(" ", strip=True).split()), a.get("href", "")))
    return out


def test_total_page_count_includes_two_edsaa_pages():
    assert len(_all_pages()) == 68
    assert all((ROOT / lang / 'edsaa.html').is_file() for lang in ('tr', 'en'))


# language-switch and side-menu contract checks
def test_header_has_exactly_one_lang_switch_and_side_menu_has_zero_for_all_pages():
    for page in _all_pages():
        soup = _soup(page)
        header_switches = soup.select('[data-testid="lang-switch"]')
        menu_switches = soup.select("#sideMenu .lang-switch")
        assert len(header_switches) == 1, f"{page.name}: expected exactly one header language switch"
        assert len(menu_switches) == 0, f"{page.name}: side-menu language switch must not exist"


# canonical content propagation checks from index per language
@pytest.mark.parametrize("lang", ["tr", "en"])
def test_canonical_index_chrome_content_matches_other_pages(lang):
    canonical = _soup(ROOT / lang / "index.html")
    can_menu = _menu_signature(canonical)
    can_footer_menu = _footer_menu_signature(canonical)
    can_discover = _discover_signature(canonical)
    can_utility = _utility_signature(canonical)

    assert len(can_footer_menu) == 10, f"{lang}/index.html expected 10 footer menu links"
    assert len(can_discover) == 4, f"{lang}/index.html expected 4 discover-row links"

    for page in _pages_by_lang(lang):
        soup = _soup(page)
        assert _menu_signature(soup) == can_menu, f"{page.name}: side-menu content mismatch vs canonical index"
        assert _footer_menu_signature(soup) == can_footer_menu, f"{page.name}: footer menu mismatch vs canonical index"
        assert _discover_signature(soup) == can_discover, f"{page.name}: footer discover mismatch vs canonical index"
        assert _utility_signature(soup) == can_utility, f"{page.name}: utility bar content mismatch vs canonical index"


# favicon references + publicly served asset checks
def test_all_pages_use_local_favicon_links_and_assets_resolve_publicly():
    session = requests.Session()
    checked_assets = set()

    for page in _all_pages():
        soup = _soup(page)
        rel = page.relative_to(ROOT).as_posix()
        head_links = soup.select("head link")

        for rel_name, href in ICON_SET:
            assert any(
                link.get("href") == href and rel_name in (link.get("rel") or [])
                for link in head_links
            ), f"{rel}: missing favicon link {rel_name} -> {href}"

        assert "flatMedia" not in page.read_text(encoding="utf-8"), f"{rel}: legacy flatMedia path found"

        for _rel_name, href in ICON_SET:
            asset = href.replace("../", "")
            if asset in checked_assets:
                continue
            checked_assets.add(asset)
            url = f"{BASE}/{asset}"
            res = session.get(url, timeout=20)
            assert res.status_code == 200, f"{url} -> {res.status_code}"
            if asset.endswith(".ico"):
                assert "image" in res.headers.get("content-type", ""), f"{url}: unexpected content-type"
            else:
                assert "png" in res.headers.get("content-type", ""), f"{url}: unexpected content-type"


def test_east_west_progress_contract_in_source_files():
    js = (ROOT / "js/east-west-feature.js").read_text(encoding="utf-8")
    css = (ROOT / "css/styles.css").read_text(encoding="utf-8")

    assert "iterations: Infinity" in js
    assert "window.addEventListener('focus', restore)" in js
    assert "window.addEventListener('blur'" not in js
    assert "onfinish" not in js

    assert ".ew-progress-top { top: 0; left: 0; width: 100%; height: 3px;" in css
    assert ".ew-progress-right { top: 0; right: 0; width: 3px; height: 100%;" in css
    assert ".ew-progress-glint" in css and "width: 5px; height: 5px;" in css
