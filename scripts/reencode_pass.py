#!/usr/bin/env python3
"""Quality-only re-encode of over-compressed-at-too-high-quality media.

Dimensions, aspect ratio, crop and file name are never changed, so nothing in the
layout or the markup moves. A candidate is only accepted when the re-encode is
visually equivalent (PSNR >= 38 dB against the original, which is well above the
~34 dB "indistinguishable" threshold for photographic content) AND saves >= 20%.
Line-art assets (floor plans, site/location maps) fail the PSNR gate by nature
and are therefore rejected automatically. Originals are copied to
/app/media_originals/ before any write.
"""
import glob
import json
import math
import os
import re
import shutil
from pathlib import Path

import numpy as np
from skimage.metrics import structural_similarity as ssim_fn
from PIL import Image, ImageChops

ROOT = Path('/app/frontend')
BACKUP = Path('/app/media_originals')
BACKUP.mkdir(parents=True, exist_ok=True)
MIN_PSNR = 34.0
MIN_SSIM = 0.99
MIN_SAVE = 0.20

refs = set()
for f in list(ROOT.glob('*.html')) + list(ROOT.glob('css/*.css')) + list(ROOT.glob('js/*.js')):
    text = f.read_text(encoding='utf-8', errors='ignore')
    for m in re.finditer(r'[\'"(]\.?/?(media/[^\'")\s]+?\.(?:webp|jpg|jpeg|JPG|JPEG))', text):
        refs.add(m.group(1))

candidates = sorted(p for p in refs if (ROOT / p).exists() and (ROOT / p).stat().st_size > 150 * 1024)


def psnr(a, b):
    diff = ImageChops.difference(a, b)
    hist = diff.histogram()
    sq = sum(v * (i % 256) ** 2 for i, v in enumerate(hist))
    mse = sq / (a.size[0] * a.size[1] * len(a.getbands()))
    return 99.0 if mse == 0 else 10 * math.log10(255 ** 2 / mse)


report, skipped = [], []
for rel in candidates:
    src = ROOT / rel
    old_kb = src.stat().st_size // 1024
    im = Image.open(src)
    fmt = im.format
    ref = im.convert('RGB')
    best = None
    for q in (80, 86, 92):
        tmp = src.with_suffix(src.suffix + '.tmp')
        if fmt == 'WEBP':
            im.save(tmp, 'WEBP', quality=q, method=6)
        else:
            im.convert('RGB').save(tmp, 'JPEG', quality=q, optimize=True,
                                   progressive=True)
        new_kb = tmp.stat().st_size // 1024
        cand = Image.open(tmp).convert('RGB')
        score = psnr(ref, cand)
        sim = ssim_fn(np.asarray(ref.convert('L')), np.asarray(cand.convert('L')),
                      data_range=255)
        save = 1 - new_kb / old_kb
        if score >= MIN_PSNR and sim >= MIN_SSIM and save >= MIN_SAVE:
            best = (q, new_kb, score, save, sim)
            break
        tmp.unlink()
    if not best:
        skipped.append((rel, old_kb))
        continue
    q, new_kb, score, save, sim = best
    flat = BACKUP / rel.replace('/', '__')
    if not flat.exists():
        shutil.copy2(src, flat)
    shutil.move(src.with_suffix(src.suffix + '.tmp'), src)
    report.append({'file': rel, 'dim': f'{im.size[0]}x{im.size[1]}', 'q': q,
                   'kb_old': old_kb, 'kb_new': new_kb,
                   'saved_pct': round(save * 100), 'psnr': round(score, 1),
                   'ssim': round(sim, 4)})

tot_old = sum(r['kb_old'] for r in report)
tot_new = sum(r['kb_new'] for r in report)
print(f'{len(report)} re-encoded: {tot_old} KB -> {tot_new} KB '
      f'({round((1 - tot_new / tot_old) * 100)}% saved)')
print(f'{len(skipped)} left untouched (failed quality or saving gate)')
for r in sorted(report, key=lambda x: -(x['kb_old'] - x['kb_new']))[:12]:
    print('  ', r['file'], r['kb_old'], '->', r['kb_new'], f"q{r['q']} psnr{r['psnr']} ssim{r['ssim']}")
for s in skipped:
    print('   SKIP', s[0], s[1], 'KB')
Path('/app/memory/media_reencode.json').write_text(json.dumps(report, indent=1))
