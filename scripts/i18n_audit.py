"""Static audit of the bilingual output: pairing, link language mapping, assets,
canonical/hreflang reciprocity, html lang, language-switch targets and sitemap.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_i18n import PAGE_MAP, WEB, OUT_EN, OUT_TR, ORIGIN

EN_FILES = {en for en, _ in PAGE_MAP.values()}
TR_FILES = {tr for _, tr in PAGE_MAP.values()}
problems = []


def check(cond, msg):
    if not cond:
        problems.append(msg)


def main():
    check(len(EN_FILES) == len(PAGE_MAP), 'duplicate EN filenames')
    check(len(TR_FILES) == len(PAGE_MAP), 'duplicate TR filenames')
    for src, (en, tr) in PAGE_MAP.items():
        check(os.path.isfile(os.path.join(OUT_EN, en)), 'missing /en/%s' % en)
        check(os.path.isfile(os.path.join(OUT_TR, tr)), 'missing /tr/%s' % tr)

    for lang, folder, allowed in (('en', OUT_EN, EN_FILES), ('tr', OUT_TR, TR_FILES)):
        for src, pair in PAGE_MAP.items():
            name = pair[0] if lang == 'en' else pair[1]
            path = os.path.join(folder, name)
            html = open(path, encoding='utf-8').read()
            tag = '/%s/%s' % (lang, name)

            check('<html lang="%s">' % lang in html, '%s: wrong html lang' % tag)

            canon = re.search(r'<link rel="canonical" href="([^"]+)"', html)
            check(canon and canon.group(1) == '%s/%s/%s' % (ORIGIN, lang, name),
                  '%s: canonical wrong' % tag)
            alts = dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', html))
            check(alts.get('en') == '%s/en/%s' % (ORIGIN, pair[0]), '%s: hreflang en wrong' % tag)
            check(alts.get('tr') == '%s/tr/%s' % (ORIGIN, pair[1]), '%s: hreflang tr wrong' % tag)
            check(alts.get('x-default') == '%s/tr/%s' % (ORIGIN, pair[1]),
                  '%s: x-default wrong' % tag)

            switch = re.findall(r'<a class="lang-opt[^"]*" href="([^"]+)"', html)
            check(switch.count('/tr/' + pair[1]) == 2 and switch.count('/en/' + pair[0]) == 2,
                  '%s: language switch targets wrong (%s)' % (tag, switch))

            # internal page links must stay inside the same language set
            body = re.sub(r'<div class="lang-switch.*?</div>', '', html, flags=re.S)
            for href in re.findall(r'href="([^"#?:]+\.html)', body):
                target = os.path.basename(href)
                check(target in allowed, '%s: cross-language link -> %s' % (tag, href))
                check(not href.startswith('/') or href == '/%s/%s' % (lang, target),
                      '%s: odd absolute link %s' % (tag, href))

            # local assets must exist
            refs = re.findall(r'(?:href|src|poster)="(/(?:css|js|media)/[^"]+)"', html)
            refs += [u.strip('\'"') for u in
                     re.findall(r'url\(["\']?(/(?:css|js|media)/[^)\'"]+)', html)]
            for part in re.findall(r'srcset="([^"]+)"', html):
                refs += [p.strip().split()[0] for p in part.split(',') if p.strip()]
                for p in part.split(','):
                    check(not p.strip().startswith(('./', 'css/', 'js/', 'media/')),
                          '%s: relative srcset entry %s' % (tag, p.strip()))
            for ref in set(refs):
                if ref.startswith('/'):
                    check(os.path.isfile(os.path.join(WEB, ref.lstrip('/').split('?')[0])),
                          '%s: missing asset %s' % (tag, ref))

            # no relative css/js/media paths left behind
            check(not re.search(r'(?:href|src|poster|srcset)="(?:\./)?(?:css|js|media)/', html),
                  '%s: relative asset path remains' % tag)
            check(not re.search(r'["\']\./(?:css|js|media)/', html),
                  '%s: relative asset path in style/script remains' % tag)
            check(not re.search(r'url\(["\']?(?:\./)?(?:css|js|media)/', html),
                  '%s: relative url() asset path remains' % tag)

    sm = open(os.path.join(WEB, 'sitemap.xml'), encoding='utf-8').read()
    locs = set(re.findall(r'<loc>([^<]+)</loc>', sm))
    expected = {'%s/%s/%s' % (ORIGIN, lang, n)
                for en, tr in PAGE_MAP.values() for lang, n in (('en', en), ('tr', tr))}
    check(locs == expected, 'sitemap mismatch: missing %s / extra %s'
          % (sorted(expected - locs), sorted(locs - expected)))

    ht = open(os.path.join(WEB, '.htaccess'), encoding='utf-8').read()
    check('RewriteRule ^$ /tr/ [R=301,L]' in ht, '.htaccess root redirect missing')
    for src, (en, _tr) in PAGE_MAP.items():
        if src == 'index.html':
            continue
        check('/en/%s [R=301,L]' % en in ht, '.htaccess legacy rule missing for %s' % src)

    missing_tr = json.load(open('/app/scripts/i18n_missing.json', encoding='utf-8'))
    check(not missing_tr, 'untranslated strings: %d' % len(missing_tr))

    print('problems:', len(problems))
    for p in problems[:60]:
        print(' -', p)


if __name__ == '__main__':
    main()
