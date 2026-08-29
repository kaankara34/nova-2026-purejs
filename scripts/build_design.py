"""Assemble frontend/design.html from the shared NOVA chrome (about.html) + design_main.html."""
import pathlib
import re

root = pathlib.Path(__file__).resolve().parent.parent
about = (root / "frontend" / "about.html").read_text(encoding="utf-8")
main = (pathlib.Path(__file__).parent / "design_main.html").read_text(encoding="utf-8")

hero_marker = "  <!-- ============================= HERO ============================= -->"
foot_marker = "  <footer class=\"site-footer\">"

chrome = about.split(hero_marker)[0]
footer = foot_marker + about.split(foot_marker, 1)[1]

chrome = chrome.replace(
    '<title>About Us | Nova Konut</title>',
    '<title>Design | Nova Konut</title>')
chrome = re.sub(r'<meta name="description"[^>]*>',
                '<meta name="description" content="Design at Nova Konut — architectural proportion, spatial clarity, material integrity and disciplined detailing in Istanbul residential architecture." />',
                chrome, count=1)
chrome = chrome.replace('<meta name="theme-color" content="#0b0b0b" />',
                        '<meta name="theme-color" content="#F2EEE7" />')
chrome = chrome.replace('./media/images/about/about_hero.webp',
                        './media/images/design/hero.webp')
chrome = chrome.replace(
    '  <link rel="stylesheet" href="css/projects.css" />\n  <link rel="stylesheet" href="css/about.css" />',
    '  <link rel="stylesheet" href="css/design.css" />')
chrome = chrome.replace('<body class="page-about">', '<body class="page-design">')
chrome = chrome.replace('media/images/nova-logo.png', 'media/images/nova-logo-dark.png')
chrome = chrome.replace('<a class="menu-link" href="#"><span class="label">DESIGN</span></a>',
                        '<a class="menu-link" href="design.html" data-testid="menu-link-design"><span class="label">DESIGN</span></a>')

scripts = """
  <script src="js/script.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/ScrollTrigger.min.js"></script>
  <script src="js/design.js"></script>
</body>
</html>
"""

footer = footer.split('  <script src="js/script.js"></script>')[0].rstrip() + "\n" + scripts

out = chrome + main + "\n" + footer
(root / "frontend" / "design.html").write_text(out, encoding="utf-8")
print("design.html written:", len(out.splitlines()), "lines")
