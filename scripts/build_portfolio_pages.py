#!/usr/bin/env python3
"""Build the six NOVA completed-portfolio project pages.

The shared chrome (utility bar, header, mobile bottom bar, side menu, footer)
is lifted verbatim from marti-residence.html so the global navigation and
footer stay byte-identical across the site.  Everything between the chrome is
authored per project from verified nova.istanbul project data.
"""
import re
from pathlib import Path

ROOT = Path('/app/frontend')
BASE = (ROOT / 'marti-residence.html').read_text(encoding='utf-8')


def slice_between(start_marker, end_marker):
    a = BASE.index(start_marker)
    b = BASE.index(end_marker, a) + len(end_marker)
    return BASE[a:b]


CHROME = slice_between('<!-- ============================= TOP UTILITY BAR', '</aside>')
FOOTER = slice_between('<footer class="site-footer">', '</footer>')

LIGHTBOX = """  <!-- ============================= GALLERY LIGHTBOX ============================= -->
  <div class="pp-lightbox" id="ppLightbox" aria-hidden="true" role="dialog" aria-modal="true" aria-label="Project images">
    <button class="pp-lightbox-close" id="ppLightboxClose" type="button" aria-label="Close images" data-testid="pp-lightbox-close">&times;</button>
    <button class="pp-lightbox-prev" id="ppLightboxPrev" type="button" aria-label="Previous image" data-testid="pp-lightbox-prev">&lsaquo;</button>
    <button class="pp-lightbox-next" id="ppLightboxNext" type="button" aria-label="Next image" data-testid="pp-lightbox-next">&rsaquo;</button>
    <img id="ppLightboxImg" alt="" />
    <p class="pp-lightbox-meta" id="ppLightboxMeta"></p>
  </div>
"""

PROJECT_OPTIONS = [
    ('dogan', 'Doğan Residence, Erenköy'),
    ('fplaza', 'Falcon Plaza, Levent'),
    ('flogistic', 'Falcon Logistics Center, İstanbul'),
    ('konelsis', 'Konelsis Center, Ankara'),
    ('nisbetiye', 'Nisbetiye On, Etiler–Levent'),
    ('gebze', 'Gebze OSB Management Building, Gebze'),
]


def enquiry(key):
    opts = '\n'.join(
        '              <option{sel}>{label}</option>'.format(
            sel=' selected' if k == key else '', label=label)
        for k, label in PROJECT_OPTIONS)
    return """  <!-- ============================= REQUEST PROJECT INFORMATION ============================= -->
  <section class="pp-enquiry" id="register">
    <div class="pp-enquiry-inner">
      <div class="pp-enquiry-copy">
        <p class="pp-eyebrow reveal-up">NOVA KONUT</p>
        <h2 class="pp-enquiry-title reveal-up">Request project information.</h2>
        <p class="pp-enquiry-lead reveal-up">Contact Nova for further information about this completed project and our wider portfolio.</p>
      </div>
      <div class="pp-enquiry-form-col">
        <p class="pp-enquiry-note reveal-up">PLEASE PROVIDE YOUR DETAILS AND WE WILL BE IN TOUCH.</p>
        <form class="pp-form reveal-up" id="ppEnquiryForm" novalidate>
          <div class="pp-field">
            <label for="pp-fullname">Full Name</label>
            <input id="pp-fullname" type="text" name="fullname" required data-testid="pp-form-name" />
          </div>
          <div class="pp-field">
            <label for="pp-phone">Phone</label>
            <div class="pp-phone-row">
              <select name="code" aria-label="Country code">
                <option>+1</option><option>+44</option><option selected>+90</option><option>+971</option><option>+966</option>
              </select>
              <input id="pp-phone" type="tel" name="phone" data-testid="pp-form-phone" />
            </div>
          </div>
          <div class="pp-field">
            <label for="pp-email">Email</label>
            <input id="pp-email" type="email" name="email" required data-testid="pp-form-email" />
          </div>
          <div class="pp-field">
            <label for="pp-project">Project</label>
            <select id="pp-project" name="project" data-testid="pp-form-project">
%s
            </select>
          </div>
          <div class="pp-field pp-field--wide">
            <label for="pp-comments">Your Enquiry</label>
            <textarea id="pp-comments" name="comments" rows="2"></textarea>
          </div>
          <div class="pp-checks">
            <label><input type="checkbox" name="news" /> <span>I&rsquo;d like to receive news about Nova Konut projects</span></label>
            <label><input type="checkbox" name="privacy" required data-testid="pp-form-privacy" /> <span>I&rsquo;ve read and agree to the <a href="#">Privacy Policy</a></span></label>
          </div>
          <button type="submit" class="pp-submit" data-testid="pp-form-submit">SEND REQUEST</button>
          <p class="pp-form-msg" id="ppFormMsg" role="status" aria-live="polite" data-testid="pp-form-msg"></p>
        </form>
      </div>
    </div>
  </section>
""" % opts


def head(title, desc, og_image, css, canonical):
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5, user-scalable=yes" />
  <meta name="theme-color" content="#14120f" />
  <meta name="description" content="{desc}" />
  <title>{title}</title>

  <link rel="canonical" href="https://nova.istanbul/{canonical}" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="Nova Konut" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:image" content="./{og_image}" />
  <meta name="twitter:card" content="summary_large_image" />

  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link rel="preload" as="image" href="./{og_image}" type="image/webp" fetchpriority="high" />
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600;700&family=Great+Vibes&family=Montserrat:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500&display=swap" rel="stylesheet" />

  <link rel="stylesheet" href="css/styles.css" />
  <link rel="stylesheet" href="css/portfolio-project.css" />
  <link rel="stylesheet" href="css/{css}" />
</head>
""".format(title=title, desc=desc, og_image=og_image, css=css, canonical=canonical)


def page(meta, body):
    return (
        head(meta['title'], meta['desc'], meta['og'], meta['css'], meta['file'])
        + '<body class="page-project {cls} pp-page">\n'.format(cls=meta['cls'])
        + '  ' + CHROME + '\n\n'
        + '  <main id="top">\n' + body + '  </main>\n\n'
        + '  ' + FOOTER + '\n\n'
        + LIGHTBOX + '\n'
        + '  <script src="js/script.js"></script>\n'
        + '  <script src="js/portfolio-project.js"></script>\n'
        + '</body>\n</html>\n'
    )


def specs(rows):
    cells = []
    for label, value, sub in rows:
        small = '<small>{}</small>'.format(sub) if sub else ''
        cells.append(
            '        <div class="pp-spec">\n'
            '          <div class="pp-spec-label">{label}</div>\n'
            '          <div class="pp-spec-value">{value}{small}</div>\n'
            '        </div>'.format(label=label, value=value, small=small))
    return ('  <!-- ============================= SPECIFICATION STRIP ============================= -->\n'
            '  <section class="pp-specs reveal-up" aria-label="Project specification">\n'
            '    <div class="pp-specs-grid" data-testid="pp-specs">\n'
            + '\n'.join(cells) + '\n'
            '    </div>\n'
            '  </section>\n')


def intro(eyebrow, lead, note=None):
    extra = '\n        <p class="pp-body pp-intro-note">{}</p>'.format(note) if note else ''
    return ('  <!-- ============================= INTRODUCTION ============================= -->\n'
            '  <section class="pp-intro">\n'
            '    <div class="pp-intro-inner">\n'
            '      <p class="pp-eyebrow reveal-up">{eyebrow}</p>\n'
            '      <div class="reveal-up">\n'
            '        <p class="pp-intro-lead">{lead}</p>{extra}\n'
            '      </div>\n'
            '    </div>\n'
            '  </section>\n').format(eyebrow=eyebrow, lead=lead, extra=extra)


def frame(src, alt, span, ratio, caption=None, contain=False, sizes='(max-width: 960px) 92vw, 46vw',
          width=None, height=None, openable=True):
    cap = '\n          <figcaption class="pp-media-caption">{}</figcaption>'.format(caption) if caption else ''
    return ('        <figure class="pp-media-frame{contain} {span} {ratio} pp-reveal-media"{opener}>\n'
            '          <img src="./{src}" alt="{alt}" width="{w}" height="{h}" sizes="{sizes}" loading="lazy" decoding="async" />{cap}\n'
            '        </figure>').format(
        contain=' pp-media-frame--contain' if contain else '',
        span=span, ratio=ratio, src=src, alt=alt, w=width, h=height, sizes=sizes, cap=cap,
        opener=' data-pp-open' if openable else '')


# =====================================================================
# 1. DOĞAN RESIDENCE
# =====================================================================
dogan_meta = dict(
    file='dogan-residence.html', cls='page-dogan', css='dogan-residence.css', js='dogan-residence.js',
    title='Doğan Residence | Nova Konut',
    desc='Doğan Residence (Doğan Apartmanı) — a 5,150 m² residential development of twenty-four homes '
         'completed in 2017 in Erenköy, Bağdat Caddesi, İstanbul.',
    og='media/images/dogan/dogan-facade-detail.webp')

dogan_body = (
    """  <!-- ============================= HERO ============================= -->
  <section class="pp-hero pp-hero--split">
    <div class="pp-hero-inner">
      <div class="pp-hero-copy">
        <p class="pp-hero-eyebrow reveal-up">Completed Development &middot; 2017</p>
        <h1 class="pp-hero-title reveal-up">Doğan Residence</h1>
        <p class="pp-hero-native reveal-up">Doğan Apartmanı</p>
        <p class="pp-hero-loc reveal-up"><span>Erenköy, Bağdat Caddesi</span><em>/</em><span>İstanbul</span></p>
      </div>
      <figure class="pp-hero-media pp-hero-media--portrait pp-reveal-media" data-pp-open data-testid="dogan-hero-image">
        <img src="./media/images/dogan/dogan-building-front.webp" width="768" height="902"
             sizes="(max-width: 960px) 92vw, 54vw"
             alt="Doğan Residence — frontal view of the completed twelve-storey residential building in Erenköy"
             fetchpriority="high" decoding="async" />
      </figure>
    </div>
  </section>

"""
    + intro(
        'The Project',
        'Completed in 2017 in Erenköy, Doğan Residence brings together twenty-four homes within a '
        '5,150 m² residential development.',
        'The building comprises twelve residential floors above the ground level, supported by two basement '
        'levels dedicated in part to enclosed parking and building services.')
    + specs([
        ('Project Type', 'Residential Development', None),
        ('Location', 'Erenköy, Bağdat&nbsp;Caddesi', 'İstanbul'),
        ('Completion Year', '2017', None),
        ('Total Construction Area', '5,150 m²', None),
        ('Floors', '12 residential', '1 ground floor &middot; 2 basement levels'),
        ('Status', 'Completed Development', None),
    ])
    + """  <!-- ============================= EXTERIOR GALLERY ============================= -->
  <section class="pp-gallery" aria-labelledby="dogan-gallery-title">
    <div class="pp-gallery-head">
      <p class="pp-eyebrow reveal-up">Exterior Architecture</p>
      <h2 class="pp-section-title reveal-up" id="dogan-gallery-title">The building on its Erenköy street.</h2>
      <p class="pp-body reveal-up">Four further views of the completed development, recorded from the street and from the
        approach to the entrance. Select any image to view it at full size.</p>
    </div>
    <div class="pp-gallery-grid" data-pp-stagger>
"""
    + frame('media/images/dogan/dogan-facade-detail.webp',
            'Doğan Residence — the textured stone and dark metal façade volumes of the completed building',
            'pp-span-3', 'pp-ratio-portrait', width=1536, height=2048) + '\n'
    + frame('media/images/dogan/dogan-facade-corner.webp',
            'Doğan Residence — corner view showing the balconies and the stone-clad façade volumes',
            'pp-span-3', 'pp-ratio-portrait', width=768, height=1024) + '\n'
    + frame('media/images/dogan/dogan-facade-trees.webp',
            'Doğan Residence — the building seen through the mature trees of the neighbouring street',
            'pp-span-3', 'pp-ratio-portrait', width=550, height=734) + '\n'
    + frame('media/images/dogan/dogan-facade-night.webp',
            'Doğan Residence — the perforated metal and stone façade detail illuminated at night',
            'pp-span-3', 'pp-ratio-portrait', width=768, height=1024) + '\n'
    + """    </div>
    <div class="pp-gallery-foot reveal-up">
      <button class="pp-textlink" type="button" data-pp-open-all data-testid="dogan-view-all">View all images</button>
    </div>
  </section>

  <!-- ============================= RESIDENTIAL PROGRAMME ============================= -->
  <section class="pp-programme" aria-labelledby="dogan-programme-title">
    <div class="pp-programme-inner">
      <div>
        <p class="pp-eyebrow reveal-up">Residential Programme</p>
        <h2 class="pp-section-title reveal-up" id="dogan-programme-title">Twenty-four residences.</h2>
        <p class="pp-body pp-programme-note reveal-up">The residential programme is distributed across the twelve
          residential floors above ground level.</p>
      </div>
      <div class="pp-programme-rows reveal-up" data-testid="dogan-programme">
        <div class="pp-programme-row"><span class="pp-programme-key">3+1 Residences</span><span class="pp-programme-val">18</span></div>
        <div class="pp-programme-row"><span class="pp-programme-key">2+1 Residences</span><span class="pp-programme-val">4</span></div>
        <div class="pp-programme-row"><span class="pp-programme-key">Duplex Residences</span><span class="pp-programme-val">2</span></div>
        <div class="pp-programme-row pp-programme-row--total"><span class="pp-programme-key">Total Residences</span><span class="pp-programme-val">24</span></div>
      </div>
    </div>
  </section>

  <!-- ============================= BUILDING SYSTEMS ============================= -->
  <section class="pp-editorial pp-editorial--dark" aria-labelledby="dogan-systems-title">
    <div class="pp-editorial-inner">
      <div class="pp-editorial-copy">
        <p class="pp-eyebrow reveal-up">Building Systems</p>
        <h2 class="pp-section-title reveal-up" id="dogan-systems-title">Designed for everyday continuity.</h2>
        <p class="pp-body reveal-up">Two levels of underground parking provide direct lift access to the residences,
          while exterior thermal insulation, a swimming pool and a sound-insulated automatic generator support the
          building&rsquo;s everyday performance.</p>
      </div>
      <ul class="pp-facts reveal-up" data-testid="dogan-features">
        <li><span>01</span><span>Exterior thermal insulation</span></li>
        <li><span>02</span><span>Two-level underground parking</span></li>
        <li><span>03</span><span>Elevator access from the parking levels directly to the residences</span></li>
        <li><span>04</span><span>Swimming pool</span></li>
        <li><span>05</span><span>Designed in compliance with the applicable earthquake regulations at the time of construction</span></li>
        <li><span>06</span><span>Sound-insulated fully automatic generator</span></li>
      </ul>
    </div>
  </section>

"""
    + enquiry('dogan'))

# =====================================================================
# 2. FALCON PLAZA
# =====================================================================
fplaza_meta = dict(
    file='falcon-plaza.html', cls='page-fplaza', css='falcon-plaza.css', js='falcon-plaza.js',
    title='Falcon Plaza | Nova Konut',
    desc='Falcon Plaza — an eight-storey, 4,000 m² office building completed in 2015 on Libadiye Sokağı, '
         'Levent, İstanbul.',
    og='media/images/falcon-plaza/falcon-plaza-exterior.webp')

fplaza_body = (
    """  <!-- ============================= HERO ============================= -->
  <section class="pp-hero pp-hero--split pp-hero--compact">
    <div class="pp-hero-inner">
      <div class="pp-hero-copy">
        <p class="pp-hero-eyebrow reveal-up">Completed Development &middot; 2015</p>
        <h1 class="pp-hero-title reveal-up">Falcon Plaza</h1>
        <p class="pp-hero-native reveal-up">Office Building</p>
        <p class="pp-hero-loc reveal-up"><span>Libadiye Sokağı, Levent</span><em>/</em><span>İstanbul</span></p>
      </div>
      <figure class="pp-hero-media pp-hero-media--landscape pp-hero-media--contain pp-reveal-media" data-pp-open data-testid="fplaza-hero-image">
        <img src="./media/images/falcon-plaza/falcon-plaza-exterior.webp" width="640" height="480"
             sizes="(max-width: 960px) 92vw, 620px"
             alt="Falcon Plaza — the completed eight-storey office building with its dark glazed façade and roof-level signage in Levent"
             fetchpriority="high" decoding="async" />
        <figcaption class="pp-media-caption">Completed Building</figcaption>
      </figure>
    </div>
  </section>

"""
    + intro(
        'The Project',
        'Falcon Plaza is an eight-storey office building located on Libadiye Street in Levent.',
        'Completed in 2015, the project delivers 4,000 m² of corporate workspace within one of İstanbul&rsquo;s '
        'established business districts.')
    + specs([
        ('Project Type', 'Office Building', None),
        ('Location', 'Libadiye Sokağı, Levent', 'İstanbul'),
        ('Completion Year', '2015', None),
        ('Total Construction Area', '4,000 m²', None),
        ('Floors', '8', None),
        ('Status', 'Completed Development', None),
    ])
    + """  <!-- ============================= PROJECT OVERVIEW ============================= -->
  <section class="pp-editorial pp-editorial--single" aria-labelledby="fplaza-overview-title">
    <div class="pp-editorial-inner">
      <div class="pp-editorial-copy">
        <p class="pp-eyebrow reveal-up">Project Overview</p>
        <h2 class="pp-section-title reveal-up" id="fplaza-overview-title">Four thousand square metres of workspace, on eight floors.</h2>
        <p class="pp-body reveal-up">Falcon Plaza was delivered in 2015 as a dedicated office building on Libadiye
          Sokağı in Levent. Its 4,000 m² of construction area is organised over eight floors.</p>
        <p class="pp-body reveal-up">The project is presented here through its single documented photograph and its
          verified construction record. No further technical information is published for this development.</p>
      </div>
    </div>
  </section>

"""
    + enquiry('fplaza'))

# =====================================================================
# 3. FALCON LOGISTICS CENTER
# =====================================================================
flogistic_meta = dict(
    file='falcon-logistic.html', cls='page-flogistic', css='falcon-logistic.css', js='falcon-logistic.js',
    title='Falcon Logistics Center | Nova Konut',
    desc='Falcon Logistics Center (Falcon Lojistik) — a 21,500 m² logistics warehouse facility completed in '
         'İstanbul in 2014.',
    og='media/images/falcon-logistics/falcon-logistics-exterior.webp')

flogistic_body = (
    """  <!-- ============================= HERO ============================= -->
  <section class="pp-hero pp-hero--full">
    <figure class="pp-hero-media" data-testid="flogistic-hero-image">
      <img src="./media/images/falcon-logistics/falcon-logistics-exterior.webp" width="1241" height="874"
           sizes="100vw"
           alt="Falcon Logistics Center — the completed warehouse facility with its loading docks and glazed office frontage"
           fetchpriority="high" decoding="async" />
      <div class="pp-hero-scrim" aria-hidden="true"></div>
    </figure>
    <div class="pp-hero-copy">
      <p class="pp-hero-eyebrow reveal-up">Completed Development &middot; 2014</p>
      <h1 class="pp-hero-title reveal-up">Falcon Logistics Center</h1>
      <p class="pp-hero-native reveal-up">Falcon Lojistik</p>
      <p class="pp-hero-loc reveal-up"><span>Logistics Warehouse Facility</span><em>/</em><span>İstanbul</span></p>
    </div>
  </section>

"""
    + intro(
        'The Project',
        'Falcon Logistics Center is a 21,500 m² logistics warehouse facility delivered in İstanbul in 2014.',
        'Its scale and programme reflect the operational requirements of a dedicated logistics development.')
    + specs([
        ('Project Type', 'Logistics Warehouse Facility', None),
        ('Location', 'İstanbul', None),
        ('Completion Year', '2014', None),
        ('Total Construction Area', '21,500 m²', None),
        ('Status', 'Completed Development', None),
    ])
    + """  <!-- ============================= OPERATIONAL SCALE ============================= -->
  <section class="pp-gallery" aria-labelledby="flogistic-gallery-title">
    <div class="pp-gallery-head">
      <p class="pp-eyebrow reveal-up">The Facility</p>
      <h2 class="pp-section-title reveal-up" id="flogistic-gallery-title">Built around operational scale.</h2>
      <p class="pp-body reveal-up">The project brings its logistics and warehouse functions together within a single
        21,500 m² development. The facility is presented through its exterior and interior architecture, without
        introducing specifications that are not documented in the original project record.</p>
    </div>
    <div class="pp-gallery-grid" data-pp-stagger>
"""
    + frame('media/images/falcon-logistics/falcon-logistics-interior.webp',
            'Falcon Logistics Center — the warehouse interior with its concrete column grid, stacked pallets and a forklift in operation',
            'pp-span-4', 'pp-ratio-pano', caption='Warehouse Interior',
            sizes='(max-width: 960px) 92vw, 60vw', width=1076, height=754) + '\n'
    + frame('media/images/falcon-logistics/falcon-logistics-facade.webp',
            'Falcon Logistics Center — the ribbed metal and glass façade of the facility seen against the sky',
            'pp-span-2', 'pp-ratio-portrait', caption='Façade',
            sizes='(max-width: 960px) 92vw, 30vw', width=768, height=1024) + '\n'
    + frame('media/images/falcon-logistics/falcon-logistics-entrance.webp',
            'Falcon Logistics Center — the main entrance elevation with its glazed office volume and planted forecourt',
            'pp-span-2', 'pp-ratio-portrait', caption='Entrance Elevation',
            sizes='(max-width: 960px) 92vw, 30vw', width=768, height=1024) + '\n'
    + """      <div class="pp-gallery-note pp-span-4 reveal-up">
        <p class="pp-body">Warehouse, circulation and office functions share one envelope on a single site. The images
          above are the complete authentic photographic record held for the project: an interior bay, the façade
          system and the entrance elevation.</p>
        <button class="pp-textlink" type="button" data-pp-open-all data-testid="flogistic-view-all">View all images</button>
      </div>
    </div>
  </section>

"""
    + enquiry('flogistic'))

# =====================================================================
# 4. KONELSIS CENTER
# =====================================================================
konelsis_meta = dict(
    file='konelsis-center.html', cls='page-konelsis', css='konelsis-center.css', js='konelsis-center.js',
    title='Konelsis Center | Nova Konut',
    desc='Konelsis Center — the 6,500 m² corporate headquarters of Konelsis Enerji A.Ş. in Yenimahalle, Ankara, '
         'completed in 2023.',
    og='media/images/konelsis/konelsis-render.webp')

konelsis_body = (
    """  <!-- ============================= HERO ============================= -->
  <section class="pp-hero pp-hero--split pp-hero--wide-media">
    <div class="pp-hero-inner">
      <div class="pp-hero-copy">
        <p class="pp-hero-eyebrow reveal-up">Completed Development &middot; 2023</p>
        <h1 class="pp-hero-title reveal-up">Konelsis Center</h1>
        <p class="pp-hero-native reveal-up">Corporate Headquarters</p>
        <p class="pp-hero-loc reveal-up"><span>Yenimahalle</span><em>/</em><span>Ankara</span></p>
      </div>
      <figure class="pp-hero-media pp-hero-media--wide pp-reveal-media" data-pp-open data-testid="konelsis-hero-image">
        <img src="./media/images/konelsis/konelsis-render.webp" width="1600" height="900"
             sizes="(max-width: 960px) 92vw, 54vw"
             alt="Konelsis Center — architectural visualisation of the corporate headquarters building in Yenimahalle, Ankara"
             fetchpriority="high" decoding="async" />
        <figcaption class="pp-media-caption">Architectural Visualisation</figcaption>
      </figure>
    </div>
  </section>

"""
    + intro(
        'The Project',
        'Konelsis Center is the 6,500 m² corporate headquarters of Konelsis Enerji A.Ş. in Yenimahalle, Ankara.',
        'Delivered in 2023, the project was developed as a dedicated corporate building bringing the '
        'organisation&rsquo;s principal workplace functions together within a single address.')
    + specs([
        ('Project Type', 'Corporate Headquarters', None),
        ('Organisation', 'Konelsis Enerji A.Ş.', None),
        ('Location', 'Yenimahalle', 'Ankara'),
        ('Completion Year', '2023', None),
        ('Total Construction Area', '6,500 m²', None),
        ('Status', 'Completed Development', None),
    ])
    + """  <!-- ============================= CORPORATE PROGRAMME ============================= -->
  <section class="pp-editorial pp-editorial--dark pp-editorial--single" aria-labelledby="konelsis-overview-title">
    <div class="pp-editorial-inner">
      <div class="pp-editorial-copy">
        <p class="pp-eyebrow reveal-up">Corporate Programme</p>
        <h2 class="pp-section-title reveal-up" id="konelsis-overview-title">One address for a single organisation.</h2>
        <p class="pp-body reveal-up">The 6,500 m² building was commissioned as the headquarters of Konelsis Enerji A.Ş.
          and completed in 2023 in Yenimahalle, Ankara.</p>
        <p class="pp-body reveal-up">The visualisation above is the architectural record held for the project. Further
          technical and programme information is not published for this development.</p>
      </div>
    </div>
  </section>

"""
    + enquiry('konelsis'))

# =====================================================================
# 5. NİSBETİYE ON
# =====================================================================
nisbetiye_meta = dict(
    file='nisbetiye-on.html', cls='page-nisbetiye', css='nisbetiye-on.css', js='nisbetiye-on.js',
    title='Nisbetiye On | Nova Konut',
    desc='Nisbetiye On — a 36,000 m² mixed-use development in the Etiler–Levent corridor of İstanbul, '
         'completed in the first quarter of 2015.',
    og='media/images/nisbetiye-on/nisbetiye-on-entrance.webp')

nisbetiye_body = (
    """  <!-- ============================= HERO ============================= -->
  <section class="pp-hero pp-hero--full">
    <figure class="pp-hero-media" data-pp-open data-testid="nisbetiye-hero-image">
      <img src="./media/images/nisbetiye-on/nisbetiye-on-entrance.webp" width="1600" height="1067"
           sizes="100vw"
           alt="Nisbetiye On — the completed building&rsquo;s main entrance canopy and glazed lobby on Nisbetiye"
           fetchpriority="high" decoding="async" />
      <div class="pp-hero-scrim" aria-hidden="true"></div>
    </figure>
    <div class="pp-hero-copy">
      <p class="pp-hero-eyebrow reveal-up">Completed Development &middot; Q1 2015</p>
      <h1 class="pp-hero-title reveal-up">Nisbetiye On</h1>
      <p class="pp-hero-native reveal-up">Mixed-Use Development</p>
      <p class="pp-hero-loc reveal-up"><span>Nisbetiye</span><em>/</em><span>Etiler&ndash;Levent</span><em>/</em><span>İstanbul</span></p>
    </div>
  </section>

"""
    + intro(
        'The Project',
        'Completed in the first quarter of 2015, Nisbetiye On is a 36,000 m² mixed-use development positioned '
        'within the Etiler&ndash;Levent corridor.',
        'The project combines residential, commercial and social programmes within a single integrated urban '
        'development.')
    + specs([
        ('Project Type', 'Mixed-Use Development', None),
        ('Location', 'Nisbetiye, Etiler&ndash;Levent', 'İstanbul'),
        ('Completion', 'Q1 2015', None),
        ('Total Programme', '36,000 m²', None),
        ('Levels', '9 residential floors', '4 commercial levels &middot; 3 parking levels'),
        ('Status', 'Completed Development', None),
    ])
    + """  <!-- ============================= ARCHITECTURAL RECORD ============================= -->
  <section class="pp-gallery" aria-labelledby="nisbetiye-media-title">
    <div class="pp-gallery-head">
      <p class="pp-eyebrow reveal-up">Architectural Record</p>
      <h2 class="pp-section-title reveal-up" id="nisbetiye-media-title">The development as drawn, and as built.</h2>
      <p class="pp-body reveal-up">Two architectural visualisations from the design stage sit alongside the photograph
        of the completed entrance above. Each image is identified by its media type.</p>
    </div>
    <div class="pp-gallery-grid" data-pp-stagger>
"""
    + frame('media/images/nisbetiye-on/nisbetiye-on-visualisation-night.webp',
            'Nisbetiye On — night-time architectural visualisation showing the residential block above the commercial levels and the landscaped terraces',
            'pp-span-3', 'pp-ratio-landscape', caption='Architectural Visualisation',
            sizes='(max-width: 960px) 92vw, 46vw', width=1800, height=1570) + '\n'
    + frame('media/images/nisbetiye-on/nisbetiye-on-visualisation-day.webp',
            'Nisbetiye On — daylight architectural visualisation of the nine residential floors and the retail frontage',
            'pp-span-3', 'pp-ratio-landscape', caption='Architectural Visualisation',
            sizes='(max-width: 960px) 92vw, 46vw', width=1800, height=1483) + '\n'
    + """    </div>
    <div class="pp-gallery-foot reveal-up">
      <button class="pp-textlink" type="button" data-pp-open-all data-testid="nisbetiye-view-all">View all images</button>
    </div>
  </section>

  <!-- ============================= PROGRAMME BREAKDOWN ============================= -->
  <section class="pp-programme" aria-labelledby="nisbetiye-programme-title">
    <div class="pp-programme-inner">
      <div>
        <p class="pp-eyebrow reveal-up">Programme</p>
        <h2 class="pp-section-title reveal-up" id="nisbetiye-programme-title">A balanced urban programme.</h2>
        <p class="pp-body pp-programme-note reveal-up">The development comprises 11,000 m² of residential space,
          11,000 m² of retail and office space and 14,000 m² of social amenities for residents. Its programme is
          organised across nine residential floors, four commercial levels and three parking levels.</p>
        <p class="pp-body pp-programme-note reveal-up">Developed in line with the international LEED green building
          framework.</p>
      </div>
      <div class="reveal-up">
        <div class="pp-programme-rows" data-testid="nisbetiye-programme">
          <div class="pp-programme-row"><span class="pp-programme-key">Residential</span><span class="pp-programme-val">11,000 m²</span></div>
          <div class="pp-programme-row"><span class="pp-programme-key">Retail and Office</span><span class="pp-programme-val">11,000 m²</span></div>
          <div class="pp-programme-row"><span class="pp-programme-key">Resident Social Amenities</span><span class="pp-programme-val">14,000 m²</span></div>
          <div class="pp-programme-row pp-programme-row--total"><span class="pp-programme-key">Total Programme</span><span class="pp-programme-val">36,000 m²</span></div>
        </div>
        <ul class="pp-facts">
          <li><span>09</span><span>Residential floors</span></li>
          <li><span>04</span><span>Commercial levels</span></li>
          <li><span>03</span><span>Parking levels</span></li>
        </ul>
      </div>
    </div>
  </section>

"""
    + enquiry('nisbetiye'))

# =====================================================================
# 6. GEBZE OSB MANAGEMENT BUILDING
# =====================================================================
gebze_meta = dict(
    file='gebze-osb-management.html', cls='page-gebze', css='gebze-osb-management.css', js='gebze-osb-management.js',
    title='Gebze OSB Management Building | Nova Konut',
    desc='Gebze OSB Management Building — the 5,500 m² administration building of the Gebze Güzeller Organized '
         'Industrial Zone, completed in 2011 in Gebze, Kocaeli.',
    og='media/images/gebze-osb/gebze-osb-building.webp')

gebze_body = (
    """  <!-- ============================= HERO ============================= -->
  <section class="pp-hero pp-hero--split">
    <div class="pp-hero-inner">
      <div class="pp-hero-copy">
        <p class="pp-hero-eyebrow reveal-up">Completed Development &middot; 2011</p>
        <h1 class="pp-hero-title reveal-up">Gebze OSB Management Building</h1>
        <p class="pp-hero-native reveal-up">Administration Building</p>
        <p class="pp-hero-loc reveal-up"><span>Gebze</span><em>/</em><span>Kocaeli</span></p>
      </div>
      <figure class="pp-hero-media pp-hero-media--landscape pp-hero-media--contain pp-reveal-media" data-pp-open data-testid="gebze-hero-image">
        <img src="./media/images/gebze-osb/gebze-osb-building.webp" width="650" height="488"
             sizes="(max-width: 960px) 92vw, 640px"
             alt="Gebze OSB Management Building — the completed administration building of the Gebze Güzeller Organized Industrial Zone"
             fetchpriority="high" decoding="async" />
        <figcaption class="pp-media-caption">Completed Building</figcaption>
      </figure>
    </div>
  </section>

"""
    + intro(
        'The Project',
        'The Gebze OSB Management Building is the 5,500 m² administration building of the Gebze Güzeller '
        'Organized Industrial Zone.',
        'Completed in 2011 in Gebze, Kocaeli, the project provides a dedicated institutional setting for the '
        'organisation&rsquo;s administrative functions.')
    + specs([
        ('Project Type', 'Administration Building', None),
        ('Organisation', 'Gebze Güzeller OSB', 'Organized Industrial Zone'),
        ('Location', 'Gebze', 'Kocaeli'),
        ('Completion Year', '2011', None),
        ('Total Construction Area', '5,500 m²', None),
        ('Status', 'Completed Development', None),
    ])
    + """  <!-- ============================= DESIGN AND DELIVERY ============================= -->
  <section class="pp-gallery" aria-labelledby="gebze-visuals-title">
    <div class="pp-gallery-head">
      <p class="pp-eyebrow reveal-up">Design and Delivery</p>
      <h2 class="pp-section-title reveal-up" id="gebze-visuals-title">From visualisation to completed building.</h2>
      <p class="pp-body reveal-up">The two images held for the project are shown side by side and identified by media
        type: the design-stage visualisation, and the building as completed in 2011.</p>
    </div>
    <div class="pp-gallery-grid" data-pp-stagger>
"""
    + frame('media/images/gebze-osb/gebze-osb-render.webp',
            'Gebze OSB Management Building — design-stage architectural visualisation of the administration building',
            'pp-span-3', 'pp-ratio-landscape', caption='Architectural Visualisation',
            sizes='(max-width: 960px) 92vw, 46vw', width=650, height=487) + '\n'
    + frame('media/images/gebze-osb/gebze-osb-building.webp',
            'Gebze OSB Management Building — photograph of the completed administration building in Gebze, Kocaeli',
            'pp-span-3', 'pp-ratio-landscape', caption='Completed Building &middot; 2011',
            sizes='(max-width: 960px) 92vw, 46vw', width=650, height=488) + '\n'
    + """    </div>
  </section>

  <!-- ============================= INSTITUTIONAL PROGRAMME ============================= -->
  <section class="pp-editorial pp-editorial--single" aria-labelledby="gebze-programme-title">
    <div class="pp-editorial-inner">
      <div class="pp-editorial-copy">
        <p class="pp-eyebrow reveal-up">Institutional Programme</p>
        <h2 class="pp-section-title reveal-up" id="gebze-programme-title">An administrative address for an industrial zone.</h2>
        <p class="pp-body reveal-up">The building was delivered for the Gebze Güzeller Organized Industrial Zone as the
          administrative centre of the zone, with a total construction area of 5,500 m².</p>
        <p class="pp-body reveal-up">Only the completion year, project type, organisation and construction area are
          documented for this development; no further programme detail is published.</p>
      </div>
    </div>
  </section>

"""
    + enquiry('gebze'))


PAGES = [
    (dogan_meta, dogan_body),
    (fplaza_meta, fplaza_body),
    (flogistic_meta, flogistic_body),
    (konelsis_meta, konelsis_body),
    (nisbetiye_meta, nisbetiye_body),
    (gebze_meta, gebze_body),
]

for meta, body in PAGES:
    html = page(meta, body)
    (ROOT / meta['file']).write_text(html, encoding='utf-8')
    leftovers = len(re.findall(r'marti|Martı|Suadiye|waterfront', html, flags=re.I))
    marti_assets = len(re.findall(r'media/images/marti', html))
    print('{:32} {:5} lines | marti/suadiye refs: {} | marti assets: {}'.format(
        meta['file'], html.count('\n'), leftovers, marti_assets))
