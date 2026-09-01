"""Assemble frontend/contact.html from the shared NOVA chrome (about.html) + contact_main.html."""
import pathlib
import re

root = pathlib.Path(__file__).resolve().parent.parent
about = (root / "frontend" / "about.html").read_text(encoding="utf-8")
main = (pathlib.Path(__file__).parent / "contact_main.html").read_text(encoding="utf-8")

hero_marker = "  <!-- ============================= HERO ============================= -->"
foot_marker = "  <footer class=\"site-footer\">"

chrome = about.split(hero_marker)[0]
footer = foot_marker + about.split(foot_marker, 1)[1]

chrome = chrome.replace('<title>About Us | Nova Konut</title>', '<title>Contact | Nova Konut</title>')
chrome = re.sub(r'<meta name="description"[^>]*>',
                '<meta name="description" content="Contact Nova Konut — enquiries, project information and resident support, with offices on Bağdat Caddesi and in Etiler, Istanbul." />',
                chrome, count=1)
chrome = chrome.replace('<meta name="theme-color" content="#0b0b0b" />',
                        '<meta name="theme-color" content="#F1EBE3" />')
chrome = re.sub(r'\n *<link rel="preload"[^>]*>', '', chrome, count=1)
chrome = chrome.replace(
    '  <link rel="stylesheet" href="css/projects.css" />\n  <link rel="stylesheet" href="css/about.css" />',
    '  <link rel="stylesheet" href="css/contact.css" />')
chrome = chrome.replace('<body class="page-about">', '<body class="page-contact">')
chrome = chrome.replace('media/images/nova-logo.png', 'media/images/nova-logo-dark.png')
# the shared chrome carries a stray slash in the logo tag; keep this page well-formed
chrome = chrome.replace('class="logo-img" / decoding="async"', 'class="logo-img" decoding="async"')

scripts = """
  <script src="js/script.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/ScrollTrigger.min.js"></script>
  <script src="js/contact.js"></script>
</body>
</html>
"""

footer = footer.split('  <script src="js/script.js"></script>')[0].rstrip() + "\n" + scripts

out = chrome + main + "\n" + footer
assert 'css/contact.css' in out and 'page-contact' in out and 'about.css' not in out
(root / "frontend" / "contact.html").write_text(out, encoding="utf-8")
print("contact.html written:", len(out.splitlines()), "lines")
