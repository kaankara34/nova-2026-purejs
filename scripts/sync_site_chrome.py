"""Index EN/TR are authoritative CONTENT; retain each page's presentation and language URLs.

Run directly after editing either index. No whole-site rebuild or runtime content fetch.
"""
import copy
import re
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from bs4 import BeautifulSoup, NavigableString, Tag

ROOT = Path(__file__).resolve().parents[1] / 'frontend'
REGIONS = {
    'utility': r'<div\b[^>]*\bid="utilityBar"[^>]*>',
    'header': r'<header\b[^>]*\bid="siteHeader"[^>]*>',
    'bottom': r'<div\b[^>]*\bid="mobileBottomBar"[^>]*>',
    'menu': r'<aside\b[^>]*\bid="sideMenu"[^>]*>',
    'footer': r'<footer\b[^>]*class="[^"]*\bsite-footer\b[^"]*"[^>]*>',
}
CONTENT_ATTRS = ('href', 'target', 'rel', 'aria-label', 'alt', 'title', 'data-title',
                 'data-target', 'data-id', 'data-projects', 'src', 'srcset')


def region_span(html, kind):
    opening = re.search(REGIONS[kind], html)
    if not opening:
        return None
    tag = re.match(r'<(\w+)', opening[0])[1]
    depth = 1
    for match in re.finditer(rf'</?{tag}\b[^>]*>', html[opening.end():]):
        depth += -1 if match[0].startswith('</') else 1
        if depth == 0:
            return opening.start(), opening.end() + match.end()
    raise ValueError(f'Unclosed {kind} region')


def fragment(html, kind):
    span = region_span(html, kind)
    if not span:
        return None
    return BeautifulSoup(html[slice(*span)], 'html.parser').find()


def local_href(href, lang):
    """Repair existing wrong-language local filenames without changing approved copy."""
    from build_i18n import PAGE_MAP
    parts = urlsplit(href)
    if parts.scheme or parts.netloc or not parts.path or '/' in parts.path:
        return href
    names = {name: pair[0 if lang == 'en' else 1]
             for original, pair in PAGE_MAP.items() for name in (original, *pair)}
    return urlunsplit(('', '', names.get(parts.path, parts.path), parts.query, parts.fragment))


def content_key(tag):
    if tag.get('aria-label'):
        return ('aria', tag['aria-label'])
    if tag.get('data-id'):
        return ('group', tag['data-id'])
    if tag.get('class'):
        return ('class', tuple(tag['class']))
    return ('tag', tag.name)


def merge_content(source, destination):
    """Preserve target element/tag/classes/styles/dimensions; replace semantic content only."""
    if source.name == 'svg' and destination.name == 'svg':
        return copy.deepcopy(destination)  # never restyle a target icon
    result = copy.deepcopy(destination)
    for attribute in CONTENT_ATTRS:
        if attribute in source.attrs:
            result[attribute] = copy.deepcopy(source[attribute])
        elif attribute in result.attrs:
            del result[attribute]
    if source.get('data-testid'):
        result['data-testid'] = source['data-testid']
    # Content may add/remove/reorder menu entries and social links. Use matching target
    # presentation when available, then same structural slot, not a page-wide CSS copy.
    children = [node for node in destination.children if isinstance(node, Tag)]
    used = set()
    result.clear()
    position = 0
    for node in source.children:
        if not isinstance(node, Tag):
            result.append(copy.copy(node))
            continue
        candidate = next((i for i, child in enumerate(children)
                          if i not in used and content_key(child) == content_key(node)), None)
        if candidate is None and not node.get('aria-label') and position < len(children) and position not in used:
            candidate = position
        if candidate is None:
            result.append(copy.deepcopy(node))
        else:
            used.add(candidate)
            result.append(merge_content(node, children[candidate]))
        position += 1
    return result


def prepared_source(html, lang):
    regions = {kind: fragment(html, kind) for kind in REGIONS}
    for root in regions.values():
        if root is None:
            continue
        for link in root.select('a[href]'):
            if not link.find_parent(class_='lang-switch'):
                link['href'] = local_href(link['href'], lang)
    menu = regions['menu']
    home = menu.select_one('.menu-list .menu-item:first-child .menu-link')
    home.name = 'a'
    home['href'] = 'index.html#top'
    home['data-testid'] = 'menu-link-home'
    for node in menu.select('.lang-switch--menu'):
        node.decompose()
    return regions


def sync_page(html, canonical, lang):
    for kind in REGIONS:
        span = region_span(html, kind)
        if not span:
            continue
        target = fragment(html, kind)
        source = canonical[kind]
        if source is None:
            continue
        if kind == 'menu':
            for node in target.select('.lang-switch--menu'):
                node.decompose()
            selectors = ['.menu-list', '.side-menu-foot', '.col-sub-back']
            selectors += [f'.submenu[data-id="{node["data-id"]}"]' for node in source.select('.submenu[data-id]')]
            selectors += [f'.projects-preview[data-id="{node["data-id"]}"]' for node in source.select('.projects-preview[data-id]')]
        elif kind == 'footer':
            selectors = ['.footer-discover-title', '.footer-discover-row', '.footer-menu-links',
                         '.social-label', '.social-icons-small', '.footer-bottom-links', '.footer-copyright-text']
        elif kind == 'header':
            selectors = ['.icon-links', '.menu-toggle']
            action = target.select_one('.register')
            final = source.select_one('.register')
            if action and final:
                action.clear()
                for node in final.contents:
                    action.append(copy.deepcopy(node))
                action['aria-label'] = final.get('aria-label', final.get_text(strip=True))
            logo = target.select_one('.logo-mark')
            if logo:
                logo['href'] = '#top' if 'id="top"' in html[:span[0]] else 'index.html#top'
                logo['aria-label'] = source.select_one('.logo-mark').get('aria-label', 'Nova')
                if logo.img and source.select_one('.logo-img'):
                    logo.img['alt'] = source.select_one('.logo-img').get('alt', '')
        elif kind == 'bottom':
            selectors = ['.bottom-icons']
            action, final = target.select_one('.btn-bottom-register'), source.select_one('.btn-bottom-register')
            if action and final:
                action.clear()
                for node in final.contents:
                    action.append(copy.deepcopy(node))
        else:
            selectors = ['.utility-left', '.utility-socials']
        for selector in selectors:
            original, final = target.select_one(selector), source.select_one(selector)
            if original and final:
                original.replace_with(merge_content(final, original))
        if kind == 'menu':
            home = target.select_one('.menu-list .menu-item:first-child .menu-link')
            home.name = 'a'
            home['href'] = 'index.html#top'
        # IDs on updated controls, without altering their display/layout.
        for i, node in enumerate(target.select('a, button, input, select, [role="switch"]')):
            if not node.get('data-testid'):
                node['data-testid'] = f'{kind}-control-{i + 1}'
        html = html[:span[0]] + str(target) + html[span[1]:]
    return add_favicon(html)


def add_favicon(html):
    def remove_icon(match):
        rel = re.search(r'\brel=["\']([^"\']+)', match[0], re.I)
        return '' if rel and any(word in rel[1].lower().split() for word in ('icon', 'apple-touch-icon')) else match[0]
    html = re.sub(r'[ \t]*<link\b[^>]*>[ \t]*(?:\r?\n)?', remove_icon, html)
    links = ('  <link rel="icon" href="../favicon.ico" sizes="16x16 32x32 48x48" />\n'
             '  <link rel="icon" type="image/png" href="../favicon-32.png" sizes="32x32" />\n'
             '  <link rel="icon" type="image/png" href="../favicon-192.png" sizes="192x192" />\n'
             '  <link rel="apple-touch-icon" href="../apple-touch-icon.png" sizes="180x180" />\n')
    return re.sub(r'\s*</head>', '\n' + links + '</head>', html, count=1)


def sync_site(root=ROOT):
    changed = 0
    for lang in ('en', 'tr'):
        canonical = prepared_source((root / lang / 'index.html').read_text(encoding='utf-8'), lang)
        for path in sorted((root / lang).glob('*.html')):
            old = path.read_text(encoding='utf-8')
            new = sync_page(old, canonical, lang)
            if old != new:
                path.write_text(new, encoding='utf-8')
                changed += 1
    print(f'Canonical navbar/footer content and favicon updated in {changed} pages.')


if __name__ == '__main__':
    sync_site()