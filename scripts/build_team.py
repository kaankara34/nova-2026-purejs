import re, pathlib

about = pathlib.Path('/app/frontend/about.html').read_text()

def seg(start, end, s=about):
    i = s.index(start)
    j = s.index(end, i) + len(end)
    return s[i:j]

chrome_top = seg('<!-- ============================= TOP UTILITY BAR', '</aside>')
touch = seg('<!-- ============================= GET IN TOUCH (sticky CTA strip) ============================= -->', '</section>')
footer = seg('<footer class="site-footer">', '</footer>')

chrome_top = chrome_top.replace('<li><a href="#"><span class="label">TEAM</span></a></li>',
                                '<li><a href="team.html"><span class="label">TEAM</span></a></li>')

GROUPS = [
    ("Management", [
        ("Cem Aydın Erdoğmuş", "Chairman of the Board", "cem@nova.istanbul"),
        ("Selin Kavakçı", "Board Member / Development &amp; Feasibility", "selin@nova.istanbul"),
        ("Bora Tunçel", "Civil Engineer / Corporate Advisor", "bora@nova.istanbul"),
    ]),
    ("Finance", [
        ("Deniz Aksel", "Director of Finance &amp; Accounting", "deniz@nova.istanbul"),
        ("Merve Ilgaz", "Accounting &amp; Financial Affairs", "merve@nova.istanbul"),
        ("Tolga Sarıkaya", "Accounting &amp; Financial Affairs", "tolga@nova.istanbul"),
    ]),
    ("Architecture &amp; Design", [
        ("Ayşe Nur Demirtaş", "Senior Architect / Project Development", "ayse@nova.istanbul"),
        ("Kerem Yalçın", "Architect / Project &amp; Technical Design", "kerem@nova.istanbul"),
        ("Elif Su Barın", "Interior Architect / Finishes &amp; Decoration", "elif@nova.istanbul"),
        ("Murat Beşiktaşlı", "Architect / Design Office Director", "murat@nova.istanbul"),
    ]),
    ("Construction &amp; Engineering", [
        ("Onur Kaplan", "Civil Engineer / Operations Coordinator", "onur@nova.istanbul"),
        ("Pelin Ergün", "Civil Engineer / Technical Office Director", "pelin@nova.istanbul"),
        ("Hakan Doruk", "Civil Engineer / Site Manager", "hakan@nova.istanbul"),
        ("Emre Sarp Yıldırım", "Civil Engineer / Site Manager", "emre@nova.istanbul"),
        ("Nazlı Cengiz", "Construction Technician", "nazli@nova.istanbul"),
    ]),
]


def initials(name):
    parts = [p for p in name.split() if p]
    return (parts[0][0] + parts[-1][0]).upper()


def slug(text):
    t = text.replace('&amp;', 'and').lower()
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')


groups_html = []
for gi, (group, members) in enumerate(GROUPS, start=1):
    cards = []
    for mi, (name, role, mail) in enumerate(members, start=1):
        cards.append(f'''          <article class="tm-card" data-testid="team-card-{slug(group)}-{mi}">
            <span class="tm-monogram" aria-hidden="true">{initials(name)}</span>
            <div class="tm-info">
              <h3 class="tm-name">{name}</h3>
              <p class="tm-role">{role}</p>
              <a class="tm-mail" href="mailto:{mail}" data-testid="team-mail-{slug(group)}-{mi}">{mail}</a>
            </div>
          </article>''')
    groups_html.append(f'''      <section class="tm-group" data-testid="team-group-{slug(group)}">
        <div class="tm-group-label">
          <span class="tm-group-index">{gi:02d}</span>
          <h2 class="tm-group-title">{group}</h2>
        </div>
        <div class="tm-grid">
{chr(10).join(cards)}
        </div>
      </section>''')

page = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="theme-color" content="#0b0b0b" />
  <meta name="description" content="Our Team — the architects, engineers and finance professionals behind Nova Konut's residential developments in Istanbul." />
  <title>Our Team | Nova Konut</title>

  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600;700&family=Montserrat:wght@300;400;500;600;700&display=swap" rel="stylesheet" />

  <link rel="stylesheet" href="css/styles.css" />
  <link rel="stylesheet" href="css/projects.css" />
  <link rel="stylesheet" href="css/team.css" />
</head>
<body class="page-team">

  {chrome_top}

  <!-- ============================= TEAM INTRO ============================= -->
  <main class="tm-main">
    <header class="tm-intro">
      <span class="tm-eyebrow">Our People</span>
      <h1 class="tm-title" data-testid="team-page-title">Our Team</h1>
      <p class="tm-lead">The architects, engineers and finance professionals who design, build and steward every Nova Konut development.</p>
    </header>

{chr(10).join(groups_html)}
  </main>

  {touch}

  {footer}

  <script src="js/script.js"></script>
  <script src="js/team.js"></script>
</body>
</html>
'''

pathlib.Path('/app/frontend/team.html').write_text(page)
print('written', len(page))
