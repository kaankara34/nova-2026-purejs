"""Generate the three English legal / corporate information pages from the
shared NOVA page skeleton (header, side menu, footer, cookie notice) so the
navbar and footer stay byte-identical to the rest of the site."""
import re

SRC = '/app/frontend/newsroom.html'
src = open(SRC, encoding='utf-8').read()

prefix = src[:src.index('</aside>') + len('</aside>')]
suffix = src[src.index('  <footer'):]
suffix = suffix.replace('  <script src="js/news.js"></script>\n', '')

# head rewrites
prefix = prefix.replace('  <link rel="stylesheet" href="css/newsroom.css" />',
                        '  <link rel="stylesheet" href="css/legal.css" />')
prefix = re.sub(r'  <script type="application/ld\+json">.*?</script>\n', '', prefix, flags=re.S)

KEP = 'novakonut@hs01.kep.tr'


def head(page_title, description, canonical):
    out = prefix
    out = out.replace('<title>NOVA Journal | Art, Architecture &amp; Urban Transformation</title>',
                      '<title>%s</title>' % page_title)
    out = out.replace(
        '<meta name="description" content="Selected news and perspectives on art, architecture, construction, Kadıköy and urban transformation from trusted sources in Türkiye and around the world." />',
        '<meta name="description" content="%s" />' % description)
    out = out.replace('<meta property="og:title" content="NOVA Journal | Art, Architecture &amp; Urban Transformation" />',
                      '<meta property="og:title" content="%s" />' % page_title)
    out = out.replace(
        '<meta property="og:description" content="Selected news and perspectives on art, architecture, construction, Kadıköy and urban transformation from trusted sources in Türkiye and around the world." />',
        '<meta property="og:description" content="%s" />' % description)
    out = out.replace('<link rel="canonical" href="newsroom.html" />',
                      '<link rel="canonical" href="%s" />' % canonical)
    return out


def section(num, title, body):
    return ('        <section class="legal-section">\n'
            '          <h2><span class="legal-num">%s</span> %s</h2>\n%s'
            '        </section>\n' % (num, title, body))


def page(title, updated, lead, sections):
    return (
        '\n  <main class="legal" id="legalTop">\n'
        '    <section class="legal-head">\n'
        '      <div class="legal-wrap">\n'
        '        <p class="legal-eyebrow">Legal &amp; Corporate</p>\n'
        '        <h1 class="legal-title">%s</h1>\n'
        '        <p class="legal-updated">Last updated: %s</p>\n'
        '        <p class="legal-lead">%s</p>\n'
        '      </div>\n'
        '    </section>\n\n'
        '    <section class="legal-body">\n'
        '      <div class="legal-wrap">\n'
        '      <article class="legal-article">\n'
        '%s'
        '      </article>\n'
        '      </div>\n'
        '    </section>\n'
        '  </main>\n\n' % (title, updated, lead, sections))


P = lambda t: '          <p>%s</p>\n' % t

# ----------------------------------------------------------------- privacy
privacy_sections = ''.join([
    section('01', 'Data controller and scope',
            P('This notice explains how NOVA KONUT İNŞAAT YATIRIM A.Ş. (&ldquo;NOVA&rdquo; or the &ldquo;Company&rdquo;) processes personal data through its website, in accordance with the information obligation under Article 10 of Turkish Personal Data Protection Law No. 6698 (&ldquo;Law No. 6698&rdquo;).') +
            '          <dl class="legal-meta">\n'
            '            <dt>Data controller</dt>\n'
            '            <dd>NOVA KONUT İNŞAAT YATIRIM A.Ş.</dd>\n'
            '            <dt>Registered electronic notification address (KEP)</dt>\n'
            '            <dd><a href="mailto:%s">%s</a></dd>\n'
            '          </dl>\n' % (KEP, KEP) +
            P('The KEP address is a formal electronic notification channel and is used for legal notifications and requests submitted through that channel.') +
            P('This notice covers website visitors and individuals who contact the Company through the website. Separate notices may apply to employees, job applicants, suppliers and contractual counterparties.')),

    section('02', 'Data collected and collection methods',
            P('The registration of interest and contact forms on this website collect the following information:') +
            '          <ul class="legal-list">\n'
            '            <li>full name;</li>\n'
            '            <li>country dialling code and telephone number;</li>\n'
            '            <li>e-mail address;</li>\n'
            '            <li>the project you are interested in;</li>\n'
            '            <li>how you heard about NOVA;</li>\n'
            '            <li>your choice as to whether you wish to hear about news and offers;</li>\n'
            '            <li>your confirmation that you have read this notice.</li>\n'
            '          </ul>\n' +
            P('The website does not contain a free-text message field, and no other personal data is requested by its forms. Any additional information you choose to include in electronic correspondence you send us is also processed.') +
            P('When the website is requested, the web server that delivers it may generate standard technical records such as an IP address, request time and browser or device information. These records are created by the hosting infrastructure that serves the website. Personal data is therefore collected electronically, through the website forms, through electronic communications you send us and through technical records generated when the website operates.') +
            P('The website does not set cookies of its own; it stores two items in your browser&rsquo;s local storage. Further information appears in the <a href="cookie-notice.html">Cookie Notice</a>.')),

    section('03', 'Purposes and legal grounds',
            P('Information submitted in an enquiry is processed to receive and respond to your request, provide project or service information you ask for, arrange meetings or visits where requested, and manage related correspondence.') +
            P('Depending on the nature of the request, the applicable grounds under Article 5(2) of Law No. 6698 may include processing directly necessary for the establishment or performance of a contract, or the Company&rsquo;s legitimate interests where these do not prejudice the individual&rsquo;s fundamental rights and freedoms.') +
            P('Correspondence and relevant records may be processed for the establishment, exercise or protection of rights. Technical and security records may be processed to maintain website operation and security, resolve errors and prevent misuse, on the applicable legal ground for the particular activity. Personal data may also be processed where necessary to comply with a legal obligation.') +
            P('Submitting an enquiry does not by itself constitute consent to receive advertising or promotional electronic messages. The news and offers preference on the form is a separate, optional choice, and such communications remain subject to the applicable consent and opt-out requirements.')),

    section('04', 'Recipients and international transfers',
            P('To the extent necessary for the purposes described above, personal data may be processed by providers that operate the website, its hosting, e-mail systems, forms or technical support; by service providers handling an enquiry on NOVA&rsquo;s behalf; and by competent public authorities or courts where disclosure is legally required. Enquiries submitted through the website are directed to the Company&rsquo;s enquiry mailbox at <a href="mailto:iletisim@nova.istanbul">iletisim@nova.istanbul</a>.') +
            P('In addition, displaying this website requires your browser to connect directly to a small number of third-party providers whose infrastructure is operated outside Türkiye:') +
            '          <ul class="legal-list">\n'
            '            <li>Google (Google Fonts) — delivery of the typefaces used across the website;</li>\n'
            '            <li>jsDelivr — delivery of the animation libraries used on some pages;</li>\n'
            '            <li>GitHub, Inc. — delivery of the static news file shown in the NOVA Journal;</li>\n'
            '            <li>the original news publishers — the illustration of a news item, when the publisher provides one;</li>\n'
            '            <li>OpenStreetMap Foundation — the location map embedded on The Residences East West page.</li>\n'
            '          </ul>\n' +
            P('Because these providers operate their infrastructure outside Türkiye, loading their content results in connection data such as your IP address, request time and browser information being transmitted abroad. Transfers of personal data abroad are governed by Article 9 of Law No. 6698. The Company reviews these connections and the applicable transfer conditions; no separate transfer of your enquiry content is made to these providers.')),

    section('05', 'Retention and disposal',
            P('Personal data is retained for the period necessary for its processing purpose and applicable legal obligations. The nature of the enquiry, any continuing legal relationship and periods relevant to potential legal claims are taken into account. When the grounds for processing and retention cease to apply, the data is deleted, destroyed or anonymised in accordance with applicable law.')),

    section('06', 'Individual rights and requests',
            P('Subject to Article 11 of Law No. 6698, you may ask whether your personal data is processed, request information about its processing, learn its purpose and recipients, request correction of inaccurate or incomplete data, request deletion or destruction where the statutory conditions are met, and exercise your other rights under the Law.') +
            P('Requests may be submitted to NOVA KONUT İNŞAAT YATIRIM A.Ş. in accordance with the applicable request procedures. The Company&rsquo;s KEP address for submissions through that channel is <a href="mailto:%s">%s</a>. Requests are assessed within the applicable statutory period.' % (KEP, KEP))),
])

privacy = head('Website Privacy Notice | NOVA Konut',
               'How NOVA KONUT İNŞAAT YATIRIM A.Ş. processes personal data collected through this website, under Turkish Personal Data Protection Law No. 6698.',
               'privacy-notice.html') + page(
    'Website Privacy Notice', '28 September 2026',
    'This notice sets out how NOVA KONUT İNŞAAT YATIRIM A.Ş. processes personal data through this website, the purposes and legal grounds for that processing, the recipients involved and the rights available to individuals under Turkish Personal Data Protection Law No. 6698.',
    privacy_sections) + suffix

# ----------------------------------------------------------------- cookies
inventory_rows = [
    ('dg_cookie_ok<br /><span style="color:#8b8b8b">browser local storage</span>',
     'NOVA KONUT İNŞAAT YATIRIM A.Ş.',
     'Records that the cookie information notice shown at the bottom of the page has been dismissed, so that it is not displayed again on each visit.',
     'First-party',
     'Stored until you clear your browser storage; no expiry date is set.',
     'Art. 5(2) — necessary for the operation of the website and the Company&rsquo;s legitimate interests'),
    ('nova-news-feed:en<br />nova-news-feed:tr<br /><span style="color:#8b8b8b">browser local storage</span>',
     'NOVA KONUT İNŞAAT YATIRIM A.Ş.',
     'Stores the last valid NOVA Journal news file so that articles can be displayed immediately and the file is not downloaded again on every page view; refreshed in the background after 30 minutes.',
     'First-party',
     'Stored until you clear your browser storage; the stored copy is replaced when the feed is refreshed.',
     'Art. 5(2) — necessary for the operation of the website and the Company&rsquo;s legitimate interests'),
    ('Google Fonts<br /><span style="color:#8b8b8b">fonts.googleapis.com, fonts.gstatic.com</span>',
     'Google',
     'Delivers the typefaces used across the website.',
     'Third-party',
     'No cookie is set by this request; the font files are cached by your browser.',
     'Art. 5(2) — necessary for the presentation of the website'),
    ('jsDelivr<br /><span style="color:#8b8b8b">cdn.jsdelivr.net</span>',
     'jsDelivr',
     'Delivers the animation and 3D libraries used on the About, Build Beyond Living, Design, Construction, LEED and Contact pages.',
     'Third-party',
     'No cookie is set by this request; the files are cached by your browser.',
     'Art. 5(2) — necessary for the operation of those pages'),
    ('GitHub raw content<br /><span style="color:#8b8b8b">raw.githubusercontent.com</span>',
     'GitHub, Inc.',
     'Delivers the static news file that the NOVA Journal displays on the homepage, the Journal index and article pages.',
     'Third-party',
     'No cookie is set by this request.',
     'Art. 5(2) — necessary for the operation of the Journal'),
    ('News illustration images<br /><span style="color:#8b8b8b">the publisher&rsquo;s own image servers</span>',
     'The original news publisher',
     'Displays the illustration of a news item when the publisher provides one; if the image cannot be loaded, a NOVA category image stored on this website is shown instead.',
     'Third-party',
     'No storage is set by NOVA; any storage set by the publisher is governed by that publisher&rsquo;s own policy.',
     'Art. 5(2) — necessary for the presentation of the Journal'),
    ('OpenStreetMap map embed<br /><span style="color:#8b8b8b">openstreetmap.org, tile.openstreetmap.org</span>',
     'OpenStreetMap Foundation',
     'Displays the location map embedded on The Residences East West page.',
     'Third-party',
     'Any cookie or storage set by the provider inside its own embedded frame is governed by that provider&rsquo;s policy.',
     'Art. 5(2) — necessary for the presentation of the location map'),
]

table = ('          <div class="legal-table-scroll">\n'
         '            <table class="legal-table">\n'
         '              <caption>Technologies verified on this website in September 2026. No analytics, advertising, profiling or social media tracking technology was found.</caption>\n'
         '              <thead><tr><th scope="col">Name</th><th scope="col">Provider</th><th scope="col">Purpose</th><th scope="col">Party</th><th scope="col">Duration</th><th scope="col">Legal ground</th></tr></thead>\n'
         '              <tbody>\n')
for row in inventory_rows:
    table += '                <tr>' + ''.join('<td>%s</td>' % c for c in row) + '</tr>\n'
table += ('              </tbody>\n'
          '            </table>\n'
          '          </div>\n')

cookie_sections = ''.join([
    section('01', 'Data controller and scope',
            P('This notice explains the cookies and similar technologies used on the website operated by NOVA KONUT İNŞAAT YATIRIM A.Ş. The Company&rsquo;s registered electronic notification address (KEP) is <a href="mailto:%s">%s</a>.' % (KEP, KEP)) +
            P('Cookies are small data files that may be stored on your device through your browser when you visit a website. Browser storage and other technologies may serve similar functions. This website does not set cookies of its own; it uses two items of browser local storage and loads a limited number of third-party files, all of which are listed below.')),

    section('02', 'Purposes and legal grounds',
            P('The technologies used on this website are limited to those necessary for its core operation and presentation: remembering that the cookie information notice has been dismissed, storing the last valid news file so it does not have to be downloaded on every page view, and loading the typefaces, libraries, news file, news images and location map that the pages display.') +
            P('These technologies are used where an appropriate legal ground under Article 5(2) of Turkish Law No. 6698 applies. No analytics, advertising, profiling or social media tracking technology is used on this website, and no technology requiring separate explicit consent has been identified. Accordingly, the website does not present an optional-cookie consent panel; the notice shown at the bottom of the page is informational only.')),

    section('03', 'Technology inventory', table +
            P('If NOVA later introduces analytics, advertising or other optional technologies, this inventory will be updated and a genuine preference mechanism will be provided before those technologies are enabled.')),

    section('04', 'Third parties and international transfers',
            P('Loading third-party content establishes a direct connection between your device and the relevant provider. The embedded map, the typefaces, the animation libraries, the static news file and publisher-supplied news images are delivered in this way, so connection data such as your IP address, request time and browser information is transmitted to the provider concerned.') +
            P('The providers listed in the inventory above (Google, jsDelivr, GitHub, OpenStreetMap Foundation and the individual news publishers) operate their infrastructure outside Türkiye. Loading their content therefore involves a transfer of connection data abroad, which is governed by Article 9 of Law No. 6698. The Company does not transfer enquiry form content to these providers.')),

    section('05', 'Managing choices',
            P('Because the website does not use optional technologies requiring consent, there is no optional-cookie panel to configure. You can manage or delete cookies and browser storage at any time through your browser settings, and you can prevent third-party content from loading using your browser or an extension.') +
            P('Clearing browser storage will cause the cookie information notice to be displayed again and the news file to be downloaded on the next visit. Blocking the third-party files listed above may prevent the typefaces, the news items or the location map from being displayed correctly; the rest of the website continues to work.')),

    section('06', 'Rights and contact',
            P('Requests concerning rights under Article 11 of Law No. 6698 may be submitted to NOVA KONUT İNŞAAT YATIRIM A.Ş. using the applicable request procedures. The Company&rsquo;s KEP address is <a href="mailto:%s">%s</a>.' % (KEP, KEP)) +
            P('For general information about the processing of personal data through this website, please read the <a href="privacy-notice.html">Website Privacy Notice</a>.')),
])

cookies = head('Cookie Notice | NOVA Konut',
               'The cookies, browser storage and third-party content verified on the NOVA Konut website, their purposes, providers and duration.',
               'cookie-notice.html') + page(
    'Cookie Notice', '28 September 2026',
    'This notice lists the cookies, browser storage and third-party content actually used on the NOVA Konut website, together with the purpose, provider, duration and legal ground for each of them.',
    cookie_sections) + suffix

# ----------------------------------------------------------------- ethics
ethics_sections = ''.join([
    section('01', 'Scope',
            P('NOVA KONUT İNŞAAT YATIRIM A.Ş. regards lawful working conditions, respect for human dignity, and occupational health and safety as fundamental principles in its construction and real estate development activities. This statement sets out the Company&rsquo;s expectations in its own operations and its relationships with contractors and suppliers.') +
            P('This is a statement of corporate principles. It is not a statutory statement made under the United Kingdom Modern Slavery Act, and it does not indicate that the Company is subject to a reporting obligation under that legislation.')),

    section('02', 'Working conditions',
            P('NOVA expects recruitment, pay, working hours and other employment conditions to comply with applicable law. Forced labour, human trafficking and child labour contrary to applicable law are not accepted. Workers&rsquo; statutory rights and dignity must be respected.')),

    section('03', 'Occupational health and safety',
            P('Identifying risks, taking appropriate precautions, informing workers and delivering relevant training are essential on construction sites and in other workplaces. NOVA fulfils its own legal obligations and expects contractors and subcontractors to comply with the occupational health and safety obligations applicable to their activities. This statement does not alter any party&rsquo;s responsibilities under law.')),

    section('04', 'Contractors and suppliers',
            P('NOVA expects contractors and suppliers to comply with the employment, social security, and occupational health and safety laws relevant to their work. Reported concerns are assessed in light of their nature and the available information. Contractual or legal steps may be taken where appropriate.') +
            P('This statement is not a guarantee that every supplier is continuously audited or that no non-compliance can occur.')),

    section('05', 'Reporting concerns',
            P('Specific concerns relating to these principles may be raised through the Company&rsquo;s published contact channels: by e-mail to <a href="mailto:iletisim@nova.istanbul">iletisim@nova.istanbul</a>, through the <a href="contact.html">Contact</a> page, or by formal electronic notification to the Company&rsquo;s KEP address <a href="mailto:%s">%s</a>. The website does not operate a separate anonymous whistleblowing line.' % (KEP, KEP)) +
            P('Personal data submitted in a report is processed to assess the concern and, where necessary, to carry out related procedures in accordance with applicable data protection law. The right to contact competent authorities in cases involving immediate danger or a suspected offence remains unaffected.')),
])

ethics = head('Ethical Principles &amp; Labour Standards | NOVA Konut',
              'NOVA KONUT İNŞAAT YATIRIM A.Ş. corporate principles on lawful working conditions, occupational health and safety, and expectations of contractors and suppliers.',
              'ethical-principles.html') + page(
    'Ethical Principles &amp; Labour Standards', '28 September 2026',
    'NOVA KONUT İNŞAAT YATIRIM A.Ş. regards lawful working conditions, respect for human dignity, and occupational health and safety as fundamental principles of its construction and real estate development activities. This statement sets out the Company&rsquo;s expectations in its own operations and in its relationships with contractors and suppliers.',
    ethics_sections) + suffix

for name, content in [('privacy-notice.html', privacy),
                      ('cookie-notice.html', cookies),
                      ('ethical-principles.html', ethics)]:
    open('/app/frontend/' + name, 'w', encoding='utf-8').write(content)
    print('wrote', name, len(content))
