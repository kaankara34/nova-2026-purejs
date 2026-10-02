"""Per-page coverage report: list the still-untranslated strings of one source
page in document order, so the Turkish dictionaries can be completed page by page.

    python3 scripts/i18n_report.py construction.html
    python3 scripts/i18n_report.py            # summary for every page
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_i18n import PAGE_MAP, SRC, SKIP_BLOCK, TRANSLATABLE_ATTRS, META_KEYS, load_dict


def page_strings(src_name):
    html = SKIP_BLOCK.sub('', open(os.path.join(SRC, src_name), encoding='utf-8').read())
    out = []
    for m in re.finditer(r'>([^<>]+)<', html):
        key = ' '.join(m.group(1).split())
        if re.search(r'[A-Za-z]', key) and len(key) >= 2:
            out.append(key)
    for m in re.finditer(r'<([a-zA-Z0-9-]+)\b([^>]*)>', html):
        tag, rest = m.group(1).lower(), m.group(2)
        meta_key = None
        if tag == 'meta':
            k = re.search(r'(?:name|property)\s*=\s*"([^"]*)"', rest)
            meta_key = k.group(1) if k else None
        for a in re.finditer(r'([a-zA-Z-]+)\s*=\s*"([^"]*)"', rest):
            name, val = a.group(1).lower(), a.group(2)
            if name == 'content':
                if tag != 'meta' or meta_key not in META_KEYS:
                    continue
            elif name not in TRANSLATABLE_ATTRS:
                continue
            key = ' '.join(val.split())
            if re.search(r'[A-Za-z]', key) and len(key) >= 2:
                out.append(key)
    seen, uniq = set(), []
    for k in out:
        if k not in seen:
            seen.add(k)
            uniq.append(k)
    return uniq


def main():
    table = load_dict()
    if len(sys.argv) > 1:
        target = sys.argv[1]
        missing = [k for k in page_strings(target) if k not in table]
        json.dump([{'en': k, 'tr': ''} for k in missing],
                  open('/app/scripts/i18n_page_todo.json', 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        print('%s: %d missing, %d words -> scripts/i18n_page_todo.json'
              % (target, len(missing), sum(len(k.split()) for k in missing)))
        return
    total = 0
    for src_name, (_en, tr) in PAGE_MAP.items():
        missing = [k for k in page_strings(src_name) if k not in table]
        words = sum(len(k.split()) for k in missing)
        total += words
        if missing:
            print('%-50s %4d strings %6d words  (/tr/%s)' % (src_name, len(missing), words, tr))
    print('total missing words:', total)


if __name__ == '__main__':
    main()
