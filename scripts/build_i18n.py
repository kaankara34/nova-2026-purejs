"""Build the bilingual static site: /en/ (approved English, unchanged copy) and
/tr/ (Turkish localisation) from the single set of source pages in /app/frontend.

The English output is a byte-faithful copy of the approved source apart from
absolute asset paths, the head link block, the language selector and the
east-west / speak-up file renames. Turkish text comes exclusively from the
hand-written dictionaries in /app/scripts/i18n_tr/*.json; anything not in a
dictionary stays English and is listed by the coverage report.
"""
import glob
import json
import os
import re
import shutil

SRC = '/app/source-pages'
WEB = '/app/frontend'
OUT_EN = os.path.join(WEB, 'en')
OUT_TR = os.path.join(WEB, 'tr')
ORIGIN = 'https://nova.istanbul'

# source file -> (english filename, turkish filename)
PAGE_MAP = {
    'index.html': ('index.html', 'index.html'),
    'projects.html': ('projects.html', 'projeler.html'),
    'about.html': ('about.html', 'hakkimizda.html'),
    'contact.html': ('contact.html', 'iletisim.html'),
    'team.html': ('team.html', 'organizasyon.html'),
    'partners.html': ('partners.html', 'partnerler.html'),
    'design.html': ('design.html', 'tasarim.html'),
    'construction.html': ('construction.html', 'muhendislik.html'),
    'leed.html': ('leed.html', 'leed.html'),
    'build-beyond-living.html': ('build-beyond-living.html', 'build-beyond-living.html'),
    'newsroom.html': ('newsroom.html', 'medya.html'),
    'news-detail.html': ('news-detail.html', 'haber.html'),
    'careers.html': ('careers.html', 'kariyer.html'),
    'construction-site-manager-architect.html': ('construction-site-manager-architect.html',
                                                 'santiye-muduru-mimar.html'),
    'anonymous-reporting.html': ('speak-up.html', 'bildirim.html'),
    'privacy-notice.html': ('privacy-notice.html', 'gizlilik-bildirimi.html'),
    'cookie-notice.html': ('cookie-notice.html', 'cerez-bildirimi.html'),
    'ethical-principles.html': ('ethical-principles.html', 'etik-ilkeler.html'),
    'applicant-privacy-notice.html': ('applicant-privacy-notice.html', 'aday-aydinlatma-metni.html'),
    'east-west.html': ('the-residences-east-west.html', 'the-residences-east-west.html'),
    'the-apartments-tac.html': ('the-apartments-tac.html', 'the-apartments-tac.html'),
    'the-apartments-ana.html': ('the-apartments-ana.html', 'the-apartments-ana.html'),
    'finance-nova.html': ('finance-nova.html', 'finance-nova.html'),
    'falcon-logistic.html': ('falcon-logistic.html', 'falcon-lojistik-merkezi.html'),
    'falcon-plaza.html': ('falcon-plaza.html', 'falcon-plaza.html'),
    'gebze-osb-management.html': ('gebze-osb-management.html', 'gebze-osb-yonetim-binasi.html'),
    'konelsis-center.html': ('konelsis-center.html', 'konelsis-merkezi.html'),
    'nisbetiye-on.html': ('nisbetiye-on.html', 'nisbetiye-on.html'),
    'mercan-bosphorus.html': ('mercan-bosphorus.html', 'mercan-bosphorus.html'),
    'marti-residence.html': ('marti-residence.html', 'marti-residence.html'),
    'bahar-residence.html': ('bahar-residence.html', 'bahar-residence.html'),
    'dogan-residence.html': ('dogan-residence.html', 'dogan-residence.html'),
    'mehtap-residence.html': ('mehtap-residence.html', 'mehtap-residence.html'),
}

SKIP_BLOCK = re.compile(r'<(script|style|svg|noscript)\b.*?</\1>', re.S | re.I)
TRANSLATABLE_ATTRS = ('alt', 'title', 'placeholder', 'aria-label', 'data-title')
META_KEYS = ('description', 'og:title', 'og:description', 'twitter:title', 'twitter:description')


# --------------------------------------------------------------- dictionary
def load_dict():
    table = {}
    for path in sorted(glob.glob('/app/scripts/i18n_tr/*.json')):
        for row in json.load(open(path, encoding='utf-8')):
            tr = (row.get('tr') or '').strip()
            if tr:
                table[' '.join(row['en'].split())] = tr
    return table


# ------------------------------------------------------------- asset paths
def absolute_assets(html):
    html = re.sub(r'(href|src|poster)="(?:\./)?(css|js|media)/', r'\1="/\2/', html)
    html = re.sub(r'srcset="([^"]*)"',
                  lambda m: 'srcset="%s"' % re.sub(r'(^|,\s*)(?:\./)?(css|js|media)/',
                                                   r'\1/\2/', m.group(1)), html)
    # url() inside inline style attributes and stylesheets, with or without quotes
    html = re.sub(r'url\((["\']?)(?:\./)?(css|js|media)/', r'url(\1/\2/', html)
    # quoted literals in script blocks, data attributes and srcset lists
    html = re.sub(r'(["\'])\./(css|js|media)/', r'\1/\2/', html)
    return html


# ------------------------------------------------------------ internal links
def rewrite_links(html, lang):
    index = 0 if lang == 'en' else 1

    def repl(match):
        quote, target, tail = match.group(1), match.group(2), match.group(3) or ''
        if target in PAGE_MAP:
            return 'href=%s%s%s%s' % (quote, PAGE_MAP[target][index], tail, quote)
        return match.group(0)

    return re.sub(r'href=(")([a-z0-9\-]+\.html)(#[A-Za-z0-9\-_]*)?\1', repl, html)


# ----------------------------------------------------------------- head block
def head_block(src_name, lang):
    en_file, tr_file = PAGE_MAP[src_name]
    self_file = en_file if lang == 'en' else tr_file
    return (
        '\n  <link rel="canonical" href="%(o)s/%(lang)s/%(self)s" />'
        '\n  <link rel="alternate" hreflang="tr" href="%(o)s/tr/%(tr)s" />'
        '\n  <link rel="alternate" hreflang="en" href="%(o)s/en/%(en)s" />'
        '\n  <link rel="alternate" hreflang="x-default" href="%(o)s/tr/%(tr)s" />'
        '\n  <meta property="og:url" content="%(o)s/%(lang)s/%(self)s" />'
        '\n  <meta property="og:locale" content="%(loc)s" />\n'
        % {'o': ORIGIN, 'lang': lang, 'self': self_file, 'en': en_file, 'tr': tr_file,
           'loc': 'tr_TR' if lang == 'tr' else 'en_GB'}
    )


def apply_head(html, src_name, lang):
    html = html.replace('<html lang="en">', '<html lang="%s">' % lang, 1)
    html = re.sub(r'(<link rel="canonical"[^>]*>\n\s*)', '', html)
    html = re.sub(r'(\s*<meta property="og:url"[^>]*>)', '', html)
    block = head_block(src_name, lang)
    return re.sub(r'(</title>)', r'\1' + block.replace('\\', '\\\\'), html, count=1)


# ------------------------------------------------------------- lang selector
def selector(src_name, lang):
    en_file, tr_file = PAGE_MAP[src_name]
    flags = {
        'tr': '<svg class="lang-flag" viewBox="0 0 24 16" aria-hidden="true">'
              '<rect width="24" height="16" fill="#E30A17"/>'
              '<circle cx="9" cy="8" r="4.2" fill="#fff"/>'
              '<circle cx="10.4" cy="8" r="3.4" fill="#E30A17"/>'
              '<path fill="#fff" d="M14.7 8l3.4-1.1-2.1 2.9V5.2l2.1 2.9z"/></svg>',
        'en': '<svg class="lang-flag" viewBox="0 0 24 16" aria-hidden="true">'
              '<rect width="24" height="16" fill="#012169"/>'
              '<path d="M0 0l24 16M24 0L0 16" stroke="#fff" stroke-width="3.2"/>'
              '<path d="M0 0l24 16M24 0L0 16" stroke="#C8102E" stroke-width="1.9"/>'
              '<path d="M12 0v16M0 8h24" stroke="#fff" stroke-width="5.4"/>'
              '<path d="M12 0v16M0 8h24" stroke="#C8102E" stroke-width="3.2"/></svg>',
    }
    items = []
    for code, href in (('tr', '/tr/' + tr_file), ('en', '/en/' + en_file)):
        active = ' is-active' if code == lang else ''
        items.append(
            '<a class="lang-opt%s" href="%s" hreflang="%s" lang="%s"%s>%s<span>%s</span></a>'
            % (active, href, code, code,
               ' aria-current="true"' if active else '',
               flags[code], code.upper()))
    return ('<div class="lang-switch" role="group" aria-label="%s" data-testid="lang-switch">%s</div>'
            % ('Dil se\u00e7imi' if lang == 'tr' else 'Language', ''.join(items)))


def insert_selector(html, src_name, lang):
    block = selector(src_name, lang)
    html = html.replace('<div class="icon-links">', block + '\n        <div class="icon-links">', 1)
    mobile = block.replace('class="lang-switch"', 'class="lang-switch lang-switch--menu"')
    html = html.replace('<div class="side-menu-grid">',
                        '      ' + mobile + '\n    <div class="side-menu-grid">', 1)
    return html


# -------------------------------------------------------------- translation
def translate(html, table, missing):
    protected = []
    orig_title = re.search(r'<title>([^<]*)</title>', html)
    orig_title = ' '.join(orig_title.group(1).split()) if orig_title else None

    def stash(match):
        protected.append(match.group(0))
        return '\x00%d\x00' % (len(protected) - 1)

    html = SKIP_BLOCK.sub(stash, html)

    def text_repl(match):
        raw = match.group(1)
        key = ' '.join(raw.split())
        if '\x00' in raw or not re.search(r'[A-Za-z]', key) or len(key) < 2:
            return match.group(0)
        if key in table:
            lead = raw[:len(raw) - len(raw.lstrip())]
            tail = raw[len(raw.rstrip()):]
            return '>' + lead + table[key] + tail + '<'
        missing.add(key)
        return match.group(0)

    html = re.sub(r'>([^<>]+)<', text_repl, html)

    def tag_repl(match):
        tag, body = match.group(1), match.group(2)
        is_meta = tag.lower() == 'meta'
        meta_key = None
        if is_meta:
            k = re.search(r'(?:name|property)\s*=\s*"([^"]*)"', body)
            meta_key = k.group(1) if k else None

        def attr_repl(a):
            name, val = a.group(1), a.group(2)
            low = name.lower()
            if low == 'content':
                if not is_meta or meta_key not in META_KEYS:
                    return a.group(0)
            elif low not in TRANSLATABLE_ATTRS:
                return a.group(0)
            key = ' '.join(val.split())
            if not re.search(r'[A-Za-z]', key) or len(key) < 2:
                return a.group(0)
            if key in table:
                return '%s="%s"' % (name, table[key])
            missing.add(key)
            return a.group(0)

        return '<%s%s>' % (tag, re.sub(r'([a-zA-Z-]+)\s*=\s*"([^"]*)"', attr_repl, body))

    html = re.sub(r'<([a-zA-Z0-9-]+)\b([^>]*)>', tag_repl, html)

    title = re.search(r'<title>([^<]*)</title>', html)
    if title and orig_title:
        if orig_title in table:
            html = html.replace(title.group(0), '<title>%s</title>' % table[orig_title], 1)
        else:
            missing.add(orig_title)

    for i, chunk in enumerate(protected):
        html = html.replace('\x00%d\x00' % i, chunk)
    return html


# -------------------------------------------------------------------- build
def build():
    table = load_dict()
    for folder in (OUT_EN, OUT_TR):
        shutil.rmtree(folder, ignore_errors=True)
        os.makedirs(folder)

    missing = set()
    for src_name, (en_file, tr_file) in PAGE_MAP.items():
        raw = open(os.path.join(SRC, src_name), encoding='utf-8').read()
        base = absolute_assets(raw)

        en = rewrite_links(base, 'en')
        en = apply_head(en, src_name, 'en')
        en = insert_selector(en, src_name, 'en')
        open(os.path.join(OUT_EN, en_file), 'w', encoding='utf-8').write(en)

        tr = rewrite_links(base, 'tr')
        tr = apply_head(tr, src_name, 'tr')
        tr = translate(tr, table, missing)
        tr = insert_selector(tr, src_name, 'tr')
        open(os.path.join(OUT_TR, tr_file), 'w', encoding='utf-8').write(tr)

    sitemap()
    routing()
    print('pages: %d EN + %d TR' % (len(PAGE_MAP), len(PAGE_MAP)))
    print('dictionary entries: %d' % len(table))
    print('untranslated strings: %d' % len(missing))
    with open('/app/scripts/i18n_missing.json', 'w', encoding='utf-8') as fh:
        json.dump(sorted(missing, key=lambda s: -len(s)), fh, ensure_ascii=False, indent=1)


def sitemap():
    rows = []
    for src_name, (en_file, tr_file) in PAGE_MAP.items():
        for lang, name in (('tr', tr_file), ('en', en_file)):
            rows.append(
                '  <url>\n'
                '    <loc>%(o)s/%(lang)s/%(name)s</loc>\n'
                '    <xhtml:link rel="alternate" hreflang="tr" href="%(o)s/tr/%(tr)s"/>\n'
                '    <xhtml:link rel="alternate" hreflang="en" href="%(o)s/en/%(en)s"/>\n'
                '    <xhtml:link rel="alternate" hreflang="x-default" href="%(o)s/tr/%(tr)s"/>\n'
                '  </url>\n'
                % {'o': ORIGIN, 'lang': lang, 'name': name, 'en': en_file, 'tr': tr_file})
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
           '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
           + ''.join(rows) + '</urlset>\n')
    open(os.path.join(WEB, 'sitemap.xml'), 'w', encoding='utf-8').write(xml)


def routing():
    """Root -> /tr/ plus one-hop 301s from the legacy root-level English URLs."""
    legacy = [(src, en) for src, (en, _tr) in PAGE_MAP.items()]

    rules = ['RewriteEngine On', 'RewriteBase /', '',
             '# Default language is Turkish', 'RewriteRule ^$ /tr/ [R=301,L]',
             'RewriteRule ^index\\.html$ /tr/ [R=301,L]', '',
             '# Legacy root-level English URLs -> /en/ (single hop)']
    for src, en in legacy:
        if src == 'index.html':
            continue
        rules.append('RewriteRule ^%s$ /en/%s [R=301,L]' % (src.replace('.', '\\.'), en))
        rules.append('RewriteRule ^%s$ /en/%s [R=301,L]' % (src[:-5], en))
    rules += ['', '# Extensionless URLs inside the language folders',
              'RewriteCond %{REQUEST_FILENAME} !-f',
              'RewriteCond %{REQUEST_FILENAME}.html -f',
              'RewriteRule ^(.+)$ $1.html [L]', '',
              'ErrorDocument 404 /tr/index.html']
    open(os.path.join(WEB, '.htaccess'), 'w', encoding='utf-8').write('\n'.join(rules) + '\n')

    redirects = [{'source': '/', 'destination': '/tr/index.html', 'type': 301},
                 {'source': '/index.html', 'destination': '/tr/index.html', 'type': 301},
                 {'source': '/tr', 'destination': '/tr/index.html', 'type': 301},
                 {'source': '/tr/', 'destination': '/tr/index.html', 'type': 301},
                 {'source': '/en', 'destination': '/en/index.html', 'type': 301},
                 {'source': '/en/', 'destination': '/en/index.html', 'type': 301}]
    for src, en in legacy:
        if src == 'index.html':
            continue
        redirects.append({'source': '/' + src, 'destination': '/en/' + en, 'type': 301})
        redirects.append({'source': '/' + src[:-5], 'destination': '/en/' + en, 'type': 301})
    cfg = json.load(open(os.path.join(WEB, 'serve.json'), encoding='utf-8'))
    cfg.pop('rewrites', None)
    cfg['redirects'] = redirects
    json.dump(cfg, open(os.path.join(WEB, 'serve.json'), 'w', encoding='utf-8'), indent=2)

    open(os.path.join(WEB, 'robots.txt'), 'w', encoding='utf-8').write(
        'User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n' % ORIGIN)


if __name__ == '__main__':
    build()
