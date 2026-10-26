"""Targeted header/media updates, without regenerating branch-authored page content."""
import re
from pathlib import Path


def optimize_runtime_markup(html):
    logo_source = None

    def logo(match):
        nonlocal logo_source
        tag = match.group()
        src = re.search(r'\bsrc="([^"]+)"', tag)
        if not src:
            return tag
        logo_source = re.sub(r'(nova-logo(?:-dark)?)(?:-header)?\.(?:png|webp)$', r'\1-header.webp', src[1])
        tag = tag.replace(src[1], logo_source)
        tag = re.sub(r'\s+/\s+(?=[a-zA-Z])', ' ', tag).rstrip('>').rstrip('/').rstrip()
        for key, value in [('width', '768'), ('height', '768'), ('loading', 'eager'),
                           ('decoding', 'sync'), ('fetchpriority', 'high'), ('data-testid', 'header-logo-image')]:
            tag = re.sub(rf'\s{key}="[^"]*"', '', tag)
            tag += f' {key}="{value}"'
        return tag + ' />'

    html = re.sub(r'<img\b[^>]*\bclass="logo-img"[^>]*>', logo, html)
    if logo_source and 'data-nova-header-preload' not in html:
        preload = (f'\n  <link rel="preload" as="image" href="{logo_source}" type="image/webp" '
                   'fetchpriority="high" data-nova-header-preload="true" />')
        html = re.sub(r'(<meta\s+charset="[^"]+"\s*/?>)', lambda m: m[0] + preload, html, count=1)
    # Offscreen menu thumbnails must not compete with the actual header logo/hero poster.
    html = re.sub(r'^[ \t]*<link\b[^>]*rel="preload"[^>]*href="[^"\n]*(?:menu-thumbs/|tac-new-render\.webp)[^"\n]*"[^>]*>\s*\n', '', html, flags=re.M)

    def inline_script(match):
        return '' if "document.getElementById('heroVideo')" in match[0] else match[0]

    html = re.sub(r'<script>.*?</script>', inline_script, html, flags=re.S)
    if 'id="heroVideoSource"' in html and 'data-hero-rendition' not in html:
        pattern = r'(<source\s+id="heroVideoSource"\s+src="([^"]*)hero-nova-1280\.mp4"[^>]*>)'
        def sources(match):
            prefix = match[2]
            responsive = '\n'.join(f'<source src="{prefix}hero-nova-{size}.mp4" type="video/mp4" media="{media}" data-hero-rendition="{size}" />'
                                   for size, media in [('960', '(max-width: 640px)'), ('1280', '(max-width: 1100px)'), ('1600', '(min-width: 1101px)')])
            return responsive + '\n        ' + match[1]
        html = re.sub(pattern, sources, html)

    def video(match):
        tag = match[0]
        if not re.search(r'class="(?:hero-video|ew-hero-video|ana-hero-video)"', tag):
            return tag
        if 'data-hero-video' not in tag:
            tag = tag[:-1] + ' data-hero-video="true">'
        if 'data-testid=' not in tag:
            name = re.search(r'id="([^"]+)"', tag)
            key = re.sub(r'(?<=[a-z0-9])(?=[A-Z])', '-', name[1]).lower() if name else 'background'
            tag = tag[:-1] + f' data-testid="hero-video-{key}">'
        tag = re.sub(r'data-testid="(hero-video-[^"]+)"',
                     lambda m: 'data-testid="' + re.sub(r'(?<=[a-z0-9])(?=[A-Z])', '-', m[1]).lower() + '"', tag)
        return tag
    return re.sub(r'<video\b[^>]*>', video, html, flags=re.S)


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1] / 'frontend'
    changed = 0
    for lang in ('en', 'tr'):
        for path in (root / lang).glob('*.html'):
            old = path.read_text(encoding='utf-8')
            new = optimize_runtime_markup(old)
            if old != new:
                path.write_text(new, encoding='utf-8')
                changed += 1
    print(f'Targeted runtime/header markup updated in {changed} pages.')