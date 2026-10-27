"""Build only EDSAA from the existing corporate shell; never rebuild other page bodies."""
import copy
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup
from edsaa_data import CONTENT, IMAGE, ORIGIN, PAGE, structured_data

ROOT = Path(__file__).resolve().parents[1] / 'frontend'


def add_menu_link(html):
    pattern = r'(<ul\b(?=[^>]*\bclass="[^"\n]*\bsubmenu\b)(?=[^>]*\bdata-id="nova-konut")[^>]*>)(.*?)(</ul>)'
    def update(match):
        if 'href="edsaa.html"' in match[2]:
            return match[0]
        item = '\n<li><a data-testid="menu-link-edsaa" href="edsaa.html"><span class="subitem">EDSAA</span></a></li>'
        return match[1] + match[2].replace('</li>', '</li>' + item, 1) + match[3]
    return re.sub(pattern, update, html, flags=re.S)


def build_page(lang):
    content = CONTENT[lang]
    reference = 'iletisim.html' if lang == 'tr' else 'contact.html'
    soup = BeautifulSoup((ROOT / lang / reference).read_text(encoding='utf-8'), 'html.parser')
    home = BeautifulSoup((ROOT / lang / 'index.html').read_text(encoding='utf-8'), 'html.parser')
    soup.html['lang'] = lang
    soup.body['class'] = ['page-contact', 'page-edsaa']
    soup.select_one('#siteHeader')['data-header-theme'] = 'light'
    soup.title.string = content['title']
    for tag in soup.head.select('meta[name="description"], link[rel="canonical"], link[rel="alternate"], script[type="application/ld+json"]'):
        tag.decompose()
    for tag in list(soup.head.find_all('meta')):
        if str(tag.get('property', '')).startswith('og:') or str(tag.get('name', '')).startswith('twitter:'):
            tag.decompose()

    def head_tag(tag_name, **attributes):
        soup.head.append(soup.new_tag(tag_name, attrs=attributes))
        soup.head.append('\n')

    canonical = f'{ORIGIN}/{lang}/{PAGE}'
    head_tag('meta', name='description', content=content['description'])
    head_tag('link', rel='canonical', href=canonical)
    for code in ('tr', 'en'):
        head_tag('link', rel='alternate', hreflang=code, href=f'{ORIGIN}/{code}/{PAGE}')
    # Match the existing default-Turkish strategy used throughout this bilingual site.
    head_tag('link', rel='alternate', hreflang='x-default', href=f'{ORIGIN}/tr/{PAGE}')
    for key, value in {
        'type': 'website', 'title': content['title'], 'description': content['description'],
        'url': canonical, 'site_name': 'Nova Konut', 'locale': content['locale'],
        'locale:alternate': CONTENT['en' if lang == 'tr' else 'tr']['locale'],
        'image': f'{ORIGIN}/{IMAGE}', 'image:type': 'image/webp', 'image:width': '1901',
        'image:height': '1070', 'image:alt': content['alt'],
    }.items():
        head_tag('meta', property='og:' + key, content=value)
    for key, value in {'card': 'summary_large_image', 'title': content['title'],
                       'description': content['description'], 'image': f'{ORIGIN}/{IMAGE}',
                       'image:alt': content['alt']}.items():
        head_tag('meta', name='twitter:' + key, content=value)
    head_tag('link', rel='stylesheet', href='../css/edsaa.css')
    data = soup.new_tag('script', type='application/ld+json')
    data.string = json.dumps(structured_data(lang), ensure_ascii=False, separators=(',', ':'))
    soup.head.append(data)

    main = BeautifulSoup(f'''<main class="edsaa-main" id="edsaa-main" data-testid="edsaa-main">
      <div class="edsaa-wrap">
        <div class="edsaa-intro">
          <h1 class="edsaa-title" data-testid="edsaa-title">EDSAA</h1>
          <p class="edsaa-description" data-testid="edsaa-description">{content['intro']}</p>
        </div>
        <figure class="edsaa-figure" data-testid="edsaa-figure">
          <img class="edsaa-render" data-testid="edsaa-render" src="../{IMAGE}"
            alt="{content['alt']}" width="1901" height="1070" loading="eager" decoding="async" fetchpriority="high" />
          <figcaption class="edsaa-caption">
            <a class="edsaa-project-link" data-testid="edsaa-project-link" href="the-residences-east-west.html">
              <span>The Residences East West</span><span aria-hidden="true">↗</span>
            </a>
          </figcaption>
        </figure>
      </div>
    </main>''', 'html.parser').main
    soup.main.replace_with(main)
    # Contact's shared shell also contains a registration section AFTER its main.
    # EDSAA deliberately has no dedicated form or sales section.
    for section in soup.select('#register'):
        section.decompose()
    for script in list(soup.body.find_all('script')):
        script.decompose()
    # Reuse the actual existing cookie banner, never put content behind consent.
    cookie = soup.select_one('#cookieBanner')
    if cookie:
        cookie.decompose()
    soup.body.append(copy.deepcopy(home.select_one('#cookieBanner')))
    for i, element in enumerate(soup.select('#cookieBanner, #cookieBanner a, #cookieBanner button')):
        if not element.get('data-testid'):
            element['data-testid'] = f'edsaa-cookie-{i + 1}'
    for src in ('../js/script.js',):
        soup.body.append(soup.new_tag('script', src=src))
    # Header actions lead to an existing page rather than inventing an EDSAA form.
    for control in soup.select('.register, .btn-bottom-register'):
        control.name = 'a'
        control.attrs.pop('data-scroll', None)
        control.attrs.pop('type', None)
        control['href'] = reference
    for code in ('en', 'tr'):
        soup.select_one(f'.lang-opt[lang="{code}"]')['href'] = f'../{code}/{PAGE}'
    menu_link = soup.select_one('[data-testid="menu-link-edsaa"]')
    if menu_link:
        menu_link['aria-current'] = 'page'
    return str(soup) + '\n'


def build():
    # Add one standard link in the existing NOVA subgroup, including canonical index files.
    for lang in ('tr', 'en'):
        for path in (ROOT / lang).glob('*.html'):
            old = path.read_text(encoding='utf-8')
            new = add_menu_link(old)
            if old != new:
                path.write_text(new, encoding='utf-8')
    for lang in ('tr', 'en'):
        path = ROOT / lang / PAGE
        updated = build_page(lang)
        if not path.exists() or path.read_text(encoding='utf-8') != updated:
            path.write_text(updated, encoding='utf-8')
    from build_i18n import sitemap
    sitemap()
    print('EDSAA TR/EN pages, existing NOVA menus and sitemap updated.')


if __name__ == '__main__':
    build()