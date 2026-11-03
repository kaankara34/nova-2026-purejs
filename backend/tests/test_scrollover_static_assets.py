# Public static asset serving and TR/EN page contracts; no backend API changes in this scope.
import os
from pathlib import Path

import pytest
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv(Path('/app/frontend/.env'))
BASE_URL = os.environ['REACT_APP_BACKEND_URL'].rstrip('/')
PLANS = [f'{tower}-{kind}.webp' for tower in ('east', 'west')
         for kind in ('3plus1', '4plus1', 'duplex-lower', 'duplex-upper')]


@pytest.mark.parametrize('filename', PLANS)
def test_plan_asset(filename):
    response = requests.get(f'{BASE_URL}/media/images/ew/plans/{filename}', timeout=30)
    assert response.status_code == 200
    assert response.headers['Content-Type'].split(';')[0] == 'image/webp'
    assert response.content[:4] == b'RIFF' and response.content[8:12] == b'WEBP'


def test_bahar_lowercase_asset():
    response = requests.get(f'{BASE_URL}/media/images/bahar-cover.jpg', timeout=30)
    assert response.status_code == 200
    assert response.headers['Content-Type'].split(';')[0] == 'image/jpeg'
    assert response.content[:3] == b'\xff\xd8\xff'


def test_bahar_old_uppercase_absent():
    response = requests.get(f'{BASE_URL}/media/images/bahar-cover.JPG', timeout=30)
    assert response.status_code == 404
    assert not response.headers.get('Content-Type', '').startswith('image/')


@pytest.mark.parametrize('lang', ['tr', 'en'])
def test_east_west_script_order_and_preload(lang):
    response = requests.get(f'{BASE_URL}/{lang}/the-residences-east-west.html', timeout=30)
    assert response.status_code == 200
    soup = BeautifulSoup(response.text, 'html.parser')
    scripts = soup.select('script[src]')
    required = ['swipe-carousel.js', 'ew-plans-data.js', 'east-west.js']
    matches = [next(s for s in scripts if s['src'].endswith(name)) for name in required]
    assert [scripts.index(s) for s in matches] == sorted(scripts.index(s) for s in matches)
    assert all('async' not in s.attrs and 'defer' not in s.attrs for s in matches)
    assert soup.select_one('link[rel="preload"][href$="east-3plus1.webp"][as="image"]')


@pytest.mark.parametrize('lang,filename', [('tr', 'projeler.html'), ('en', 'projects.html')])
def test_projects_bahar_reference(lang, filename):
    response = requests.get(f'{BASE_URL}/{lang}/{filename}', timeout=30)
    assert response.status_code == 200
    soup = BeautifulSoup(response.text, 'html.parser')
    image = soup.select_one('[data-testid="pj-card-bahar-residence"] img')
    assert image['src'] == '../media/images/bahar-cover.jpg'


@pytest.mark.parametrize('lang', ['tr', 'en'])
def test_home_structure(lang):
    response = requests.get(f'{BASE_URL}/{lang}/index.html', timeout=30)
    assert response.status_code == 200
    soup = BeautifulSoup(response.text, 'html.parser')
    assert soup.select_one('.home-hero-scrollover > .hero video[autoplay][muted][playsinline]')
    assert soup.select_one('.home-hero-scrollover > .home-scrollover-content > #buildBeyondLiving')
    assert 'home-page' in soup.html['class'] and 'home-page' in soup.body['class']