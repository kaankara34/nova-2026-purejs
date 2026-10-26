"""Regression checks for language-toggle-only redesign against archived branch snapshot."""

from __future__ import annotations

import re
from pathlib import Path


CURRENT_FRONTEND = Path("/app/frontend")
BASELINE_FRONTEND = Path(
    "/tmp/nova-branch/nova-2026-purejs-3a238f1c6ef793f1cd75583ca6f9bbd7bb6a88f9/frontend"
)

LANG_BLOCK_RE = re.compile(r'<div class="lang-switch\b[^>]*>.*?</div>', re.S)
LANG_ANCHOR_RE = re.compile(r"<a\b[^>]*>")


def _html_pairs():
    pairs = []
    for lang in ("tr", "en"):
        for cur in sorted((CURRENT_FRONTEND / lang).glob("*.html")):
            rel = cur.relative_to(CURRENT_FRONTEND)
            base = BASELINE_FRONTEND / rel
            assert base.exists(), f"Missing baseline file for {rel}"
            pairs.append((rel.as_posix(), cur, base))
    return pairs


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


def test_all_66_pages_exist_against_baseline_snapshot():
    current = sorted((CURRENT_FRONTEND / "tr").glob("*.html")) + sorted(
        (CURRENT_FRONTEND / "en").glob("*.html")
    )
    baseline = sorted((BASELINE_FRONTEND / "tr").glob("*.html")) + sorted(
        (BASELINE_FRONTEND / "en").glob("*.html")
    )
    assert len(current) == 66
    assert len(baseline) == 66


def test_html_changes_are_limited_to_lang_switch_blocks():
    for rel, cur_file, base_file in _html_pairs():
        cur_html = cur_file.read_text(encoding="utf-8")
        base_html = base_file.read_text(encoding="utf-8")
        assert _strip_lang_switch_blocks(cur_html) == _strip_lang_switch_blocks(
            base_html
        ), f"Unexpected non-lang-switch diff in {rel}"


def test_lang_switch_link_semantics_preserved_from_baseline():
    for rel, cur_file, base_file in _html_pairs():
        cur_html = cur_file.read_text(encoding="utf-8")
        base_html = base_file.read_text(encoding="utf-8")

        cur_blocks = _extract_lang_switch_blocks(cur_html)
        base_blocks = _extract_lang_switch_blocks(base_html)

        assert len(cur_blocks) == len(base_blocks) == 2, f"Expected 2 lang-switch blocks in {rel}"

        for idx, (cur_block, base_block) in enumerate(zip(cur_blocks, base_blocks), start=1):
            cur_attrs = _extract_anchor_attrs(cur_block)
            base_attrs = _extract_anchor_attrs(base_block)
            assert cur_attrs == base_attrs, (
                f"Link attrs changed in {rel} block#{idx}. "
                f"Expected href/hreflang/lang/aria-current to remain identical"
            )


def test_shared_css_before_language_selector_block_is_byte_identical():
    marker = "/* ---------- Language selector (TR / EN) ---------- */"
    cur_css = (CURRENT_FRONTEND / "css/styles.css").read_text(encoding="utf-8")
    base_css = (BASELINE_FRONTEND / "css/styles.css").read_text(encoding="utf-8")

    assert marker in cur_css and marker in base_css
    cur_prefix = cur_css.split(marker, 1)[0]
    base_prefix = base_css.split(marker, 1)[0]
    assert cur_prefix == base_prefix


def test_script_keeps_native_language_link_navigation():
    script = (CURRENT_FRONTEND / "js/script.js").read_text(encoding="utf-8")
    # Cosmetic arrival animation helper should exist.
    assert "control.dataset.langFrom" in script
    # No explicit click interception for language options.
    assert not re.search(r"lang-opt.{0,120}addEventListener|addEventListener.{0,120}lang-opt", script, re.S)


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
