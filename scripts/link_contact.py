"""Point the existing CONTACT menu item at the new contact page across all pages."""
import pathlib

frontend = pathlib.Path(__file__).resolve().parent.parent / "frontend"

OLD = '<li class="menu-item"><a class="menu-link" href="#register"><span class="label">CONTACT</span></a></li>'
NEW = ('<li class="menu-item"><a class="menu-link" href="contact.html" data-testid="menu-link-contact">'
       '<span class="label">CONTACT</span></a></li>')

hits = 0
for page in sorted(frontend.glob("*.html")):
    src = page.read_text(encoding="utf-8")
    if OLD not in src:
        continue
    page.write_text(src.replace(OLD, NEW), encoding="utf-8")
    hits += 1
    print("updated", page.name)
print("contact menu links:", hits)
