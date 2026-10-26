"""Header logo and preload consistency checks across all 66 public pages."""

import re
import requests
import pytest
from pathlib import Path
from dotenv import dotenv_values


BASE = dotenv_values(Path(__file__).resolve().parents[1] / 'frontend/.env')['REACT_APP_BACKEND_URL'].rstrip('/')

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


ALL_PAGES = [("tr", p) for p in TR_PAGES] + [("en", p) for p in EN_PAGES]


@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    s.headers["User-Agent"] = "pytest-header-assets/1.0"
    return s


@pytest.mark.parametrize("lang,page", ALL_PAGES)
def test_header_logo_and_preload_consistency(session, lang, page):
    url = f"{BASE}/{lang}/{page}"
    r = session.get(url, timeout=20)
    assert r.status_code == 200, f"{url} => {r.status_code}"
    html = r.text

    # Exactly one header logo image with required attrs.
    logos = re.findall(r'<img[^>]*class="logo-img"[^>]*>', html)
    assert len(logos) == 1, f"{url} expected 1 logo-img, found {len(logos)}"
    logo = logos[0]

    src_match = re.search(r'\bsrc="([^"]+)"', logo)
    assert src_match, f"{url} missing logo src"
    logo_src = src_match.group(1)
    assert logo_src in (
        "../media/images/nova-logo-header.webp",
        "../media/images/nova-logo-dark-header.webp",
    ), f"{url} unexpected logo src: {logo_src}"
    assert " " not in logo_src, f"{url} logo src contains space: {logo_src}"

    for key, val in [
        ("width", "768"),
        ("height", "768"),
        ("loading", "eager"),
        ("decoding", "sync"),
        ("fetchpriority", "high"),
        ("data-testid", "header-logo-image"),
    ]:
        assert f'{key}="{val}"' in logo, f"{url} logo missing {key}={val}"

    # Exactly one preload marker and matching href.
    preloads = re.findall(r'<link[^>]*data-nova-header-preload="true"[^>]*>', html)
    assert len(preloads) == 1, f"{url} expected 1 data-nova-header-preload link, found {len(preloads)}"
    preload = preloads[0]
    href = re.search(r'\bhref="([^"]+)"', preload)
    assert href, f"{url} preload missing href"
    assert href.group(1) == logo_src, f"{url} preload href {href.group(1)} != logo src {logo_src}"
    assert 'fetchpriority="high"' in preload, f"{url} preload missing fetchpriority=high"

    # Removed competing PRELOADS should stay removed (runtime image refs may still exist in menu cards).
    assert not re.search(
        r'<link[^>]*rel="preload"[^>]*href="[^">]*(menu-thumbs/|tac-new-render\.webp)[^">]*"',
        html,
    ), f"{url} still contains competing image preload"
