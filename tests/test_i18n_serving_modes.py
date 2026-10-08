"""Regression tests for bilingual static pages under two serving roots.

Mode A: repository root served at /app  -> pages under /frontend/{lang}/...
Mode B: frontend folder served as site root -> pages under /{lang}/...
"""

import re
from urllib.parse import urljoin

import pytest
import requests


BASES = {
    "repo_root": "http://127.0.0.1:5501/frontend/",
    "frontend_root": "http://127.0.0.1:5502/",
}


PAGES = {
    "tr_privacy": ("tr/gizlilik-bildirimi.html", "tr"),
    "en_about": ("en/about.html", "en"),
    "tr_design": ("tr/tasarim.html", "tr"),
    "en_design": ("en/design.html", "en"),
    "tr_east_west": ("tr/the-residences-east-west.html", "tr"),
    "en_east_west": ("en/the-residences-east-west.html", "en"),
}

EW_PLAN_IMAGES = [
    "media/images/ew/plans/east-3plus1.webp",
    "media/images/ew/plans/east-4plus1.webp",
    "media/images/ew/plans/east-duplex-lower.webp",
    "media/images/ew/plans/east-duplex-upper.webp",
    "media/images/ew/plans/west-3plus1.webp",
    "media/images/ew/plans/west-4plus1.webp",
    "media/images/ew/plans/west-duplex-lower.webp",
    "media/images/ew/plans/west-duplex-upper.webp",
]

DESIGN_TEXTURES = [
    "media/images/design/tex-walnut.webp",
    "media/images/design/tex-walnut-n.webp",
    "media/images/design/tex-walnut-r.webp",
    "media/images/design/tex-pietra.webp",
    "media/images/design/tex-pietra-n.webp",
    "media/images/design/tex-pietra-r.webp",
    "media/images/design/tex-bronze.webp",
    "media/images/design/tex-bronze-n.webp",
    "media/images/design/tex-bronze-r.webp",
    "media/images/design/tex-leather.webp",
    "media/images/design/tex-leather-n.webp",
    "media/images/design/tex-leather-r.webp",
]


@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    s.headers["User-Agent"] = "pytest-i18n-serving-modes/1.0"
    return s


def _get(session, base, rel_path):
    response = session.get(urljoin(base, rel_path), timeout=20)
    return response


def _extract_local_assets(html):
    refs = []
    refs += re.findall(r'(?:href|src|poster)="((?:\.\./|/)?(?:css|js|media)/[^"#?]+)', html)
    refs += re.findall(r'url\(["\']?((?:\.\./|/)?(?:css|js|media)/[^)"\']+)', html)
    for srcset in re.findall(r'srcset="([^"]+)"', html):
        for token in srcset.split(','):
            candidate = token.strip().split()[0] if token.strip() else ""
            if re.match(r'(?:\.\./|/)?(?:css|js|media)/', candidate):
                refs.append(candidate)
    return sorted(set(refs))


@pytest.mark.parametrize("base_key,base", BASES.items())
@pytest.mark.parametrize("page_key", ["tr_privacy", "en_about"])
def test_core_pages_open_styled_under_both_roots(session, base_key, base, page_key):
    rel_path, lang = PAGES[page_key]
    r = _get(session, base, rel_path)
    assert r.status_code == 200, f"{base_key} {rel_path} -> {r.status_code}"
    assert f'lang="{lang}"' in r.text

    assets = _extract_local_assets(r.text)
    assert assets, f"No local assets detected for {base_key} {rel_path}"
    for asset in assets[:30]:
        a = session.get(urljoin(urljoin(base, rel_path), asset), timeout=20)
        assert a.status_code == 200, f"{base_key} {rel_path} missing asset {asset}: {a.status_code}"


@pytest.mark.parametrize("base_key,base", BASES.items())
@pytest.mark.parametrize("page_key", ["tr_privacy", "en_about", "tr_design", "en_design"])
def test_lang_switch_goes_to_counterpart_page(session, base_key, base, page_key):
    rel_path, lang = PAGES[page_key]
    opposite = "en" if lang == "tr" else "tr"
    r = _get(session, base, rel_path)
    assert r.status_code == 200

    block = re.search(r'data-testid="lang-switch".*?</div>', r.text, re.S)
    assert block, f"lang-switch block missing on {base_key} {rel_path}"
    hrefs = re.findall(r'href="([^"]+)"', block.group(0))
    targets = [h for h in hrefs if f"/{opposite}/" in h or h.startswith(f"../{opposite}/")]
    assert targets, f"No {opposite} target found in lang-switch for {base_key} {rel_path}"

    target_url = urljoin(urljoin(base, rel_path), targets[0])
    t = session.get(target_url, timeout=20)
    assert t.status_code == 200, f"lang-switch target broken: {target_url}"
    assert f'lang="{opposite}"' in t.text


def test_no_root_dependent_links_remain_in_generated_pages():
    for folder in ("/app/frontend/en", "/app/frontend/tr"):
        pages = sorted(
            p for p in __import__("pathlib").Path(folder).glob("*.html")
            if p.is_file()
        )
        assert len(pages) == 33, f"Expected 33 pages in {folder}, found {len(pages)}"

        for page in pages:
            html = page.read_text(encoding="utf-8")
            tag = page.as_posix()
            assert not re.search(r'(?:href|src|poster)="/(?:css|js|media)/', html), tag
            assert not re.search(r'url\(["\']?/(?:css|js|media)/', html), tag

            for srcset in re.findall(r'srcset="([^"]+)"', html):
                for token in srcset.split(','):
                    candidate = token.strip().split()[0] if token.strip() else ""
                    if re.match(r'(?:css|js|media)/', candidate):
                        candidate = "/" + candidate
                    assert not candidate.startswith("/css/")
                    assert not candidate.startswith("/js/")
                    assert not candidate.startswith("/media/")

            body = html.split("</head>", 1)[-1]
            assert not re.search(r'href="/(?:tr|en)/[^"#?]+\.html', body), tag


@pytest.mark.parametrize("base_key,base", BASES.items())
@pytest.mark.parametrize("asset", EW_PLAN_IMAGES + DESIGN_TEXTURES)
def test_ew_and_design_assets_resolve_under_both_roots(session, base_key, base, asset):
    r = session.get(urljoin(base, asset), timeout=20)
    assert r.status_code == 200, f"{base_key} missing {asset}: {r.status_code}"
