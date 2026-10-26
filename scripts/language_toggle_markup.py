"""Refresh only language controls; preserve branch-authored page content verbatim."""
import re
from pathlib import Path


def enhance_language_switches(html):
    def update(match):
        block = match.group(0)
        if 'data-language-toggle="slide-v2"' in block:
            return block
        placement = 'menu' if 'lang-switch--menu' in block else 'header'
        links, flags = {}, {}
        current = 'tr'
        for link in re.findall(r'<a\b[^>]*>.*?</a>', block, re.S):
            lang = re.search(r'\blang="(tr|en)"', link).group(1)
            if 'is-active' in link:
                current = lang
            flags[lang] = re.search(r'<svg\b.*?</svg>', link, re.S).group(0)
            opening = link[:link.index('>') + 1]
            name = 'Türkçe' if lang == 'tr' else 'English'
            if 'data-testid=' not in opening:
                opening = opening.replace('<a ', f'<a data-testid="lang-{placement}-{lang}" ', 1)
            if 'aria-label=' not in opening:
                opening = opening.replace('<a ', f'<a aria-label="{name}" ', 1)
            links[lang] = (opening + f'<span class="lang-label" '
                           f'data-testid="lang-{placement}-{lang}-label">{lang.upper()}</span></a>')

        opening = block[:block.index('>') + 1]
        opening = opening[:-1] + f' data-language-toggle="slide-v2" data-language="{current}">'
        if placement == 'menu':
            opening = opening.replace('data-testid="lang-switch"', 'data-testid="lang-switch-menu"')
        checked = 'true' if current == 'en' else 'false'
        label = 'İngilizce' if current == 'tr' else 'English'
        track = (f'<button class="lang-toggle" type="button" role="switch" '
                 f'aria-label="{label}" aria-checked="{checked}" disabled '
                 f'data-testid="lang-{placement}-toggle">'
                 f'<span class="lang-rail" aria-hidden="true" data-testid="lang-{placement}-rail">')
        for lang in ('en', 'tr'):
            track += (f'<span class="lang-flag-window" data-flag="{lang}" '
                      f'data-testid="lang-{placement}-flag-{lang}">{flags[lang]}</span>')
        track += (f'<span class="lang-knob" data-testid="lang-{placement}-knob"></span>'
                  '</span></button>')
        return opening + links['tr'] + track + links['en'] + '</div>'

    return re.sub(r'<div class="lang-switch\b[^>]*>.*?</div>', update, html, flags=re.S)


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