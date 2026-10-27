"""Refresh only language controls; preserve branch-authored page content verbatim."""
import re
from pathlib import Path


def place_header_switch_last(html):
    """Move the same control after contact icons; preserve every other byte and tab order."""
    header = re.search(r'<div class="header-actions"[^>]*>', html)
    if not header:
        return html
    depth = 1
    for tag in re.finditer(r'</?div\b[^>]*>', html[header.end():]):
        depth += -1 if tag.group().startswith('</') else 1
        if depth:
            continue
        end = header.end() + tag.start()
        inner = html[header.end():end]
        control = re.search(r'<div\b[^>]*\bclass="lang-switch\b[^>]*>.*?</div>', inner, re.S)
        if not control or 'class="icon-links"' not in inner[control.end():]:
            return html
        # Moving only the matched bytes also preserves original surrounding whitespace.
        reordered = inner[:control.start()] + inner[control.end():] + control.group()
        return html[:header.end()] + reordered + html[end:]
    return html


def enhance_language_switches(html):
    def update(match):
        block = match.group(0)
        def deduplicate_current(link):
            tag = link.group(0)
            attributes = list(re.finditer(r'\saria-current="[^"]*"', tag))
            for duplicate in reversed(attributes[1:]):
                tag = tag[:duplicate.start()] + tag[duplicate.end():]
            return tag
        block = re.sub(r'<a\b[^>]*>', deduplicate_current, block)
        if 'lang-switch--menu' in block:
            return ''  # Only the header owns a language control, at every viewport.
        if 'data-flag-source="wikimedia"' in block:
            return block
        placement = 'menu' if 'lang-switch--menu' in block else 'header'
        links = {}
        current = 'tr'
        for link in re.findall(r'<a\b[^>]*>.*?</a>', block, re.S):
            lang = re.search(r'\blang="(tr|en)"', link).group(1)
            if 'is-active' in link:
                current = lang
            opening = link[:link.index('>') + 1]
            name = 'Türkçe' if lang == 'tr' else 'English'
            if 'data-testid=' not in opening:
                opening = opening.replace('<a ', f'<a data-testid="lang-{placement}-{lang}" ', 1)
            if 'aria-label=' not in opening:
                opening = opening.replace('<a ', f'<a aria-label="{name}" ', 1)
            links[lang] = (opening + f'<span class="lang-label" '
                           f'data-testid="lang-{placement}-{lang}-label">{lang.upper()}</span></a>')

        opening = block[:block.index('>') + 1]
        opening = re.sub(r'\sdata-(?:language-toggle|language|flag-language|flag-source)="[^"]*"', '', opening)
        opening = (opening[:-1] + f' data-language-toggle="slide-v2" data-language="{current}" '
                   f'data-flag-source="wikimedia" data-flag-language="{current}">')
        if placement == 'menu':
            opening = opening.replace('data-testid="lang-switch"', 'data-testid="lang-switch-menu"')
        checked = 'true' if current == 'en' else 'false'
        label = 'İngilizce' if current == 'tr' else 'English'
        track = (f'<button class="lang-toggle" type="button" role="switch" '
                 f'aria-label="{label}" aria-checked="{checked}" disabled '
                 f'data-testid="lang-{placement}-toggle">'
                 f'<span class="lang-rail" aria-hidden="true" data-testid="lang-{placement}-rail">')
        track += (f'<span class="lang-knob" data-testid="lang-{placement}-knob"></span>'
                  '</span></button>')
        return opening + links['tr'] + track + links['en'] + '</div>'

    updated = re.sub(r'<div\b[^>]*\bclass="lang-switch\b[^>]*>.*?</div>', update, html, flags=re.S)
    return place_header_switch_last(updated)


if __name__ == '__main__':
    frontend = Path(__file__).resolve().parents[1] / 'frontend'
    count = 0
    for lang in ('en', 'tr'):
        for path in sorted((frontend / lang).glob('*.html')):
            original = path.read_text(encoding='utf-8')
            updated = enhance_language_switches(original)
            if updated != original:
                path.write_text(updated, encoding='utf-8')
                count += 1
    print(f'Language controls updated in {count} pages; other markup preserved.')