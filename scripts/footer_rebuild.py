"""One-off: rebuild the footer (upper row, secondary nav, bottom legal row) and add
Speak Up / Careers to the side menu on every page."""
import glob
import re

OLD_GRID = re.compile(r'      <!-- 3 Column Links -->\n      <div class="footer-grid">.*?\n      </div>\n\n', re.S)
NEW_GRID = """      <!-- Discover Our Residences — editorial row -->
      <div class="footer-discover">
        <h3 class="footer-discover-title">Discover Our Residences</h3>
        <ul class="footer-discover-row">
          <li><a href="east-west.html"><span class="fd-name">The Residences East West</span><span class="fd-meta">&Ccedil;iftehavuzlar</span></a></li>
          <li><a href="the-apartments-tac.html"><span class="fd-name">The Apartments Ta&ccedil;</span><span class="fd-meta">Feneryolu</span></a></li>
          <li><a href="the-apartments-ana.html"><span class="fd-name">The Apartments Ana</span><span class="fd-meta">Caddebostan</span></a></li>
          <li><a href="projects.html"><span class="fd-name">View All Projects</span><span class="fd-meta">Ba&#287;dat Caddesi portfolio</span></a></li>
        </ul>
      </div>

"""

OLD_GLOBE = re.compile(r'          <div class="footer-globe-links">.*?</div>\n', re.S)

OLD_MENU_LINKS = re.compile(r'        <div class="footer-menu-links">.*?</div>\n', re.S)
NEW_MENU_LINKS = """        <div class="footer-menu-links">
          <a href="projects.html" data-testid="footer-link-portfolio">PORTFOLIO</a>
          <a href="newsroom.html" data-testid="footer-link-newsroom">NEWSROOM</a>
          <a href="design.html" data-testid="footer-link-design">DESIGN</a>
          <a href="build-beyond-living.html" data-testid="footer-link-bbl">BUILD BEYOND LIVING</a>
          <a href="#">AGENT CONNECT</a>
          <a href="#">INVESTOR RELATIONS</a>
          <a href="#">BLOGS</a>
          <a href="#">PRESS</a>
          <a href="careers.html" data-testid="footer-link-careers">CAREERS</a>
          <a href="anonymous-reporting.html" data-testid="footer-link-speakup">SPEAK UP</a>
        </div>
"""

OLD_BOTTOM = re.compile(r'        <div class="footer-bottom-links">.*?</div>\n', re.S)
NEW_BOTTOM = """        <div class="footer-bottom-links">
          <a href="index.html#register" data-testid="footer-link-getintouch">Get in Touch</a>
          <a href="privacy-notice.html">Privacy Notice</a>
          <a href="cookie-notice.html">Cookie Notice</a>
          <a href="ethical-principles.html">Ethical Principles &amp; Labour Standards</a>
        </div>
"""

MENU_ANCHOR = '          <li><a href="team.html"><span class="label">TEAM</span></a></li>'
MENU_NEW = MENU_ANCHOR + """
          <li><a href="careers.html" data-testid="menu-link-careers"><span class="label">CAREERS</span></a></li>
          <li><a href="anonymous-reporting.html" data-testid="menu-link-speakup"><span class="label">SPEAK UP</span></a></li>"""

stats = {'grid': 0, 'globe': 0, 'menu_links': 0, 'bottom': 0, 'side_menu': 0}
for path in sorted(glob.glob('/app/frontend/*.html')):
    src = open(path, encoding='utf-8').read()
    out = src

    if OLD_GRID.search(out):
        out = OLD_GRID.sub(NEW_GRID, out, count=1)
        stats['grid'] += 1
    if OLD_GLOBE.search(out):
        out = OLD_GLOBE.sub('', out, count=1)
        stats['globe'] += 1
    if OLD_MENU_LINKS.search(out):
        out = OLD_MENU_LINKS.sub(NEW_MENU_LINKS, out, count=1)
        stats['menu_links'] += 1
    if OLD_BOTTOM.search(out):
        out = OLD_BOTTOM.sub(NEW_BOTTOM, out, count=1)
        stats['bottom'] += 1
    if MENU_ANCHOR in out and 'menu-link-careers' not in out:
        out = out.replace(MENU_ANCHOR, MENU_NEW, 1)
        stats['side_menu'] += 1

    if out != src:
        open(path, 'w', encoding='utf-8').write(out)

print(stats)
