#!/usr/bin/env python3
"""Safe, non-visual performance pass over every HTML page.

1. Below-the-fold <img> tags that have no `loading` attribute (browser default =
   eager) get `loading="lazy" decoding="async"`. Images inside heroes, sliders,
   carousels and swipe tracks are skipped, because those can be off-screen in the
   layout while still needing to be painted immediately.
2. The three side-menu project thumbnails live in a closed off-canvas drawer but
   were marked `loading="eager" fetchpriority="high"`, competing with each page's
   real LCP image. They become lazy (no visual change: the drawer is closed).
3. Hero videos: the `<link rel="preload" as="video" fetchpriority="high">` hints
   pulled 8-24 MB at highest priority before the poster/LCP could paint, and
   `preload="auto"` downloaded the whole file. Poster + autoplay behaviour is
   unchanged; only the download strategy becomes `metadata`.
4. `preconnect` hints for the CDNs a page actually uses (gsap / leaflet / dar
   global images) so the TLS handshake is not serialised after HTML parsing.
"""
import re
from pathlib import Path

ROOT = Path('/app/frontend')
SKIP_CTX = ('slide', 'slider', 'carousel', 'swipe', 'hero', 'ew-plans-lightbox',
            'pp-lightbox', 'logo-mark')
IMG_RE = re.compile(r'<img\b[^>]*>', re.I)

report = []

for f in sorted(ROOT.glob('*.html')):
    html = f.read_text(encoding='utf-8')
    original = html
    lazified = 0

    # ---------- 1. lazy-load images that default to eager ----------
    out = []
    pos = 0
    for m in IMG_RE.finditer(html):
        tag = m.group(0)
        out.append(html[pos:m.start()])
        pos = m.end()
        if 'loading=' in tag:
            out.append(tag)
            continue
        prefix = html[:m.start()]
        anchor = max(prefix.rfind('<section'), prefix.rfind('<figure'),
                     prefix.rfind('<header'), prefix.rfind('<aside'))
        ctx = (prefix[anchor:] + tag).lower()
        if any(k in ctx for k in SKIP_CTX):
            out.append(tag)
            continue
        new = tag[:-1].rstrip()
        if new.endswith('/'):
            new = new[:-1].rstrip()
        extra = ' loading="lazy"'
        if 'decoding=' not in tag:
            extra += ' decoding="async"'
        out.append(new + extra + ' />')
        lazified += 1
    out.append(html[pos:])
    html = ''.join(out)

    # ---------- 2. side-menu thumbnails are in a closed drawer ----------
    menu_thumbs = 0
    a, b = html.find('<aside class="side-menu"'), html.find('</aside>')
    if a != -1 and b != -1:
        block = html[a:b]
        new_block, n1 = re.subn(r'loading="eager" decoding="async" fetchpriority="high"',
                                'loading="lazy" decoding="async"', block)
        new_block, n2 = re.subn(r'loading="eager" decoding="async"',
                                'loading="lazy" decoding="async"', new_block)
        menu_thumbs = n1 + n2
        html = html[:a] + new_block + html[b:]

    # ---------- 3. hero video download strategy ----------
    vid_preload = len(re.findall(r'<link rel="preload" as="video"[^>]*>\s*', html))
    html = re.sub(r'\s*<link rel="preload" as="video"[^>]*>', '', html)
    auto = len(re.findall(r'preload="auto"', html))
    html = html.replace('preload="auto"', 'preload="metadata"')
    # the homepage collaboration film sits far below the fold and is started by
    # js/script.js when it scrolls into view, so it needs no data up front
    html = html.replace('id="collabVid" playsinline loop muted autoplay preload="metadata"',
                        'id="collabVid" playsinline loop muted autoplay preload="none"')

    # ---------- 4. preconnect only for CDNs the page really uses ----------
    hints = []
    if 'cdn.jsdelivr.net' in html and 'preconnect" href="https://cdn.jsdelivr.net' not in html:
        hints.append('  <link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin />')
    if 'unpkg.com' in html and 'preconnect" href="https://unpkg.com' not in html:
        hints.append('  <link rel="preconnect" href="https://unpkg.com" crossorigin />')
    if 'cdn.darglobal.co.uk' in html and 'preconnect" href="https://cdn.darglobal.co.uk' not in html:
        hints.append('  <link rel="preconnect" href="https://cdn.darglobal.co.uk" crossorigin />')
    if hints:
        marker = '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />'
        if marker in html:
            html = html.replace(marker, marker + '\n' + '\n'.join(hints), 1)
        else:
            hints = []

    if html != original:
        f.write_text(html, encoding='utf-8')
    report.append((f.name, lazified, menu_thumbs, vid_preload, auto, len(hints)))

print('{:32} {:>4} {:>6} {:>8} {:>7} {:>6}'.format('file', 'lazy', 'menu', 'vid-pre', 'auto', 'hints'))
for row in report:
    if any(row[1:]):
        print('{:32} {:>4} {:>6} {:>8} {:>7} {:>6}'.format(*row))
