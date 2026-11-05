"""Frontend-only cPanel source contract and public static-page regression checks."""
import os
import re
import subprocess
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote

import pytest
import requests

ROOT = Path('/app/frontend')


def preview_url():
    configured = os.environ.get('REACT_APP_BACKEND_URL')
    if configured:
        return configured.rstrip('/')
    for line in (ROOT / '.env').read_text().splitlines():
        if line.startswith('REACT_APP_BACKEND_URL='):
            return line.split('=', 1)[1].strip().rstrip('/')
    raise RuntimeError('REACT_APP_BACKEND_URL is not configured.')


BASE_URL = preview_url()
PAGES = ['tr/index.html', 'en/index.html', 'tr/projeler.html', 'en/projects.html',
         'tr/the-residences-east-west.html', 'en/the-residences-east-west.html']

class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if value and key in ('src', 'href', 'poster'):
                self.refs.append(value)
            if value and key == 'style':
                self.refs.extend(re.findall(r'url\([\'\"]?([^\)\'\"]+)', value))

def test_exact_upstream():
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd='/app', text=True).strip()
    upstream = subprocess.check_output(['git', 'rev-parse', 'upstream/conflict_tr_destekli'], cwd='/app', text=True).strip()
    assert head != upstream
    subprocess.run(['git', 'merge-base', '--is-ancestor', upstream, head], cwd='/app', check=True)

def test_static_package_contract():
    import json
    for name in ['index.html', '.htaccess', 'tr/index.html', 'en/index.html', 'css', 'js', 'media', 'robots.txt', 'sitemap.xml']:
        assert (ROOT / name).exists(), name
    package = json.loads((ROOT / 'package.json').read_text())
    assert package['dependencies'] == {}
    assert 'build' not in package['scripts']
    root_entry = (ROOT / 'index.html').read_text()
    assert "window.location.replace('tr/')" in root_entry

def test_all_language_html_asset_references():
    missing, absolute = [], []
    count = 0
    for page in list((ROOT / 'tr').glob('*.html')) + list((ROOT / 'en').glob('*.html')):
        parser = References()
        parser.feed(page.read_text())
        for ref in parser.refs:
            path = unquote(urlsplit(ref).path)
            if urlsplit(ref).scheme or ref.startswith('//'):
                continue
            if not re.search(r'(?:^|/)(css|js|media)/', path):
                continue
            count += 1
            if path.startswith(('/css/', '/js/', '/media/')):
                absolute.append((str(page.relative_to(ROOT)), ref))
            target = ROOT / path.lstrip('/') if path.startswith('/') else page.parent / path
            if not target.exists():
                missing.append((str(page.relative_to(ROOT)), ref))
    print('Checked local asset references:', count)
    assert not absolute, absolute
    assert not missing, missing

def test_apache_source_targets():
    text = (ROOT / '.htaccess').read_text()
    for rule in ['RewriteBase /', 'RewriteRule ^$ /tr/ [R=301,L]',
                 r'RewriteRule ^index\.html$ /tr/ [R=301,L]',
                 'RewriteCond %{REQUEST_FILENAME} !-f',
                 'RewriteCond %{REQUEST_FILENAME}.html -f',
                 'RewriteRule ^(.+)$ $1.html [L]', 'ErrorDocument 404 /tr/index.html']:
        assert rule in text
    assert (ROOT / 'tr/index.html').is_file()

@pytest.mark.parametrize('path', PAGES)
def test_public_static_page(path):
    response = requests.get(BASE_URL + '/' + path, timeout=30)
    assert response.status_code == 200
    assert 'text/html' in response.headers['Content-Type']
    assert f'lang="{path[:2]}"' in response.text
    assert 'data-testid="header-control-1"' in response.text
    assert '../css/styles.css' in response.text