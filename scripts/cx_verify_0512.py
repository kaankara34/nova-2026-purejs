#!/usr/bin/env python3
"""Verify that every line of the approved sections 05-12 copy exists verbatim
in construction.html (whitespace / case / dash normalised)."""
import html
import pathlib
import re
import sys

APPROVED = pathlib.Path('/app/scripts/cx_approved_0512.txt').read_text(encoding='utf-8')
src = pathlib.Path('/app/frontend/construction.html').read_text(encoding='utf-8')

start = src.index('<!-- ===================== REINFORCEMENT ===================== -->')
end = src.index('<footer class="site-footer">')
page = src[start:end]
page = re.sub(r'<svg.*?</svg>', ' ', page, flags=re.S)
page = re.sub(r'<[^>]+>', ' ', page)
page = html.unescape(page)

TR = str.maketrans({'\u0131': 'i', '\u0130': 'i', '\u015f': 's', '\u015e': 's',
                    '\u011f': 'g', '\u011e': 'g', '\u00fc': 'u', '\u00dc': 'u',
                    '\u00f6': 'o', '\u00d6': 'o', '\u00e7': 'c', '\u00c7': 'c'})


def norm(s):
    s = html.unescape(s)
    s = s.replace('\u2014', ' ').replace('\u2013', ' ').replace('\u2019', "'")
    s = s.translate(TR).lower()
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


page_n = norm(page)

missing = []
checked = 0
for raw in APPROVED.splitlines():
    line = raw.strip()
    if not line or set(line) <= set('='):
        continue
    if line.startswith('\u2022'):
        line = line[1:].strip()
    exp = norm(line)
    if not exp:
        continue
    checked += 1
    if exp not in page_n:
        missing.append(line)

print('checked %d approved lines' % checked)
if missing:
    print('MISSING %d:' % len(missing))
    for m in missing:
        print('  -', m[:130])
    sys.exit(1)
print('CONTENT INTEGRITY OK')
