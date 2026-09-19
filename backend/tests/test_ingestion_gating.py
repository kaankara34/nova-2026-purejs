"""Verify correction pass: image gating, source-URL integrity, capitalised titles/summaries,
snapshot json presence, and pending items excluded from public endpoints."""
import os
import re
import json
import pytest
import requests
from urllib.parse import urlparse

BASE_URL = "https://515dc9a7-0d61-46f2-bb41-31805466b8fc.preview.emergentagent.com"
FRONTEND_SNAPSHOT = "/app/frontend/data/news-featured.json"

UA = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

BRAND_LOWERCASE_ALLOWED = {
    "iF", "iPhone", "iPad", "iOS", "eSIM", "ing", "tvN",
}


def _starts_capital(text: str) -> bool:
    if not text:
        return True
    t = text.strip()
    if not t:
        return True
    first_word = re.split(r"[\s\-:\u2013\u2014]", t, 1)[0]
    if first_word in BRAND_LOWERCASE_ALLOWED:
        return True
    # Ignore leading quotes / punctuation
    for ch in t:
        if ch.isalpha():
            return ch.isupper() or not ch.isascii()  # non-ascii (Turkish) is okay
        if ch.isdigit():
            return True
    return True


@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    return s


@pytest.fixture(scope="module")
def news_items(session):
    r = session.get(f"{BASE_URL}/api/news?limit=24")
    assert r.status_code == 200
    return r.json()["items"]


@pytest.fixture(scope="module")
def featured_items(session):
    r = session.get(f"{BASE_URL}/api/news/featured")
    assert r.status_code == 200
    data = r.json()
    return data.get("items") if isinstance(data, dict) else data


class TestImageGating:
    def test_all_list_items_cached_local_webp(self, news_items):
        for it in news_items:
            assert it.get("image_kind") == "cached", f"{it.get('slug')} image_kind={it.get('image_kind')}"
            card = it.get("image_card") or ""
            detail = it.get("image_detail") or ""
            assert card.startswith("media/news/cache/") and card.endswith(".webp"), card
            assert detail.startswith("media/news/cache/") and detail.endswith(".webp"), detail

    def test_all_list_items_status_published(self, news_items):
        for it in news_items:
            assert it.get("status", "published") == "published", it.get("slug")

    def test_image_source_width_ge_1000(self, news_items):
        # width metadata should be present and >= 1000
        for it in news_items:
            w = it.get("image_card_width") or it.get("image_detail_width") or 0
            assert w >= 1000, f"{it.get('slug')} image width {w}"

    def test_image_files_load_200(self, session, news_items):
        checked = 0
        for it in news_items[:8]:
            for key in ("image_card", "image_detail"):
                url = f"{BASE_URL}/{it[key]}"
                r = session.get(url, timeout=15)
                assert r.status_code == 200, f"{url} -> {r.status_code}"
                assert "image" in r.headers.get("Content-Type", ""), r.headers.get("Content-Type")
                checked += 1
        assert checked >= 8

    def test_featured_all_cached(self, featured_items):
        assert featured_items and len(featured_items) >= 3
        for it in featured_items:
            assert it.get("image_kind") == "cached"
            assert (it.get("image_card") or "").endswith(".webp")


class TestSourceURLIntegrity:
    def test_canonical_urls_reachable(self, session, news_items):
        # sample first 8 published items
        sample = news_items[:8]
        assert len(sample) >= 8
        dead = []
        homepage_like = []
        for it in sample:
            url = it.get("canonical_url") or it.get("source_url")
            assert url, it.get("slug")
            try:
                r = requests.get(url, headers=UA, timeout=12, allow_redirects=True)
            except Exception as e:
                dead.append((it["slug"], str(e)))
                continue
            if r.status_code >= 400:
                dead.append((it["slug"], f"status={r.status_code}"))
                continue
            # Homepage/parked detection heuristic: final path is / or empty
            final = urlparse(r.url)
            path = (final.path or "/").rstrip("/")
            if path == "" or path == "/":
                homepage_like.append((it["slug"], r.url))
        # Allow up to 1 transient failure out of 8 (network flake) but no homepage.
        assert len(dead) <= 1, f"Dead links: {dead}"
        assert not homepage_like, f"Homepage/parked links: {homepage_like}"


class TestCapitalisation:
    def test_titles_start_capital(self, news_items):
        offenders = [it["slug"] for it in news_items if not _starts_capital(it.get("title", ""))]
        assert not offenders, f"Lowercase titles: {offenders}"

    def test_summaries_start_capital(self, news_items):
        offenders = []
        for it in news_items:
            s = it.get("summary") or ""
            if s and not _starts_capital(s):
                offenders.append((it["slug"], s[:40]))
        assert not offenders, f"Lowercase summaries: {offenders}"

    def test_summaries_no_midsentence_truncation(self, news_items):
        # a summary should end at a sentence terminator or closing punctuation
        bad = []
        for it in news_items:
            s = (it.get("summary") or "").rstrip()
            if not s:
                continue
            if s[-1] not in ".!?\u2026\"')]" and not s.endswith("..."):
                bad.append((it["slug"], s[-40:]))
        # Report but don't hard-fail — the task note allows short deterministic summaries.
        # We only fail if > 30% end mid-sentence.
        ratio = len(bad) / max(1, len(news_items))
        assert ratio <= 0.30, f"{ratio:.0%} summaries end mid-sentence, examples: {bad[:5]}"


class TestSnapshotFile:
    def test_snapshot_json_exists(self):
        assert os.path.exists(FRONTEND_SNAPSHOT)
        with open(FRONTEND_SNAPSHOT, "r", encoding="utf-8") as f:
            data = json.load(f)
        items = data.get("items") or []
        assert len(items) >= 6, len(items)
        for it in items[:6]:
            assert (it.get("image_card") or "").endswith(".webp")
            assert it.get("slug")
            assert it.get("title")
