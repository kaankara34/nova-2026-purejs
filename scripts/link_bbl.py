"""Point the existing BUILD BEYOND LIVING menu item at the new page, and add a footer link next to DESIGN."""
import pathlib

frontend = pathlib.Path(__file__).resolve().parent.parent / "frontend"

MENU_OLD = '<li class="menu-item bb-living"><a class="menu-link" href="#"><span class="label">BUILD BEYOND LIVING</span></a></li>'
MENU_NEW = ('<li class="menu-item bb-living"><a class="menu-link" href="build-beyond-living.html" '
            'data-testid="menu-link-bbl"><span class="label">BUILD BEYOND LIVING</span></a></li>')

FOOT_OLD = '<a href="design.html" data-testid="footer-link-design">DESIGN</a>'
FOOT_NEW = (FOOT_OLD + '\n          '
            '<a href="build-beyond-living.html" data-testid="footer-link-bbl">BUILD BEYOND LIVING</a>')

menu_hits = foot_hits = 0
for page in sorted(frontend.glob("*.html")):
    src = page.read_text(encoding="utf-8")
    out = src
    if MENU_OLD in out:
        out = out.replace(MENU_OLD, MENU_NEW)
        menu_hits += 1
    if FOOT_OLD in out and 'footer-link-bbl' not in out:
        out = out.replace(FOOT_OLD, FOOT_NEW)
        foot_hits += 1
    if out != src:
        page.write_text(out, encoding="utf-8")
        print("updated", page.name)
print("menu links:", menu_hits, "footer links:", foot_hits)
