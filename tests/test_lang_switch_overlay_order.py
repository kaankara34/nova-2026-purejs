"""Regression checks for header language-switch order and overlay styling."""

from __future__ import annotations

import re
from pathlib import Path
from bs4 import BeautifulSoup


FRONTEND = Path("/app/frontend")
CSS_PATH = FRONTEND / "css" / "styles.css"
JS_FILES = [
    FRONTEND / "js" / "language-toggle.js",
    FRONTEND / "js" / "language-toggle-gesture.js",
]


def _all_pages():
    pages = []
    for lang in ("tr", "en"):
        pages.extend(sorted((FRONTEND / lang).glob("*.html")))
    return pages


def test_total_page_count_is_stable():
    pages = _all_pages()
    assert len(pages) == 68


def test_header_action_order_register_icons_language_in_all_pages():
    for page in _all_pages():
        soup = BeautifulSoup(page.read_text(encoding="utf-8"), 'html.parser')
        actions = soup.select_one('.header-actions')
        assert actions, f"missing header-actions in {page.name}"
        children = actions.find_all(recursive=False)
        register, icons, language = [actions.select_one(selector) for selector in ('.register', '.icon-links', '.lang-switch')]
        assert all((register, icons, language)), f"Missing header action in {page.name}"
        assert children.index(register) < children.index(icons) < children.index(language), page.name


def test_only_header_language_switch_exists_per_page():
    for page in _all_pages():
        html = page.read_text(encoding="utf-8")
        assert 'data-testid="lang-switch"' in html, f"Missing header switch in {page.name}"
        assert 'data-testid="lang-switch-menu"' not in html, f"Removed menu switch returned in {page.name}"


def test_overlay_and_knob_css_values_are_preserved():
    css = CSS_PATH.read_text(encoding="utf-8")
    # Overlay pane values
    assert ".lang-rail::before" in css
    assert "backdrop-filter: blur(var(--lang-flag-blur, .35px));" in css
    assert "-webkit-backdrop-filter: blur(var(--lang-flag-blur, .35px));" in css
    assert "pointer-events: none;" in css
    assert "z-index: 0;" in css
    assert "rgba(255, 255, 255, .13)" in css
    # Knob is above overlay and remains opaque
    assert ".lang-knob" in css
    assert "z-index: 1;" in css
    assert "background-color: var(--lang-knob-fill, #ececec);" in css
    assert "backdrop-filter: none;" in css


def test_toggle_js_files_unchanged_for_navigation_and_gesture_contract():
    toggle_js = JS_FILES[0].read_text(encoding="utf-8")
    gesture_js = JS_FILES[1].read_text(encoding="utf-8")
    assert "window.location.assign(links[target].href)" in toggle_js
    assert "if (Math.abs(dx) >= 4) pointer.moved = true;" in gesture_js
    assert "actions.commit(progress >= .5 ? 1 : 0);" in gesture_js
