#!/usr/bin/env python3
"""Add a correctly-sized srcset variant to the fixed-width gallery/card grids.

Every one of these grids renders at the SAME CSS pixel width at 390px, 768px,
1024px, 1440px, 1920px and 2560px viewports (measured), so `sizes` can be an
exact px value and the browser can never pick a candidate that is too small.
One variant at 2x the CSS width is generated; the original file stays untouched
and remains what the lightbox and `el.src` read, so full-screen quality is
unchanged. Visitors at DPR 1 and DPR 2 get the right-sized file instead of the
full-resolution master.
"""
import math
import re
from pathlib import Path

from PIL import Image

ROOT = Path('/app/frontend')

# (page, wrapper class, css px width the image always renders at)
GRIDS = [
    ('projects.html', 'pj-card-img', 421),
    ('mercan-bosphorus.html', 'mercan-manifesto-img', 611),
    ('mercan-bosphorus.html', 'mercan-features-img', 409),
    ('bahar-residence.html', 'bahar-manifesto-img', 404),
    ('marti-residence.html', 'marti-manifesto-img', 404),
    ('marti-residence.html', 'marti-features-img', 626),
    ('mehtap-residence.html', 'mehtap-manifesto-img', 404),
    ('mehtap-residence.html', 'mehtap-features-img', 626),
    ('east-west.html', 'ew-amenity-img', 347),
]

made, total_old, total_new = {}, 0, 0
changed_pages = []

for page, cls, css_w in GRIDS:
    f = ROOT / page
    html = f.read_text(encoding='utf-8')
    original = html
    target_w = int(math.ceil(css_w * 2 / 50.0)) * 50
    out, pos = [], 0
    for m in re.finditer(r'class="[^"]*\b' + re.escape(cls) + r'\b[^"]*"', html):
        img = re.search(r'<img\b[^>]*>', html[m.end():m.end() + 1200])
        if not img:
            continue
        tag = img.group(0)
        start = m.end() + img.start()
        if 'srcset' in tag:
            continue
        src = re.search(r'src="([^"]+)"', tag)
        if not src:
            continue
        rel = src.group(1).lstrip('./')
        path = ROOT / rel
        if not path.exists():
            continue
        im = Image.open(path)
        if im.width < target_w * 1.15:
            continue
        var_rel = f'{rel.rsplit(".", 1)[0]}-{target_w}.{rel.rsplit(".", 1)[1]}'
        var_path = ROOT / var_rel
        if not var_path.exists():
            h = round(im.height * target_w / im.width)
            small = im.resize((target_w, h), Image.LANCZOS)
            if var_path.suffix.lower() == '.webp':
                small.save(var_path, 'WEBP', quality=86, method=6)
            else:
                small.convert('RGB').save(var_path, 'JPEG', quality=86,
                                          optimize=True, progressive=True)
        made[var_rel] = (path.stat().st_size // 1024, var_path.stat().st_size // 1024)
        new_tag = tag[:-1].rstrip()
        if new_tag.endswith('/'):
            new_tag = new_tag[:-1].rstrip()
        new_tag += (f' srcset="./{var_rel} {target_w}w, ./{rel} {im.width}w"'
                    f' sizes="{css_w}px" />')
        out.append(html[pos:start])
        out.append(new_tag)
        pos = start + len(tag)
    out.append(html[pos:])
    html = ''.join(out)
    if html != original:
        f.write_text(html, encoding='utf-8')
        changed_pages.append(page)

for k, (o, n) in sorted(made.items()):
    total_old += o
    total_new += n
print(f'{len(made)} variants generated for {len(set(changed_pages))} pages')
print(f'served bytes for DPR<=2 visitors: {total_old} KB -> {total_new} KB '
      f'({round((1 - total_new / total_old) * 100) if total_old else 0}% less)')
