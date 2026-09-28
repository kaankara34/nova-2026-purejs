"""One-off: bottom footer legal links + accurate cookie information notice on every page."""
import glob

OLD_LINKS = """          <a href="#">Data Privacy Statement</a>
          <a href="#">Anti slavery and human trafficking statement</a>"""
NEW_LINKS = """          <a href="privacy-notice.html">Privacy Notice</a>
          <a href="cookie-notice.html">Cookie Notice</a>
          <a href="ethical-principles.html">Ethical Principles &amp; Labour Standards</a>"""

OLD_BANNER = """      <p>We use cookies to enhance your browsing experience, serve personalized content, and analyze our traffic. By clicking &ldquo;Accept&rdquo;, you consent to our <a href="#" style="text-decoration:underline;">use of cookies</a>.</p>"""
NEW_BANNER = """      <p>This website uses only the technologies needed to display its pages, remember this notice and load the fonts, libraries, news and map content it shows. No analytics, advertising or profiling technologies are used. Details are in our <a href="cookie-notice.html" style="text-decoration:underline;">Cookie Notice</a>.</p>"""

OLD_HEADING = '<h6>We value our privacy</h6>'
NEW_HEADING = '<h6>Cookies and browser storage</h6>'

OLD_BTNS = ('<a href="#" class="find-more">FIND OUT MORE</a>',
            '<a href="cookie-notice.html" class="find-more">COOKIE NOTICE</a>')

counts = {'links': 0, 'banner': 0, 'privacy_checkbox': 0}
for path in sorted(glob.glob('/app/frontend/*.html')):
    src = open(path, encoding='utf-8').read()
    out = src
    if OLD_LINKS in out:
        out = out.replace(OLD_LINKS, NEW_LINKS)
        counts['links'] += 1
    if OLD_BANNER in out:
        out = out.replace(OLD_BANNER, NEW_BANNER).replace(OLD_HEADING, NEW_HEADING)
        out = out.replace(*OLD_BTNS)
        counts['banner'] += 1
    # registration forms: point the consent checkbox at the real notice
    before = out
    out = out.replace('agree to the <a href="#">Privacy Policy</a>',
                      'agree to the <a href="privacy-notice.html">Privacy Notice</a>')
    if out != before:
        counts['privacy_checkbox'] += 1
    if out != src:
        open(path, 'w', encoding='utf-8').write(out)
print(counts)
