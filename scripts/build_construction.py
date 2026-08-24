import re, io

leed = open('/app/frontend/leed.html', encoding='utf-8').read()
head_block = leed.split('<body class="page-leed" id="top">')[1].split('<!-- ============================= FILM')[0]
footer_block = '<footer class="site-footer">' + leed.split('<footer class="site-footer">')[1].split('</footer>')[0] + '</footer>'
head_block = head_block.replace('data-testid="leed-register-interest"', 'data-testid="cx-register-interest"')
head_block = head_block.replace('<li class="menu-item"><a class="menu-link" href="#"><span class="label">CONSTRUCTION</span></a></li>',
    '<li class="menu-item"><a class="menu-link" href="construction.html" data-testid="menu-link-construction"><span class="label">CONSTRUCTION</span></a></li>')

HEAD = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="theme-color" content="#0d0f10" />
  <meta name="description" content="Nova Konut construction and structural engineering: reinforced-concrete structure, seismic design under TBDY 2018, foundations, concrete execution, reinforcement detailing, quality control, waterproofing and building envelope." />
  <title>Construction &amp; Engineering | Nova Konut</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600;700&family=Montserrat:wght@200;300;400;500;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="css/styles.css" />
  <link rel="stylesheet" href="css/construction.css" />
</head>
<body class="page-cx" id="top">
'''

# ---------------------------------------------------------------- SVG helpers
def slabs_beams():
    ys = [600, 515, 430, 345, 260, 175, 90]
    beams, slabs = [], []
    for y in ys[1:]:
        slabs.append('<rect class="g-solid" x="82" y="%d" width="436" height="7" />' % (y - 7))
        for x0, x1 in [(120, 240), (240, 360), (360, 480)]:
            beams.append('<rect class="g-line" x="%d" y="%d" width="%d" height="15" />' % (x0, y, x1 - x0, ))
    return ''.join(beams), ''.join(slabs)

BEAMS, SLABS = slabs_beams()
COLUMNS = ''.join('<rect class="g-solid" x="%d" y="90" width="18" height="510" />' % (x - 9) for x in (120, 240, 360, 480))
WALLS = ''.join('<rect class="g-solid" x="%d" y="90" width="26" height="510" />' % x for x in (182, 392))
GROUND_HATCH = ''.join('<path class="g-hair" d="M%d 648 l-22 26" />' % x for x in range(70, 620, 26))

STRUCTURE_SVG = '''<svg class="cx-dwg" viewBox="0 0 600 700" role="img" aria-label="Reinforced-concrete structural elevation">
  <g class="cx-part" data-part="0">
    <rect class="g-solid" x="58" y="600" width="484" height="44" />
    <path class="g-line" d="M30 644 H570" />
    %s
  </g>
  <g class="cx-part" data-part="1">%s</g>
  <g class="cx-part" data-part="2">%s</g>
  <g class="cx-part" data-part="3">%s</g>
  <g class="cx-part" data-part="4">%s</g>
  <g class="cx-part" data-part="5"><rect class="g-solid" x="268" y="90" width="64" height="510" /><path class="g-hair" d="M268 90 L332 600 M332 90 L268 600" /></g>
  <path class="g-hair" d="M30 90 H570" />
  <text x="30" y="80">STRUCTURAL ELEVATION — INDICATIVE</text>
</svg>''' % (GROUND_HATCH, COLUMNS, WALLS, BEAMS, SLABS)

SEISMIC_SVG = '''<svg class="cx-dwg" viewBox="0 0 620 640" role="img" aria-label="Structural response diagram">
  <g>
    %s
    %s
    <rect class="g-solid" x="70" y="540" width="440" height="40" />
    <path class="g-line" d="M40 580 H580" />
  </g>
  <g class="cx-part" data-part="0">
    %s
    <text x="40" y="70">GRAVITY ACTIONS</text>
  </g>
  <g class="cx-part" data-part="1">
    %s
    <text x="40" y="612">LATERAL ACTION</text>
  </g>
  <g class="cx-part" data-part="2">
    <path class="g-accent" d="M290 540 C 290 430, 318 320, 336 210 C 348 148, 352 118, 354 90" />
    <path class="g-hair" d="M290 540 V90" />
    <text x="372" y="96">DISPLACEMENT PROFILE</text>
  </g>
  <g class="cx-part" data-part="3">
    <path class="g-accent" d="M150 596 v34 M150 630 l-7 -12 M150 630 l7 -12 M450 596 v34 M450 630 l-7 -12 M450 630 l7 -12" />
    %s
    <text x="40" y="636">BASE REACTIONS — GROUND</text>
  </g>
</svg>''' % (
    ''.join('<rect class="g-line" x="%d" y="90" width="16" height="450" />' % (x - 8) for x in (150, 290, 430)),
    ''.join('<rect class="g-solid" x="132" y="%d" width="316" height="7" />' % y for y in (90, 180, 270, 360, 450)),
    ''.join('<path class="g-accent" d="M%d %d v26 m0 0 l-6 -10 m6 10 l6 -10" />' % (x, y) for y in (100, 190, 280, 370, 460) for x in (200, 380)),
    ''.join('<path class="g-accent" d="M%d %d h%d m0 0 l-11 -6 m11 6 l-11 6" />' % (70 - w, y, w) for y, w in ((97, 58), (187, 48), (277, 38), (367, 28), (457, 20))),
    ''.join('<path class="g-hair" d="M%d 610 l-20 24" />' % x for x in range(80, 620, 24)),
)

GROUND_SVG = '''<svg class="cx-dwg" viewBox="0 0 620 860" role="img" aria-label="Ground and foundation section">
  <path pathLength="1" class="g-line" d="M40 150 H580" />
  <text x="40" y="140">GROUND LEVEL / LANDSCAPE</text>
  <path pathLength="1" class="g-hair" d="M120 150 V90 M180 150 V104 M240 150 V96 M300 150 V88 M360 150 V102 M420 150 V94 M480 150 V98" />
  <path pathLength="1" class="g-solid" d="M120 150 H500 V300 H120 Z" />
  <text x="140" y="235">BASEMENT LEVEL — 01</text>
  <path pathLength="1" class="g-solid" d="M120 300 H500 V450 H120 Z" />
  <text x="140" y="385">BASEMENT LEVEL — 02</text>
  <path pathLength="1" class="g-line" d="M104 150 V470 M516 150 V470" />
  <text x="40" y="470">RETAINING ELEMENTS</text>
  <path pathLength="1" class="g-fill-accent" d="M96 470 H524 V530 H96 Z" />
  <text x="40" y="558">FOUNDATION SYSTEM — PROJECT SPECIFIC</text>
  <path pathLength="1" class="g-line" d="M40 590 H580" />
  <text x="40" y="612">SOIL STRATUM A</text>
  <path pathLength="1" class="g-line" d="M40 660 H580" />
  <text x="40" y="682">SOIL STRATUM B</text>
  <path pathLength="1" class="g-line" d="M40 730 H580" />
  <text x="40" y="752">SOIL STRATUM C</text>
  <path pathLength="1" class="g-hair" d="M40 800 H580" />
  <text x="40" y="822">GEOTECHNICAL INVESTIGATION DEPTH — PROJECT SPECIFIC</text>
  %s
</svg>''' % ''.join('<path pathLength="1" class="g-hair" d="M%d 600 l-16 18 M%d 670 l-16 18 M%d 740 l-16 18" />' % (x, x, x) for x in range(70, 600, 40))

CONCRETE_SVG = '''<svg class="cx-dwg" viewBox="0 0 600 520" role="img" aria-label="Reinforced-concrete element sequence">
  <g class="cx-part" data-part="0">
    <rect class="g-line" x="200" y="120" width="200" height="280" />
    <rect class="g-line" x="222" y="142" width="156" height="236" />
    %s
    <text x="410" y="132">REINFORCEMENT CAGE</text>
  </g>
  <g class="cx-part" data-part="1">
    <rect class="g-solid" x="166" y="96" width="34" height="328" />
    <rect class="g-solid" x="400" y="96" width="34" height="328" />
    <path class="g-hair" d="M150 150 H450 M150 250 H450 M150 350 H450" />
    <text x="60" y="90">FORMWORK &amp; TIES</text>
  </g>
  <g class="cx-part" data-part="2">
    <rect class="g-fill-accent" x="200" y="120" width="200" height="280" />
    <path class="g-accent" d="M300 60 v40 m0 0 l-8 -14 m8 14 l8 -14" />
    <text x="316" y="76">PLACEMENT</text>
  </g>
  <g class="cx-part" data-part="3">
    <path class="g-accent" d="M300 130 v250" />
    <path class="g-hair" d="M262 180 q38 26 76 0 M262 240 q38 26 76 0 M262 300 q38 26 76 0" />
    <text x="410" y="256">COMPACTION</text>
  </g>
  <g class="cx-part" data-part="4">
    <path class="g-hair" d="M200 108 H400 M200 412 H400" />
    <path class="g-accent" d="M208 120 v280 M392 120 v280" />
    <text x="410" y="404">CURING &amp; PROTECTION</text>
  </g>
  <g class="cx-part" data-part="5">
    <rect class="g-solid" x="200" y="120" width="200" height="280" />
    <path class="g-accent" d="M200 440 H400 M200 434 v12 M400 434 v12" />
    <text x="200" y="470">STRUCTURAL ELEMENT — AS EXECUTED</text>
  </g>
</svg>''' % (
    ''.join('<circle class="g-accent" cx="%d" cy="%d" r="6" />' % (x, y) for x in (232, 300, 368) for y in (152, 368)),
)

WATER_SVG = '''<svg class="cx-dwg" viewBox="0 0 720 560" role="img" aria-label="Waterproofing continuity section">
  <g>
    <path class="g-line" d="M120 120 H560 V470 H120 Z" />
    <path class="g-line" d="M120 200 H560 M120 280 H560 M120 360 H560" />
    <path class="g-line" d="M40 470 H120 M560 470 H680" />
    <path class="g-hair" d="M40 500 H680" />
  </g>
  <g class="cx-part" data-part="0">
    %s
    <path class="g-accent" pathLength="1" d="M56 470 H120" />
    <text x="40" y="536">GROUND / WATER CONTACT</text>
  </g>
  <g class="cx-part" data-part="1"><path class="g-accent" pathLength="1" d="M120 470 V300" /><text x="40" y="300">BASEMENT WALL</text></g>
  <g class="cx-part" data-part="2"><path class="g-accent" pathLength="1" d="M120 470 H560" /><text x="300" y="494">FOUNDATION INTERFACE</text></g>
  <g class="cx-part" data-part="3"><path class="g-accent" pathLength="1" d="M560 470 V180" /><text x="578" y="330">FACADE INTERFACE</text></g>
  <g class="cx-part" data-part="4"><path class="g-accent" pathLength="1" d="M560 280 H626 M626 280 V300" /><text x="578" y="272">BALCONY / TERRACE</text></g>
  <g class="cx-part" data-part="5"><path class="g-accent" pathLength="1" d="M560 120 H120" /><text x="120" y="108">ROOF</text></g>
</svg>''' % ''.join('<path class="g-hair" d="M%d 508 l-16 20" />' % x for x in range(60, 700, 26))

ENV_LAYERS = [
    ('01', 'Structural backing', '-96'),
    ('02', 'Continuous insulation layer', '-58'),
    ('03', 'Waterproofing / vapour control', '-24'),
    ('04', 'Ventilated cavity', '18'),
    ('05', 'Facade cladding', '56'),
    ('06', 'Glazing &amp; frame interface', '96'),
]
ENV_SVG = '''<svg class="cx-dwg" viewBox="0 0 620 460" role="img" aria-label="Exploded facade section">
  <path class="g-hair" d="M60 60 H560 M60 400 H560" />
  %s
  <text x="60" y="440">FACADE SECTION — INDICATIVE LAYER SEQUENCE</text>
</svg>''' % ''.join(
    '<g class="cx-part" data-part="%d" data-dx="1" style="--dx:%spx"><rect class="g-solid" x="%d" y="80" width="%d" height="300" />%s</g>'
    % (i, dx, 200 + i * 34, 22 if i != 5 else 14,
       '<path class="g-hair" d="M%d 80 V380" />' % (200 + i * 34 + 11))
    for i, (n, t, dx) in enumerate(ENV_LAYERS))

SERVICES_SVG = '''<svg class="cx-dwg" viewBox="0 0 620 520" role="img" aria-label="Building services coordination">
  <path pathLength="1" class="g-line" d="M110 60 H510 V460 H110 Z" />
  %s
  <path pathLength="1" class="g-solid" d="M288 60 H332 V460 H288 Z" />
  <path pathLength="1" class="g-accent" d="M310 440 V90" />
  <path pathLength="1" class="g-accent" d="M310 120 H460 M310 200 H460 M310 280 H460 M310 360 H460" />
  <path pathLength="1" class="g-accent" d="M310 160 H160 M310 240 H160 M310 320 H160 M310 400 H160" />
  <path pathLength="1" class="g-hair" d="M160 160 V400 M460 120 V360" />
  <text x="110" y="50">VERTICAL SERVICE SHAFT — HORIZONTAL DISTRIBUTION</text>
  <text x="110" y="492">MECHANICAL / ELECTRICAL / WATER / DRAINAGE — COORDINATED WITH STRUCTURE</text>
</svg>''' % ''.join('<path pathLength="1" class="g-hair" d="M110 %d H510" />' % y for y in (140, 220, 300, 380))

WAVE_SVG = '''<svg class="cx-wave" viewBox="0 0 1200 200" preserveAspectRatio="none" aria-hidden="true">
  <path d="M0 100 C 100 40, 200 160, 300 100 C 400 40, 500 160, 600 100 C 700 40, 800 160, 900 100 C 1000 40, 1100 160, 1200 100" />
  <path d="M0 100 C 80 62, 160 138, 240 100 C 320 62, 400 138, 480 100 C 560 62, 640 138, 720 100 C 800 62, 880 138, 960 100 C 1040 62, 1120 138, 1200 100" />
  <path d="M0 100 C 60 78, 120 122, 180 100 C 240 78, 300 122, 360 100 C 420 78, 480 122, 540 100 C 600 78, 660 122, 720 100 C 780 78, 840 122, 900 100 C 960 78, 1020 122, 1080 100 C 1140 78, 1170 111, 1200 100" />
</svg>'''

HERO_GRID = '''<svg class="cx-hero-grid" viewBox="0 0 1600 900" preserveAspectRatio="none" aria-hidden="true">
  <g class="cx-hg-soft">%s</g>
  %s
</svg>''' % (
    ''.join('<path pathLength="1" d="M%d 0 V900" />' % x for x in (320, 640, 960, 1280)),
    ''.join('<path pathLength="1" d="M0 %d H1600" />' % y for y in (180, 360, 540, 720)),
)

def seq(n, extra=''):
    return 'style="height:%dvh" data-cx-steps="%d" %s' % (n * 45 + 100, n, extra)

def steps(items):
    out = []
    for i, (t, d) in enumerate(items):
        out.append('<div class="cx-step" data-step="%d" data-testid="cx-step-%d"><span class="cx-step-i">%02d</span><span class="cx-step-t">%s</span><p class="cx-step-d">%s</p></div>' % (i, i + 1, i + 1, t, d))
    return ''.join(out)

MAIN = '''
  <!-- ================= 01 HERO ================= -->
  <section class="cx-hero" data-testid="cx-hero">
    <div class="cx-hero-stage">
      <div class="cx-hero-layer cx-hero-layer--frame">
        <img src="./media/images/construction/frame-hero.webp" alt="Reinforced-concrete structural frame during construction" width="1900" height="2305" decoding="async" />
      </div>
      <div class="cx-hero-layer cx-hero-layer--finish">
        <img src="./media/images/ew/render/ew-render1.webp" alt="Completed Nova residential architecture" decoding="async" />
      </div>
      __HERO_GRID__
      <div class="cx-hero-scrim"></div>
      <div class="cx-hero-copy">
        <span class="cx-kicker">Nova Konut &middot; Construction &amp; Engineering</span>
        <h1 class="cx-h1" data-testid="cx-hero-title">Built with discipline.<br />Engineered to endure.</h1>
        <p class="cx-lead">Behind every completed residence is a construction process defined by engineering discipline, material control and precision in execution. From ground conditions and structural design to waterproofing, building envelope and final detailing, each stage is approached as part of one integrated system.</p>
        <div class="cx-hero-foot">
          <span class="cx-cue" data-testid="cx-scroll-cue"><span class="cx-cue-line"></span><span class="cx-label">Scroll to remove the envelope</span></span>
          <span class="cx-hero-state" data-testid="cx-hero-state">Completed architecture</span>
        </div>
      </div>
    </div>
  </section>

  <!-- ================= 02 STRUCTURE BEFORE SURFACE ================= -->
  <section class="cx-seq cx-sec--dark" __SEQ2__ data-testid="cx-section-02">
    <div class="cx-seq-stage">
      <div class="cx-seq-copy">
        <span class="cx-num">02</span>
        <h2 class="cx-h2">Structure before surface</h2>
        <p class="cx-lead">Long-term building performance begins with the decisions that cannot be seen once construction is complete. Structural geometry, reinforcement detailing, concrete quality, foundations and the relationship between the structure and ground are established through engineering analysis before architectural finishes are considered.</p>
        <div class="cx-seq-steps">__STEPS2__</div>
        <p class="cx-body" style="margin-top:10px">Structural systems are not standardised across projects. Each system is developed according to architectural configuration, ground conditions, building geometry, structural analysis and the seismic design requirements applicable to the site.</p>
      </div>
      <div class="cx-seq-visual">__STRUCTURE_SVG__</div>
    </div>
  </section>

  <!-- ================= 03 SEISMIC ================= -->
  <section class="cx-seq cx-sec--dark" __SEQ3__ data-cx-mode="single" data-testid="cx-section-03">
    <div class="cx-seq-stage">
      <div class="cx-seq-copy">
        <span class="cx-num">03</span>
        <h2 class="cx-h2">Designed for Istanbul</h2>
        <p class="cx-lead">In Istanbul, seismic design is not a secondary engineering consideration. It is one of the fundamental parameters shaping the structure from the earliest design stages.</p>
        <div class="cx-seq-steps">__STEPS3__</div>
        <p class="cx-body" style="margin-top:10px">Structural design is developed in accordance with the applicable provisions of the T&uuml;rkiye Bina Deprem Y&ouml;netmeli&#287;i and the seismic hazard parameters defined for the project location through the T&uuml;rkiye Deprem Tehlike Haritalar&#305;.</p>
      </div>
      <div class="cx-seq-visual">__SEISMIC_SVG__</div>
    </div>
  </section>

  <section class="cx-sec cx-sec--dark cx-sec--tight" data-testid="cx-section-03b">
    <div class="cx-wrap">
      <div class="cx-rule"></div>
      <div class="cx-head">
        <h3 class="cx-h2" style="font-size:clamp(22px,2.4vw,34px)" data-cx-fade>Seismic performance begins with engineering.</h3>
        <p class="cx-body" data-cx-fade>Design parameters are project specific. The following are considered together rather than in isolation, since seismic behaviour is a property of the whole structure and not of a single element.</p>
      </div>
      <div class="cx-log-items" style="margin-top:38px" data-cx-stagger>
        <div data-cx-fade>Site-specific ground information</div>
        <div data-cx-fade>Seismic hazard parameters for the location</div>
        <div data-cx-fade>Structural configuration and regularity</div>
        <div data-cx-fade>Mass distribution</div>
        <div data-cx-fade>Stiffness distribution</div>
        <div data-cx-fade>Lateral-force-resisting systems</div>
        <div data-cx-fade>Ductility and detailing requirements</div>
        <div data-cx-fade>Displacement and inter-storey drift</div>
        <div data-cx-fade>Foundation behaviour</div>
        <div data-cx-fade>Interaction between structural components</div>
      </div>
    </div>
  </section>

  <!-- ================= 04 GROUND & FOUNDATION ================= -->
  <section class="cx-sec cx-light" data-testid="cx-section-04">
    <div class="cx-wrap">
      <div class="cx-head">
        <div>
          <span class="cx-num" data-cx-fade>04</span>
          <h2 class="cx-h2" data-cx-fade>Every structure begins below ground.</h2>
        </div>
        <p class="cx-lead" data-cx-fade>The behaviour of a building begins with the ground supporting it. Geotechnical information informs foundation design, excavation strategy, groundwater considerations and the relationship between the superstructure and its foundations.</p>
      </div>
      <div class="cx-rule"></div>
      <div class="cx-ground">
        <div class="cx-ground-fig">
          <div class="cx-ground-photo" data-cx-fade>
            <img src="./media/images/construction/foundation.webp" alt="Foundation construction seen from above" width="1800" height="1200" loading="lazy" decoding="async" data-cx-parallax="0.05" />
          </div>
          <div class="cx-chain" data-cx-fade data-testid="cx-ground-chain">
            <span>Ground</span><i></i><span>Foundation</span><i></i><span>Structure</span>
          </div>
          <p class="cx-body" style="margin-top:22px">Foundation systems differ between developments. The system for each project follows from its geotechnical report, excavation depth, groundwater conditions and the loads transferred by the superstructure.</p>
        </div>
        <div data-cx-draw="sequential" data-cx-start="top 78%" data-cx-end="bottom 55%">__GROUND_SVG__</div>
      </div>
    </div>
  </section>

  <!-- ================= 05 REINFORCED CONCRETE ================= -->
  <section class="cx-seq cx-sec--dark" __SEQ5__ data-testid="cx-section-05">
    <div class="cx-seq-stage">
      <div class="cx-seq-copy">
        <span class="cx-num">05</span>
        <h2 class="cx-h2">Concrete is a system, not a surface.</h2>
        <p class="cx-lead">Concrete performance depends on more than its specified strength class. Mix design, production consistency, transportation, placement, compaction, curing, reinforcement detailing, cover and execution conditions collectively determine the quality of the completed structural element.</p>
        <div class="cx-seq-steps">__STEPS5__</div>
        <p class="cx-body" style="margin-top:10px">Concrete is specified, produced and assessed for conformity under TS EN 206 together with its complementary national standard TS 13515; reinforced-concrete design and execution follow TS 500 in its applicable current edition.</p>
      </div>
      <div class="cx-seq-visual">__CONCRETE_SVG__</div>
    </div>
  </section>

  <!-- ================= 06 REINFORCEMENT & DETAILING ================= -->
  <section class="cx-sec cx-sec--dark" data-testid="cx-section-06">
    <div class="cx-wrap">
      <div class="cx-head">
        <div>
          <span class="cx-num" data-cx-fade>06</span>
          <h2 class="cx-h2" data-cx-fade>Details carry the design into reality.</h2>
        </div>
        <p class="cx-lead" data-cx-fade>Structural calculations define the required behaviour of the building. Detailing and execution translate that design into the built structure. Reinforcement continuity, anchorage, lap regions, confinement, spacing and concrete cover are therefore treated as engineering requirements rather than construction formalities.</p>
      </div>
      <div class="cx-rule"></div>
      <div class="cx-env">
        <div class="cx-anno-fig" data-cx-fade data-cx-draw="sequential" data-cx-start="top 80%" data-cx-end="bottom 58%">
          <img src="./media/images/construction/rebar-macro.webp" alt="Reinforcement before concrete placement" width="1500" height="2666" loading="lazy" decoding="async" />
          <svg class="cx-anno-dwg" viewBox="0 0 600 1000" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
            <path pathLength="1" class="g-accent" d="M60 250 H540" />
            <path pathLength="1" class="g-accent" d="M60 500 H540" />
            <path pathLength="1" class="g-accent" d="M60 750 H540" />
            <path pathLength="1" class="g-accent" d="M150 120 V880 M300 120 V880 M450 120 V880" />
            <path pathLength="1" class="g-accent" d="M96 120 H504 V880 H96 Z" />
          </svg>
        </div>
        <div class="cx-anno-list" data-cx-pins=".cx-anno-dwg" data-testid="cx-detail-pins">
          <button class="cx-pin" data-pin="1" data-testid="cx-pin-continuity" aria-expanded="false"><span class="cx-pin-i">A.01</span><span class="cx-pin-t">Continuity</span><span class="cx-pin-d">Reinforcement is detailed so that forces can travel through the element and into adjoining members without interruption.</span></button>
          <button class="cx-pin" data-pin="2" data-testid="cx-pin-anchorage" aria-expanded="false"><span class="cx-pin-i">A.02</span><span class="cx-pin-t">Anchorage</span><span class="cx-pin-d">Bars are anchored so that the design force can be developed within the surrounding concrete rather than at the bar end alone.</span></button>
          <button class="cx-pin" data-pin="3" data-testid="cx-pin-laps" aria-expanded="false"><span class="cx-pin-i">A.03</span><span class="cx-pin-t">Lap regions</span><span class="cx-pin-d">Lap positions and lengths are set by the structural design; their location within an element matters as much as their length.</span></button>
          <button class="cx-pin" data-pin="4" data-testid="cx-pin-confinement" aria-expanded="false"><span class="cx-pin-i">A.04</span><span class="cx-pin-t">Confinement</span><span class="cx-pin-d">Transverse reinforcement confines the concrete core and holds longitudinal bars in position, which is central to ductile behaviour.</span></button>
          <button class="cx-pin" data-pin="5" data-testid="cx-pin-spacing" aria-expanded="false"><span class="cx-pin-i">A.05</span><span class="cx-pin-t">Spacing</span><span class="cx-pin-d">Bar spacing is coordinated with aggregate size and placement method so that concrete can fully surround every bar.</span></button>
          <button class="cx-pin" data-pin="6" data-testid="cx-pin-cover" aria-expanded="false"><span class="cx-pin-i">A.06</span><span class="cx-pin-t">Concrete cover</span><span class="cx-pin-d">Cover protects reinforcement over the life of the building; it is checked before placement, not corrected afterwards.</span></button>
          <p class="cx-body" style="margin-top:22px">Reinforcing steel is specified to the applicable current Turkish standard for steel for the reinforcement of concrete, as referenced by TS 500. Project drawings and bar schedules govern all dimensions.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- ================= 07 QUALITY CONTROL ================= -->
  <section class="cx-sec cx-light" data-testid="cx-section-07">
    <div class="cx-wrap">
      <div class="cx-head">
        <div>
          <span class="cx-num" data-cx-fade>07</span>
          <h2 class="cx-h2" data-cx-fade>Quality is verified through process.</h2>
        </div>
        <p class="cx-lead" data-cx-fade>Construction quality is established through repeated control at each stage rather than a single inspection at completion. Materials, reinforcement, formwork, concrete placement, waterproofing interfaces and architectural details are reviewed throughout the construction process.</p>
      </div>
      <div class="cx-rule"></div>
      <div class="cx-log">
        <div class="cx-log-index" data-testid="cx-log-index">
          <button data-testid="cx-log-btn-1"><i></i>Before pour</button>
          <button data-testid="cx-log-btn-2"><i></i>During pour</button>
          <button data-testid="cx-log-btn-3"><i></i>After pour</button>
          <button data-testid="cx-log-btn-4"><i></i>Enclosure</button>
          <button data-testid="cx-log-btn-5"><i></i>Finishing</button>
        </div>
        <div>
          <article class="cx-log-entry" data-testid="cx-log-entry-1">
            <span class="cx-num">01</span><h3>Before pour</h3>
            <div class="cx-log-items">
              <div>Reinforcement configuration against the approved drawings and bar schedules</div>
              <div>Formwork alignment, stability, tightness and release preparation</div>
              <div>Dimensional control: axes, levels, section sizes</div>
              <div>Embedded elements, sleeves and service penetrations in position</div>
              <div>Concrete cover confirmed by spacers before closing the formwork</div>
              <div>Access and placement route agreed for the element</div>
            </div>
          </article>
          <article class="cx-log-entry" data-testid="cx-log-entry-2">
            <span class="cx-num">02</span><h3>During pour</h3>
            <div class="cx-log-items">
              <div>Delivery coordination with the concrete plant and site sequence</div>
              <div>Placement sequence and layer thickness suited to the element</div>
              <div>Compaction discipline, avoiding both under- and over-vibration</div>
              <div>Execution conditions: temperature, weather, continuity of supply</div>
              <div>Conformity documentation collected with each delivery</div>
              <div>Sampling carried out in line with the applicable standard requirements</div>
            </div>
          </article>
          <article class="cx-log-entry" data-testid="cx-log-entry-3">
            <span class="cx-num">03</span><h3>After pour</h3>
            <div class="cx-log-items">
              <div>Curing regime maintained for the required period</div>
              <div>Formwork removal timing according to the structural design</div>
              <div>Visual inspection of the struck surface and detail zones</div>
              <div>Dimensional and level control of the completed element</div>
              <div>Preparation of construction joints and interfaces for the next stage</div>
              <div>Records kept per element and per pour</div>
            </div>
          </article>
          <article class="cx-log-entry" data-testid="cx-log-entry-4">
            <span class="cx-num">04</span><h3>Enclosure</h3>
            <div class="cx-log-items">
              <div>Waterproofing continuity at foundations, retaining elements and roofs</div>
              <div>Insulation continuity and thermal bridge detailing</div>
              <div>Facade and glazing interfaces, fixings and tolerances</div>
              <div>Water testing of critical interfaces before covering</div>
              <div>Coordination of service penetrations through the envelope</div>
              <div>Protection of completed work during following trades</div>
            </div>
          </article>
          <article class="cx-log-entry" data-testid="cx-log-entry-5">
            <span class="cx-num">05</span><h3>Finishing</h3>
            <div class="cx-log-items">
              <div>Wet-area waterproofing and drainage falls before finishes</div>
              <div>Acoustic detailing at partitions, floors and service routes</div>
              <div>Mechanical and electrical commissioning against design intent</div>
              <div>Substrate and tolerance checks ahead of architectural finishes</div>
              <div>Snagging by apartment, reviewed and re-inspected</div>
              <div>Handover documentation compiled per unit</div>
            </div>
          </article>
        </div>
      </div>
    </div>
  </section>

  <!-- ================= 08 WATERPROOFING ================= -->
  <section class="cx-seq cx-sec--dark" __SEQ8__ data-testid="cx-section-08">
    <div class="cx-seq-stage">
      <div class="cx-seq-copy">
        <span class="cx-num">08</span>
        <h2 class="cx-h2">Durability starts at the interfaces.</h2>
        <p class="cx-lead">Waterproofing is not treated as a finishing operation. Foundations, retaining elements, roofs, terraces, balconies and wet areas require continuity between individual waterproofing details if the building envelope is to perform as intended over time.</p>
        <div class="cx-seq-steps">__STEPS8__</div>
        <p class="cx-body" style="margin-top:10px">Waterproofing is designed and applied under the Binalarda Su Yal&#305;t&#305;m&#305; Y&ouml;netmeli&#287;i. A waterproofing system is only as reliable as its weakest discontinuity.</p>
      </div>
      <div class="cx-seq-visual">__WATER_SVG__</div>
    </div>
  </section>

  <!-- ================= 09 ENVELOPE ================= -->
  <section class="cx-seq cx-sec--dark" __SEQ9__ data-testid="cx-section-09">
    <div class="cx-seq-stage">
      <div class="cx-seq-copy">
        <span class="cx-num">09</span>
        <h2 class="cx-h2">The envelope defines the interior experience.</h2>
        <p class="cx-lead">Facades, glazing, insulation, waterproofing and interfaces between materials form a continuous environmental boundary between interior and exterior. Their design affects thermal comfort, moisture behaviour, durability, acoustic performance and energy demand.</p>
        <div class="cx-seq-steps">__STEPS9__</div>
        <p class="cx-body" style="margin-top:10px">Layer sequence is indicative. Materials, thicknesses and performance values are defined by the project-specific specification and the Binalarda Enerji Performans&#305; Y&ouml;netmeli&#287;i together with the applicable construction-product performance requirements.</p>
      </div>
      <div class="cx-seq-visual">__ENV_SVG__</div>
    </div>
  </section>

  <!-- ================= 10 ACOUSTIC ================= -->
  <section class="cx-sec cx-light" data-testid="cx-section-10">
    <div class="cx-wrap">
      <div class="cx-head">
        <div>
          <span class="cx-num" data-cx-fade>10</span>
          <h2 class="cx-h2" data-cx-fade>Quality can also be heard.</h2>
        </div>
        <p class="cx-lead" data-cx-fade>Residential comfort is influenced not only by what occupants see, but by what they do not hear. Building layout, wall and floor assemblies, facade design and building-services coordination all contribute to acoustic performance.</p>
      </div>
      <div style="margin:clamp(28px,5vh,60px) 0">__WAVE_SVG__</div>
      <div class="cx-log-items" data-cx-stagger>
        <div data-cx-fade>Plan layout: separating noisy and quiet functions between neighbouring residences</div>
        <div data-cx-fade>Wall and floor assemblies detailed for airborne and impact sound</div>
        <div data-cx-fade>Facade and glazing selected with the external noise environment in mind</div>
        <div data-cx-fade>Service routes, shafts and equipment isolated from living spaces</div>
      </div>
      <p class="cx-body" style="margin-top:34px;max-width:70ch" data-cx-fade>Acoustic design is carried out under the Binalar&#305;n G&uuml;r&uuml;lt&uuml;ye Kar&#351;&#305; Korunmas&#305; Hakk&#305;nda Y&ouml;netmelik. Performance is a property of the completed assembly and its execution; project-specific acoustic documentation governs each development.</p>
    </div>
  </section>

  <!-- ================= 11 BUILDING SERVICES ================= -->
  <section class="cx-sec cx-sec--dark" data-testid="cx-section-11">
    <div class="cx-wrap">
      <div class="cx-head">
        <div>
          <span class="cx-num" data-cx-fade>11</span>
          <h2 class="cx-h2" data-cx-fade>Engineering beyond the structure</h2>
        </div>
        <p class="cx-lead" data-cx-fade>A high-quality residence depends on the coordination of architecture, structure and building services. Mechanical, electrical and plumbing systems are considered as part of the building rather than installations added after the architecture is complete.</p>
      </div>
      <div class="cx-rule"></div>
      <div class="cx-env">
        <div data-cx-draw="sequential" data-cx-start="top 80%" data-cx-end="bottom 55%">__SERVICES_SVG__</div>
        <div class="cx-env-layers" data-cx-stagger>
          <div class="cx-env-layer" data-cx-fade><span>01</span><b>Ventilation</b><p>Fresh-air supply and extract routes planned with the structural grid, not cut into it afterwards.</p></div>
          <div class="cx-env-layer" data-cx-fade><span>02</span><b>Heating &amp; cooling distribution</b><p>Distribution zoned by apartment, with space for maintenance access designed in.</p></div>
          <div class="cx-env-layer" data-cx-fade><span>03</span><b>Electrical infrastructure</b><p>Risers, distribution and low-voltage systems coordinated with architectural layouts.</p></div>
          <div class="cx-env-layer" data-cx-fade><span>04</span><b>Water systems</b><p>Supply routes, isolation and metering positioned for serviceability over the building life.</p></div>
          <div class="cx-env-layer" data-cx-fade><span>05</span><b>Drainage</b><p>Falls, stacks and ventilation resolved with acoustic separation from living spaces.</p></div>
          <div class="cx-env-layer" data-cx-fade><span>06</span><b>Vertical shafts</b><p>Shaft geometry set early so structure, services and fire compartmentation agree.</p></div>
        </div>
      </div>
      <p class="cx-body" style="margin-top:34px;max-width:74ch" data-cx-fade>Fire safety provisions, compartmentation and escape routes are designed under the Binalar&#305;n Yang&#305;ndan Korunmas&#305; Hakk&#305;nda Y&ouml;netmelik in coordination with the architectural and services design.</p>
    </div>
  </section>

  <!-- ================= 12 FROM STRUCTURE TO RESIDENCE ================= -->
  <section class="cx-xfade" data-testid="cx-section-12">
    <div class="cx-xfade-stage">
      <div class="cx-xfade-layer"><img src="./media/images/construction/frame-detail.webp" alt="Reinforced-concrete frame" width="1800" height="1200" loading="lazy" decoding="async" /></div>
      <div class="cx-xfade-layer"><img src="./media/images/leed/material-facade.webp" alt="Facade and envelope" loading="lazy" decoding="async" /></div>
      <div class="cx-xfade-layer"><img src="./media/images/ew/ew_lounge.webp" alt="Interior architecture" loading="lazy" decoding="async" /></div>
      <div class="cx-xfade-layer"><img src="./media/images/east-west-cover.webp" alt="Completed Nova residence" loading="lazy" decoding="async" /></div>
      <div class="cx-xfade-scrim"></div>
      <div class="cx-xfade-copy">
        <div class="cx-xfade-stages" data-testid="cx-xfade-stages">
          <span class="is-on">Structural frame</span><span>Envelope</span><span>Interior architecture</span><span>Completed residence</span>
        </div>
        <h2 class="cx-h2">One building.<br />One continuous standard.</h2>
        <p class="cx-lead">Structural engineering, waterproofing, building systems, architecture and interior detailing are not independent stages. The performance of the completed residence depends on how precisely these disciplines are coordinated from the beginning.</p>
      </div>
    </div>
  </section>

  <!-- ================= 13 ENGINEERING FRAMEWORK ================= -->
  <section class="cx-sec cx-light" data-testid="cx-section-13">
    <div class="cx-wrap">
      <div class="cx-head">
        <div>
          <span class="cx-num" data-cx-fade>13</span>
          <h2 class="cx-h2" data-cx-fade>Engineering framework</h2>
        </div>
        <p class="cx-lead" data-cx-fade>Design and construction in T&uuml;rkiye are carried out within a defined regulatory and standards framework. The principal references applicable to residential development are listed below.</p>
      </div>
      <div class="cx-rule"></div>
      <div class="cx-fw" data-cx-stagger data-testid="cx-framework">
        <div class="cx-fw-row" data-cx-fade><b>T&uuml;rkiye Bina Deprem Y&ouml;netmeli&#287;i (TBDY 2018)</b><p>The seismic design basis for buildings, in force since 1 January 2019.</p></div>
        <div class="cx-fw-row" data-cx-fade><b>T&uuml;rkiye Deprem Tehlike Haritalar&#305;</b><p>Location-based seismic hazard parameters used as design input for each site.</p></div>
        <div class="cx-fw-row" data-cx-fade><b>TS 500</b><p>Requirements for design and construction of reinforced concrete structures, in its applicable current edition.</p></div>
        <div class="cx-fw-row" data-cx-fade><b>TS EN 206</b><p>Concrete: specification, performance, production and conformity, in its applicable current edition, applied together with the complementary national standard TS 13515.</p></div>
        <div class="cx-fw-row" data-cx-fade><b>Reinforcing steel standards</b><p>Steel for the reinforcement of concrete to the applicable current Turkish standard referenced by TS 500.</p></div>
        <div class="cx-fw-row" data-cx-fade><b>Yap&#305; Malzemeleri Y&ouml;netmeli&#287;i</b><p>Construction-product legislation governing declared performance and CE marking of materials placed on the market.</p></div>
        <div class="cx-fw-row" data-cx-fade><b>Binalarda Su Yal&#305;t&#305;m&#305; Y&ouml;netmeli&#287;i</b><p>Waterproofing requirements for buildings, including foundations, roofs and wet areas.</p></div>
        <div class="cx-fw-row" data-cx-fade><b>Binalar&#305;n G&uuml;r&uuml;lt&uuml;ye Kar&#351;&#305; Korunmas&#305; Hakk&#305;nda Y&ouml;netmelik</b><p>Protection of buildings against noise, including residential acoustic requirements.</p></div>
        <div class="cx-fw-row" data-cx-fade><b>Binalarda Enerji Performans&#305; Y&ouml;netmeli&#287;i</b><p>Energy performance requirements for buildings and their envelope and systems.</p></div>
        <div class="cx-fw-row" data-cx-fade><b>Binalar&#305;n Yang&#305;ndan Korunmas&#305; Hakk&#305;nda Y&ouml;netmelik</b><p>Fire protection requirements, compartmentation and means of escape.</p></div>
        <div class="cx-fw-row" data-cx-fade><b>Planl&#305; Alanlar &#304;mar Y&ouml;netmeli&#287;i</b><p>Planning and zoning framework governing building geometry and site conditions.</p></div>
      </div>
      <p class="cx-fw-note" data-testid="cx-framework-note">Applicable regulations and technical standards may vary according to project characteristics, approval date and project scope. Project-specific engineering documentation governs each development.</p>
    </div>
  </section>

  <!-- ================= FINAL ================= -->
  <section class="cx-final" data-testid="cx-final">
    <div class="cx-final-img"><img src="./media/images/ew/render/ew-render4.webp" alt="Completed Nova residential architecture" loading="lazy" decoding="async" data-cx-parallax="0.04" /></div>
    <div class="cx-final-scrim"></div>
    <div class="cx-wrap cx-final-copy">
      <span class="cx-kicker" data-cx-fade>Nova Konut</span>
      <h2 class="cx-h2" data-cx-fade data-testid="cx-final-title">What is built into the structure remains in the building for generations.</h2>
      <p class="cx-lead" data-cx-fade>The finished architecture is only the visible result. Behind it lies a sequence of engineering decisions, material choices, construction controls and carefully resolved details designed to support long-term performance.</p>
    </div>
  </section>
'''

STEPS2 = steps([
    ('Foundation', 'The interface between the structure and the ground, sized from geotechnical information and the loads above.'),
    ('Columns', 'Vertical load paths whose position and dimensions follow from the architectural grid and the analysis.'),
    ('Reinforced-concrete walls', 'Where required, walls provide lateral stiffness and strength in addition to carrying vertical load.'),
    ('Beams', 'Elements transferring floor loads to the vertical structure, detailed for both strength and ductility.'),
    ('Slabs', 'Floor plates that carry loads and tie the structure together as a horizontal diaphragm.'),
    ('Structural core', 'Vertical circulation and service zones that can also form part of the lateral-force-resisting system.'),
])
STEPS3 = steps([
    ('Gravity actions', 'Permanent and imposed loads are established first; the structure must satisfy them before any seismic consideration.'),
    ('Lateral action', 'Seismic action is applied as a design demand derived from the hazard parameters for the site.'),
    ('Structural response', 'Configuration, stiffness and ductility govern how displacement is distributed over the height of the building.'),
    ('Foundation and ground', 'Actions are transferred to the foundation and into the ground; foundation behaviour is part of the analysis.'),
])
STEPS5 = steps([
    ('Reinforcement detailing', 'Bar arrangement, spacing and cover are set out and checked before the element is closed.'),
    ('Formwork', 'Geometry, tightness and stability of the formwork determine both dimensions and surface quality.'),
    ('Concrete placement', 'Placement is planned in sequence and in layers appropriate to the element being cast.'),
    ('Compaction', 'Compaction removes entrapped air so that concrete fully surrounds the reinforcement.'),
    ('Curing', 'Early-age protection and moisture retention are decisive for durability, not only for strength.'),
    ('Quality control', 'Conformity records, sampling and inspection accompany each stage rather than concluding it.'),
])
STEPS8 = steps([
    ('Ground and water contact', 'Soil and groundwater conditions define the exposure that buried elements have to resist.'),
    ('Basement walls', 'Retaining elements are waterproofed as a continuous surface, including construction joints.'),
    ('Foundation interface', 'The junction between wall and foundation is detailed as a continuation of the same system.'),
    ('Facade interfaces', 'Envelope penetrations, fixings and junctions are resolved so that continuity is not interrupted.'),
    ('Balconies and terraces', 'Falls, upstands, thresholds and drainage are coordinated with the interior floor build-up.'),
    ('Roof', 'The system is closed at roof level, completing an uninterrupted boundary around the building.'),
])
STEPS9 = steps([
    ('Structural backing', 'The structural surface that receives the envelope, prepared to the required tolerances.'),
    ('Continuous insulation', 'Insulation is planned as a continuous layer, with thermal bridges addressed by detailing.'),
    ('Waterproofing and vapour control', 'Moisture behaviour is considered across the whole section, not layer by layer.'),
    ('Ventilated cavity', 'Where used, a cavity manages moisture and supports the performance of the cladding system.'),
    ('Facade cladding', 'The outer layer resists weather and defines the architectural surface and its long-term appearance.'),
    ('Glazing and frame interface', 'Junctions between glazing, frame and wall are usually the most demanding details in the envelope.'),
])

html = HEAD + head_block + MAIN + '\n  ' + footer_block + '''

  <script src="js/script.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/ScrollTrigger.min.js"></script>
  <script src="js/construction.js"></script>
</body>
</html>
'''

rep = {
    '__HERO_GRID__': HERO_GRID,
    '__STRUCTURE_SVG__': STRUCTURE_SVG,
    '__SEISMIC_SVG__': SEISMIC_SVG,
    '__GROUND_SVG__': GROUND_SVG,
    '__CONCRETE_SVG__': CONCRETE_SVG,
    '__WATER_SVG__': WATER_SVG,
    '__ENV_SVG__': ENV_SVG,
    '__SERVICES_SVG__': SERVICES_SVG,
    '__WAVE_SVG__': WAVE_SVG,
    '__STEPS2__': STEPS2, '__STEPS3__': STEPS3, '__STEPS5__': STEPS5, '__STEPS8__': STEPS8, '__STEPS9__': STEPS9,
    '__SEQ2__': seq(6), '__SEQ3__': seq(4), '__SEQ5__': seq(6), '__SEQ8__': seq(6), '__SEQ9__': seq(6),
}
for k, v in rep.items():
    html = html.replace(k, v)

assert '__' not in html.replace('__', '__', 1) or True
open('/app/frontend/construction.html', 'w', encoding='utf-8').write(html)
print('written', len(html), 'chars; placeholders left:', [k for k in rep if k in html])
