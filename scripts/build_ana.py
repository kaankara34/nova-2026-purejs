"""Builds the-apartments-ana.html / css / js from the Taç page.

The Ana page is a structural counterpart of Taç: same DOM, same grid, same
motion. Only the namespace (tac -> ana), the project identity and the palette
change. Taç's own files are read-only here.
Run:  python3 scripts/build_ana.py
"""
import re
from pathlib import Path

root = Path(__file__).resolve().parent.parent
fe = root / "frontend"

# ---------------------------------------------------------------- helpers
def mask(text, pieces, tag="M"):
    store = {}
    for i, piece in enumerate(pieces):
        if piece in text:
            key = "\u0000%s%d\u0000" % (tag, i)
            store[key] = piece
            text = text.replace(piece, key)
    return text, store


def unmask(text, store):
    for key, piece in store.items():
        text = text.replace(key, piece)
    return text


def rename(text):
    """tac namespace -> ana namespace (asset paths must be masked first)."""
    text = text.replace("page-tac", "page-ana")
    text = text.replace("tac-", "ana-")
    text = re.sub(r"\btac(?=[A-Z])", "ana", text)
    text = re.sub(r"\bTac(?=[A-Z])", "Ana", text)
    text = text.replace("--tac", "--ana")
    text = text.replace("TAÇ", "ANA").replace("Taç", "Ana")
    return text


ASSET_RE = re.compile(r"(?:\./)?media/[A-Za-z0-9_\-./+]+")

# ---------------------------------------------------------------- html
html = (fe / "the-apartments-tac.html").read_text(encoding="utf-8")

keep = [
    # the Taç entries in the shared navigation / footer must stay Taç
    '<li><a href="the-apartments-tac.html">The Apartments Taç</a></li>',
    '<img src="./media/images/menu-thumbs/tac-ai-render.webp" alt="The Apartments Taç" width="280" height="352" loading="eager" decoding="async" fetchpriority="high" />',
    '<img src="./media/images/logos/TAC_logo-tight.svg" alt="The Apartments Taç" width="180" height="44" loading="eager" decoding="async" />',
]
html, kept = mask(html, keep, "KEEP")
html, assets = mask(html, sorted(set(ASSET_RE.findall(html)), key=len, reverse=True), "ASSET")

html = rename(html)
html = unmask(html, assets)
html = unmask(html, kept)

# page identity
html = html.replace(
    "<title>The Apartments Ana | Nova Konut</title>",
    "<title>The Apartments Ana | Nova Konut</title>")
html = re.sub(r'<meta name="theme-color" content="[^"]*" />',
              '<meta name="theme-color" content="#281B23" />', html)
html = html.replace('href="css/the-apartments-tac.css"', 'href="css/the-apartments-ana.css"')
html = html.replace('src="js/the-apartments-tac.js"', 'src="js/the-apartments-ana.js"')

# project logo: intro lettermark
html = html.replace(
    'src="./media/images/logos/TAC_logo-tight.svg" width="300" height="100"',
    'src="./media/images/logos/ANA_logo-tight.svg" width="300" height="100"')

# links: the Ana entries now point at this page
html = html.replace('<li><a href="#">The Apartments Ana</a></li>',
                    '<li><a href="the-apartments-ana.html">The Apartments Ana</a></li>')
html = re.sub(
    r'<a href="#(?:projects)?" class="proj-card">(?:(?!</a>).)*?ANA_logo-tight\.svg(?:(?!</a>).)*?</a>',
    lambda m: re.sub(r'^<a href="#(?:projects)?"', '<a href="the-apartments-ana.html"', m.group(0)),
    html, flags=re.S)

# remaining project links inside this page only
html = html.replace('<li><a href="#">The Residences East West</a></li>',
                    '<li><a href="east-west.html">The Residences East West</a></li>')
for logo, target in (("EASTWEST_v2-tight.svg", "east-west.html"),
                     ("TAC_logo-tight.svg", "the-apartments-tac.html")):
    html = re.sub(
        r'<a href="#(?:projects)?" class="proj-card">(?:(?!</a>).)*?' + re.escape(logo) + r'(?:(?!</a>).)*?</a>',
        lambda m, t=target: re.sub(r'^<a href="#(?:projects)?"', '<a href="%s"' % t, m.group(0)),
        html, flags=re.S)

leftovers = re.findall(r'(?:class|id|data-testid|for|aria-controls)="[^"]*\btac[-A-Z]', html)
(fe / "the-apartments-ana.html").write_text(html, encoding="utf-8")
print("the-apartments-ana.html written: %d lines; %d namespace leftovers"
      % (len(html.splitlines()), len(leftovers)))

# ---------------------------------------------------------------- css
css = (fe / "css" / "the-apartments-tac.css").read_text(encoding="utf-8")
css, assets = mask(css, sorted(set(ASSET_RE.findall(css)), key=len, reverse=True), "ASSET")
css = rename(css)
css = unmask(css, assets)

# Taç greys/blacks -> Ana plum & ivory family (the light sections are then
# re-stated explicitly in ana_palette.css)
tone = [
    ("#0B0B0A", "#281B23"), ("#050505", "#281B23"), ("#0A0A0A", "#281B23"),
    ("#121311", "#3B2632"), ("#111210", "#3B2632"), ("#11110F", "#3B2632"),
    ("#1A1916", "#59404A"), ("#0b0d0e", "#281B23"),
    ("#FFFDF7", "#F3EFE7"), ("#F0EEE8", "#F3EFE7"), ("#F5F4EE", "#F3EFE7"),
    ("#E8E3D9", "#E8E0D4"), ("#E8E3D8", "#E8E0D4"),
    ("#AAA69D", "#B8AA9D"), ("#A7A39B", "#B8AA9D"),
    ("#A99A7B", "#8B7257"), ("#A79879", "#8B7257"),
    ("#6E6A61", "#6B5661"), ("#5D5A53", "#5A4650"),
    ("rgba(240, 238, 232,", "rgba(243, 239, 231,"),
    ("rgba(245, 244, 238,", "rgba(243, 239, 231,"),
    ("rgba(5, 5, 5,", "rgba(40, 27, 35,"),
    ("rgba(11, 11, 10,", "rgba(40, 27, 35,"),
    ("rgba(169, 154, 123,", "rgba(139, 114, 87,"),
    ("rgba(167, 152, 121,", "rgba(139, 114, 87,"),
]
for a, b in tone:
    css = css.replace(a, b)

palette = (root / "scripts" / "ana_palette.css").read_text(encoding="utf-8")
(fe / "css" / "the-apartments-ana.css").write_text(css.rstrip() + "\n\n" + palette, encoding="utf-8")
print("the-apartments-ana.css written; %d .tac- selectors left"
      % css.count(".tac-"))

# ---------------------------------------------------------------- js
js = (fe / "js" / "the-apartments-tac.js").read_text(encoding="utf-8")
js, assets = mask(js, sorted(set(ASSET_RE.findall(js)), key=len, reverse=True), "ASSET")
js = rename(js)
js = unmask(js, assets)
js = js.replace("/* The Apartments Ana", "/* The Apartments Ana")
(fe / "js" / "the-apartments-ana.js").write_text(js, encoding="utf-8")
print("the-apartments-ana.js written; %d tac references left" % len(re.findall(r"\btac", js, re.I)))
