"""Extract every translatable string from the approved English pages.

Produces /app/scripts/i18n_strings.json: a de-duplicated, ordered list of the
text segments and attribute values that need Turkish equivalents. Shared chrome
(header, side menu, footer) collapses to a single entry each.
"""
import glob
import json
import os
import re

SRC = '/app/frontend'
SKIP_TAGS = re.compile(r'<(script|style|svg|noscript)\b.*?</\1>', re.S | re.I)
ATTRS = ('alt', 'title', 'placeholder', 'aria-label', 'value', 'content', 'data-title')
META_NAMES = ('description', 'og:title', 'og:description', 'twitter:title', 'twitter:description')


def segments(html):
    """Yield every text run that sits between two tags."""
    for m in re.finditer(r'>([^<>]+)<', html):
        yield m.group(1)


def attr_values(html):
    for m in re.finditer(r'<([a-zA-Z0-9-]+)\b([^>]*)>', html):
        tag, rest = m.group(1).lower(), m.group(2)
        for a in re.finditer(r'([a-zA-Z-]+)\s*=\s*"([^"]*)"', rest):
            name, val = a.group(1).lower(), a.group(2)
            if name == 'content':
                if tag != 'meta':
                    continue
                key = re.search(r'(?:name|property)\s*=\s*"([^"]*)"', rest)
                if not key or key.group(1) not in META_NAMES:
                    continue
            elif name == 'value':
                if 'type="hidden"' in rest or tag != 'input':
                    continue
            elif name not in ATTRS:
                continue
            yield val


def meaningful(s):
    t = s.strip()
    if len(t) < 2:
        return False
    if not re.search(r'[A-Za-z]', t):
        return False
    if re.fullmatch(r'[\s\W\d]+', t):
        return False
    return True


def main():
    found = {}
    for path in sorted(glob.glob(os.path.join(SRC, '*.html'))):
        name = os.path.basename(path)
        html = SKIP_TAGS.sub('', open(path, encoding='utf-8').read())
        for raw in list(segments(html)) + list(attr_values(html)):
            t = ' '.join(raw.split())
            if not meaningful(t):
                continue
            found.setdefault(t, []).append(name)

    out = [{'en': k, 'tr': '', 'pages': sorted(set(v))} for k, v in found.items()]
    out.sort(key=lambda r: (-len(r['pages']), -len(r['en'])))
    with open('/app/scripts/i18n_strings.json', 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    words = sum(len(r['en'].split()) for r in out)
    print('unique strings:', len(out), 'words:', words)
    print('shared (>=20 pages):', sum(1 for r in out if len(r['pages']) >= 20))


if __name__ == '__main__':
    main()
