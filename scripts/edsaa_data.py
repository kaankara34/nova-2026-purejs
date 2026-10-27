"""Approved static EDSAA content. Do not infer additional company facts."""
ORIGIN = 'https://nova.istanbul'
PAGE = 'edsaa.html'
IMAGE = 'media/images/ew/render/ew-render1.webp'
PARENT_NAME = 'Nova Konut İnşaat Yatırım A.Ş.'
CONTENT = {
    'tr': {
        'title': 'EDSAA | İnşaat | Nova Konut',
        'intro': 'EDSAA, Nova Konut İnşaat Yatırım A.Ş.’nin inşaat alanında faaliyet gösteren iştirakidir.',
        'description': 'EDSAA, Nova Konut İnşaat Yatırım A.Ş.’nin inşaat alanında faaliyet gösteren iştirakidir. EDSAA hakkında bilgi için Nova’nın kurumsal sayfasını ziyaret edin.',
        'alt': 'The Residences East West mimari renderı',
        'locale': 'tr_TR',
    },
    'en': {
        'title': 'EDSAA | Construction | Nova Konut',
        'intro': 'EDSAA is an affiliate of Nova Konut İnşaat Yatırım A.Ş., operating in the construction sector.',
        'description': 'EDSAA is an affiliate of Nova Konut İnşaat Yatırım A.Ş., operating in the construction sector. Learn about EDSAA on Nova’s corporate website.',
        'alt': 'The Residences East West architectural render',
        'locale': 'en_GB',
    },
}


def structured_data(lang):
    preferred = f'{ORIGIN}/tr/{PAGE}'
    canonical = f'{ORIGIN}/{lang}/{PAGE}'
    entity = preferred + '#organization'
    # No pre-existing Nova Organization @id is present in the site's current JSON-LD.
    # Reference only the known parent name/homepage; do not manufacture entity details.
    return {'@context': 'https://schema.org', '@graph': [
        {'@type': 'AboutPage', '@id': canonical + '#webpage', 'url': canonical,
         'name': CONTENT[lang]['title'], 'description': CONTENT[lang]['intro'],
         'inLanguage': lang, 'mainEntity': {'@id': entity}},
        {'@type': 'Organization', '@id': entity, 'name': 'EDSAA',
         'description': CONTENT[lang]['intro'], 'url': preferred,
         'parentOrganization': {'@type': 'Organization', 'name': PARENT_NAME, 'url': ORIGIN + '/'}},
    ]}