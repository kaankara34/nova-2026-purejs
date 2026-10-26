"""Regression checks for language-toggle redesign against baseline snapshot/fixture."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


CURRENT_FRONTEND = Path("/app/frontend")
BASELINE_CANDIDATE = Path("/tmp/nova-toggle-before-gesture/frontend")
FIXTURE_PATH = Path("/app/tests/fixtures/lang_toggle_baseline_fixture.json")

LANG_BLOCK_RE = re.compile(r'<div class="lang-switch\b[^>]*>.*?</div>', re.S)
LANG_ANCHOR_RE = re.compile(r"<a\b[^>]*>")


def _strip_lang_switch_blocks(html: str) -> str:
    return LANG_BLOCK_RE.sub("", html)


def _extract_lang_switch_blocks(html: str):
    return LANG_BLOCK_RE.findall(html)


def _extract_anchor_attrs(block: str):
    attrs = []
    for anchor in LANG_ANCHOR_RE.findall(block):
        href = re.search(r'href="([^"]+)"', anchor)
        hreflang = re.search(r'hreflang="([^"]+)"', anchor)
        lang = re.search(r'\blang="([^"]+)"', anchor)
        aria_current = re.search(r'aria-current="([^"]+)"', anchor)
        attrs.append(
            {
                "href": href.group(1) if href else None,
                "hreflang": hreflang.group(1) if hreflang else None,
                "lang": lang.group(1) if lang else None,
                "aria_current": aria_current.group(1) if aria_current else None,
            }
        )
    return attrs


def _load_fixture():
    assert FIXTURE_PATH.exists(), f"Missing fixture: {FIXTURE_PATH}"
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _html_pairs():
    pairs = []
    baseline_exists = BASELINE_CANDIDATE.exists()
    for lang in ("tr", "en"):
        for cur in sorted((CURRENT_FRONTEND / lang).glob("*.html")):
            rel = cur.relative_to(CURRENT_FRONTEND)
            base = BASELINE_CANDIDATE / rel if baseline_exists else None
            if baseline_exists:
                assert base.exists(), f"Missing baseline file for {rel}"
            pairs.append((rel.as_posix(), cur, base))
    return pairs


def test_all_66_pages_exist_against_baseline_snapshot_or_fixture():
    current = sorted((CURRENT_FRONTEND / "tr").glob("*.html")) + sorted(
        (CURRENT_FRONTEND / "en").glob("*.html")
    )
    assert len(current) == 66

    fixture = _load_fixture()
    assert fixture["total_pages"] == 66

    if BASELINE_CANDIDATE.exists():
        baseline = sorted((BASELINE_CANDIDATE / "tr").glob("*.html")) + sorted(
            (BASELINE_CANDIDATE / "en").glob("*.html")
        )
        assert len(baseline) == 66


def test_html_changes_are_limited_to_lang_switch_blocks():
    fixture = _load_fixture()
    for rel, cur_file, base_file in _html_pairs():
        cur_html = cur_file.read_text(encoding="utf-8")
        cur_stripped = _strip_lang_switch_blocks(cur_html)

        if base_file is not None:
            base_html = base_file.read_text(encoding="utf-8")
            assert cur_stripped == _strip_lang_switch_blocks(
                base_html
            ), f"Unexpected non-lang-switch diff in {rel}"
        else:
            digest = hashlib.sha256(cur_stripped.encode("utf-8")).hexdigest()
            assert digest == fixture["stripped_sha256"][rel], f"Hash mismatch in {rel}"


def test_lang_switch_link_semantics_preserved_from_baseline():
    fixture = _load_fixture()
    for rel, cur_file, base_file in _html_pairs():
        cur_html = cur_file.read_text(encoding="utf-8")
        cur_blocks = _extract_lang_switch_blocks(cur_html)

        if base_file is not None:
            base_html = base_file.read_text(encoding="utf-8")
            base_blocks = _extract_lang_switch_blocks(base_html)
            assert len(cur_blocks) == len(base_blocks) == 2, f"Expected 2 lang-switch blocks in {rel}"
            for idx, (cur_block, base_block) in enumerate(zip(cur_blocks, base_blocks), start=1):
                cur_attrs = _extract_anchor_attrs(cur_block)
                base_attrs = _extract_anchor_attrs(base_block)
                assert cur_attrs == base_attrs, (
                    f"Link attrs changed in {rel} block#{idx}. "
                    "Expected href/hreflang/lang/aria-current to remain identical"
                )
        else:
            expected = fixture["lang_link_attrs"][rel]
            assert len(cur_blocks) == len(expected) == 2, f"Expected 2 lang-switch blocks in {rel}"
            for idx, cur_block in enumerate(cur_blocks, start=1):
                assert _extract_anchor_attrs(cur_block) == expected[idx - 1], (
                    f"Link attrs changed in {rel} block#{idx}. "
                    "Expected href/hreflang/lang/aria-current to remain identical"
                )


def test_shared_css_before_language_selector_block_is_byte_identical():
    marker = "/* ---------- Language selector (TR / EN) ---------- */"
    cur_css = (CURRENT_FRONTEND / "css/styles.css").read_text(encoding="utf-8")
    cur_prefix = cur_css.split(marker, 1)[0]

    if BASELINE_CANDIDATE.exists():
        base_css = (BASELINE_CANDIDATE / "css/styles.css").read_text(encoding="utf-8")
        base_prefix = base_css.split(marker, 1)[0]
        assert cur_prefix == base_prefix
    else:
        fixture = _load_fixture()
        digest = hashlib.sha256(cur_prefix.encode("utf-8")).hexdigest()
        assert digest == fixture["css_prefix_sha256"]


def test_language_toggle_enhancement_uses_native_anchor_hrefs():
    script = (CURRENT_FRONTEND / "js/script.js").read_text(encoding="utf-8")
    toggle_controller = (CURRENT_FRONTEND / "js/language-toggle.js").read_text(encoding="utf-8")

    assert "import('./language-toggle.js')" in script
    assert "window.location.assign(links[target].href)" in toggle_controller
    # Links may cancel pending gesture visual state, but native destination remains authoritative.
    assert "links.forEach(link => link.addEventListener('click', () => cancelGesture()))" in toggle_controller
    assert "lang-indicator" not in (CURRENT_FRONTEND / "css/styles.css").read_text(encoding="utf-8")


def test_active_language_link_matches_document_lang():
    html_lang_re = re.compile(r"<html[^>]*\blang=\"(tr|en)\"", re.I)
    for rel, cur_file, _base_file in _html_pairs():
        html = cur_file.read_text(encoding="utf-8")
        m = html_lang_re.search(html)
        assert m, f"Missing html lang in {rel}"
        doc_lang = m.group(1).lower()

        blocks = _extract_lang_switch_blocks(html)
        assert len(blocks) == 2, f"Expected 2 lang-switch blocks in {rel}"
        for idx, block in enumerate(blocks, start=1):
            active = re.search(
                r'<a\b[^>]*class="[^"]*\bis-active\b[^"]*"[^>]*\blang="(tr|en)"[^>]*\baria-current="true"',
                block,
                re.I,
            )
            assert active, f"Missing active link with aria-current in {rel} block#{idx}"
            assert active.group(1).lower() == doc_lang, (
                f"Active lang mismatch in {rel} block#{idx}: "
                f"active={active.group(1)} doc={doc_lang}"
            )
