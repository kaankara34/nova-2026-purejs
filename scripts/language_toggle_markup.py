"""Refresh only language controls; preserve branch-authored page content verbatim."""
import re
from pathlib import Path


def enhance_language_switches(html):
    def update(match):
        block = match.group(0)
        if 'class="lang-indicator"' in block:
            return block
        placement = 'menu' if 'lang-switch--menu' in block else 'header'
        if placement == 'menu':
            block = block.replace('data-testid="lang-switch"', 'data-testid="lang-switch-menu"')
        opening_end = block.index('>') + 1
        indicator = ('<span class="lang-indicator" aria-hidden="true" '
                     f'data-testid="lang-{placement}-indicator"></span>')
        block = block[:opening_end] + indicator + block[opening_end:]

        def update_link(link_match):
            link = link_match.group(0)
            lang = re.search(r'\blang="(tr|en)"', link).group(1)
            name = 'Türkçe' if lang == 'tr' else 'English'
            link = link.replace('<a ', f'<a data-testid="lang-{placement}-{lang}" '
                                f'aria-label="{name}" ', 1)
            return link.replace('<span>', f'<span class="lang-label" '
                                f'data-testid="lang-{placement}-{lang}-label">')

        return re.sub(r'<a\b[^>]*>.*?</a>', update_link, block, flags=re.S)

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