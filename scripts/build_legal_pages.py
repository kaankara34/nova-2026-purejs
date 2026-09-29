"""Generate the three English legal / corporate information pages from the shared
NOVA page skeleton (header, side menu, footer, cookie notice).

Public text is deliberately concise: it describes categories of processing and of
service providers rather than naming every technical dependency. The verified
technical inventory is kept internally in /app/memory/technical-inventory.md."""
import re

SRC = '/app/frontend/newsroom.html'
src = open(SRC, encoding='utf-8').read()

prefix = src[:src.index('</aside>') + len('</aside>')]
suffix = src[src.index('  <footer'):]
suffix = suffix.replace('  <script src="js/news.js"></script>\n', '')

prefix = prefix.replace('  <link rel="stylesheet" href="css/newsroom.css" />',
                        '  <link rel="stylesheet" href="css/legal.css" />')
prefix = re.sub(r'  <script type="application/ld\+json">.*?</script>\n', '', prefix, flags=re.S)

KEP = 'novakonut@hs01.kep.tr'
MAIL = 'iletisim@nova.istanbul'


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


def P(t):
    return '          <p>%s</p>\n' % t


def UL(items):
    return ('          <ul class="legal-list">\n' +
            ''.join('            <li>%s</li>\n' % i for i in items) +
            '          </ul>\n')


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
            P('The KEP address is a formal electronic notification channel used for legal notifications and for requests submitted through that channel.') +
            P('This notice covers website visitors and individuals who contact the Company through the website. Separate notices apply to other relationships: job applicants are covered by the <a href="applicant-privacy-notice.html">Applicant Privacy Notice</a>, and reports made through <a href="anonymous-reporting.html">Speak Up</a> are covered by the information given on that page.')),

    section('02', 'Data we process and how it is collected',
            P('<strong>Information you provide.</strong> The registration of interest and contact forms collect your name, telephone number and country dialling code, e-mail address, the project you are interested in, how you heard about NOVA, your preference as to receiving news and offers, and your confirmation that you have read this notice. The forms contain no free-text message field; any further information you include in correspondence you send us is also processed.') +
            P('<strong>Technical information.</strong> When the website is requested, the infrastructure that delivers it may generate standard technical records such as an IP address, request time and browser or device information. The website sets no cookies of its own and uses no analytics, advertising or profiling technologies. It keeps one item in your browser&rsquo;s own storage so that news items do not have to be downloaded again on every page view; this is described in the <a href="cookie-notice.html">Cookie Notice</a>.')),

    section('03', 'Purposes and legal grounds',
            P('Information submitted in an enquiry is processed to receive and respond to your request, provide project or service information you ask for, arrange meetings or visits where requested, and manage related correspondence.') +
            P('Depending on the nature of the request, the applicable grounds under Article 5(2) of Law No. 6698 may include processing directly necessary for the establishment or performance of a contract, or the Company&rsquo;s legitimate interests where these do not prejudice the individual&rsquo;s fundamental rights and freedoms. Correspondence and related records may be processed for the establishment, exercise or protection of rights, and technical records to maintain the website&rsquo;s operation and security, resolve errors and prevent misuse. Personal data is also processed where necessary to comply with a legal obligation.') +
            P('Submitting an enquiry does not by itself constitute consent to receive advertising or promotional electronic messages. The news and offers preference is a separate, optional choice and such communications remain subject to the applicable consent and opt-out requirements.')),

    section('04', 'Recipients',
            P('Personal data is shared only to the extent necessary for the purposes above, with the following categories of recipient:') +
            UL(['information technology and communication service providers that operate the website, its hosting, e-mail and form infrastructure;',
                'professional advisers and service providers acting on NOVA&rsquo;s behalf in relation to an enquiry;',
                'competent public authorities and courts, where disclosure is legally required.']) +
            P('Enquiries submitted through the website are directed to the Company&rsquo;s enquiry mailbox at <a href="mailto:%s">%s</a>. NOVA does not sell personal data and does not share it for third-party advertising purposes.' % (MAIL, MAIL))),

    section('05', 'International transfers',
            P('Some of the technical resources used to display the website &mdash; typefaces, interface libraries, the news file and the embedded location map &mdash; are delivered by service providers whose infrastructure is located outside Türkiye. When your browser requests those resources, connection data such as your IP address, request time and browser information reaches the provider concerned. This is limited to connection data; the content of the forms you submit is not sent to these providers.') +
            P('Any transfer of personal data abroad is subject to the conditions set out in Article 9 of Law No. 6698. This notice does not assert that a particular transfer condition or safeguard applies to a given transfer. The Company is reducing avoidable third-party requests by serving static resources from its own infrastructure where the licence permits.')),

    section('06', 'Retention and disposal',
            P('Personal data is retained for the period necessary for its processing purpose and applicable legal obligations. The nature of the enquiry, any continuing legal relationship and periods relevant to potential legal claims are taken into account. When the grounds for processing and retention cease to apply, the data is deleted, destroyed or anonymised in accordance with applicable law. Specific retention periods are set out in the Company&rsquo;s internal retention schedule.')),

    section('07', 'Your rights',
            P('Subject to Article 11 of Law No. 6698, you may ask whether your personal data is processed, request information about its processing, learn its purpose and recipients, request correction of inaccurate or incomplete data, request deletion or destruction where the statutory conditions are met, and exercise your other rights under the Law.') +
            P('Requests may be submitted to NOVA KONUT İNŞAAT YATIRIM A.Ş. in accordance with the applicable request procedures; the Company&rsquo;s KEP address for submissions through that channel is <a href="mailto:%s">%s</a>. Requests are assessed within the applicable statutory period.' % (KEP, KEP))),
])

privacy = head('Website Privacy Notice | NOVA Konut',
               'How NOVA KONUT İNŞAAT YATIRIM A.Ş. processes personal data collected through this website, under Turkish Personal Data Protection Law No. 6698.',
               'privacy-notice.html') + page(
    'Website Privacy Notice', '28 September 2026',
    'This notice sets out how NOVA KONUT İNŞAAT YATIRIM A.Ş. processes personal data through this website, the purposes and legal grounds for that processing, the categories of recipient involved and the rights available to individuals under Turkish Personal Data Protection Law No. 6698.',
    privacy_sections) + suffix

# ----------------------------------------------------------------- cookies
table = ('          <div class="legal-table-scroll">\n'
         '            <table class="legal-table">\n'
         '              <caption>Technologies used on this website. No analytics, advertising, profiling or social media tracking technology is used.</caption>\n'
         '              <thead><tr><th scope="col">Technology</th><th scope="col">Type</th><th scope="col">Purpose</th><th scope="col">Duration</th></tr></thead>\n'
         '              <tbody>\n'
         '                <tr><td>News file cache</td><td>First-party browser local storage</td><td>Keeps the most recent NOVA Journal news file so that articles display immediately instead of being downloaded on every page view.</td><td>Replaced when the file is refreshed; held until you clear your browser storage.</td></tr>\n'
         '                <tr><td>Typefaces, interface libraries, news content and news images</td><td>Direct requests to service providers</td><td>Delivers the resources the pages display. These requests transmit connection data to the provider concerned; NOVA sets no cookie through them.</td><td>Browser caching only; no cookie set by NOVA.</td></tr>\n'
         '                <tr><td>Embedded location map (project pages)</td><td>Third-party embedded content</td><td>Displays the project location map. The map provider may set its own cookies or storage inside its frame under its own policy.</td><td>Determined by the map provider.</td></tr>\n'
         '              </tbody>\n'
         '            </table>\n'
         '          </div>\n')

cookie_sections = ''.join([
    section('01', 'Scope',
            P('This notice explains the cookies, browser storage and third-party requests used on the website operated by NOVA KONUT İNŞAAT YATIRIM A.Ş. The Company&rsquo;s registered electronic notification address (KEP) is <a href="mailto:%s">%s</a>.' % (KEP, KEP)) +
            P('Cookies are small data files that a website may store on your device through your browser; browser local storage keeps information in a similar way. Loading a resource from another organisation&rsquo;s servers does not necessarily store anything on your device, but it does send connection data to that organisation.')),

    section('02', 'What this website uses',
            P('This website sets no cookies of its own. It keeps one item in your browser&rsquo;s local storage &mdash; the most recent news file, so that it does not have to be downloaded on every page view. It also loads a limited number of resources, and one embedded map, from service providers in order to display its pages.') +
            P('No analytics, advertising, profiling or social media tracking technology is used, and no technology requiring separate consent is used. As there is no optional technology to switch on or off, the website presents no consent panel.')),

    section('03', 'Technologies used', table +
            P('Service providers may set their own cookies or storage within content they serve, under their own policies; NOVA does not control that storage. If an optional technology requiring consent is introduced in future, this notice will be updated and a genuine preference mechanism, with an equally accessible option to refuse, will be provided before it is enabled.')),

    section('04', 'Service providers and international transfers',
            P('Loading an external resource creates a direct connection between your device and the provider concerned, which transmits connection data such as your IP address, request time and browser information. Several of these providers operate their infrastructure outside Türkiye, so those requests involve connection data reaching a country other than Türkiye.') +
            P('Any transfer of personal data abroad is subject to the conditions set out in Article 9 of Law No. 6698. This notice does not assert that a particular transfer condition or safeguard applies to a given transfer. The content of the forms you submit through this website is not transmitted to these providers.')),

    section('05', 'Managing your browser',
            P('Because the website uses no optional technologies requiring consent, there is no preference panel to configure. You can delete or block cookies, browser storage and third-party content at any time through your browser settings or an extension.') +
            P('Clearing browser storage causes the news file to be downloaded again on your next visit. Blocking external resources may prevent the typefaces, news items or the location map from displaying correctly; the rest of the website continues to work.')),

    section('06', 'Rights and contact',
            P('Requests concerning rights under Article 11 of Law No. 6698 may be submitted to NOVA KONUT İNŞAAT YATIRIM A.Ş. using the applicable request procedures. The Company&rsquo;s KEP address is <a href="mailto:%s">%s</a>.' % (KEP, KEP)) +
            P('For general information about the processing of personal data through this website, please read the <a href="privacy-notice.html">Website Privacy Notice</a>.')),
])

cookies = head('Cookie Notice | NOVA Konut',
               'Cookies, browser storage and third-party requests used on the NOVA Konut website, their purpose and duration.',
               'cookie-notice.html') + page(
    'Cookie Notice', '28 September 2026',
    'This notice explains the cookies, browser storage and third-party requests actually used on the NOVA Konut website, what each of them is for and how you can control them.',
    cookie_sections) + suffix

# ----------------------------------------------------------------- ethics
ethics_sections = ''.join([
    section('01', 'Scope',
            P('NOVA KONUT İNŞAAT YATIRIM A.Ş. regards lawful working conditions, respect for human dignity, and occupational health and safety as fundamental principles in its construction and real estate development activities. This statement sets out the Company&rsquo;s expectations in its own operations and its relationships with contractors and suppliers.') +
            P('This is a statement of corporate principles. It is not a statutory statement made under the United Kingdom Modern Slavery Act and does not indicate that the Company is subject to a reporting obligation under that legislation.')),

    section('02', 'Working conditions',
            P('NOVA expects recruitment, pay, working hours and other employment conditions to comply with applicable law. Forced labour, human trafficking and child labour contrary to applicable law are not accepted. Workers&rsquo; statutory rights and dignity must be respected.')),

    section('03', 'Occupational health and safety',
            P('Identifying risks, taking appropriate precautions, informing workers and delivering relevant training are essential on construction sites and in other workplaces. NOVA fulfils its own legal obligations and expects contractors and subcontractors to comply with the occupational health and safety obligations applicable to their activities. This statement does not alter any party&rsquo;s responsibilities under law.')),

    section('04', 'Contractors and suppliers',
            P('NOVA expects contractors and suppliers to comply with the employment, social security, and occupational health and safety laws relevant to their work. Reported concerns are assessed in light of their nature and the available information, and contractual or legal steps may be taken where appropriate.') +
            P('This statement is not a guarantee that every supplier is continuously audited or that no non-compliance can occur.')),

    section('05', 'Raising a concern',
            P('Concerns relating to these principles can be raised through <a href="anonymous-reporting.html">Speak Up</a>, the Company&rsquo;s reporting page, which sets out what can be reported and how to do so.') +
            P('Personal data submitted in a report is processed to assess the concern and, where necessary, to carry out related procedures in accordance with applicable data protection law. The right to contact competent authorities in cases involving immediate danger or a suspected offence remains unaffected.')),
])

ethics = head('Ethical Principles &amp; Labour Standards | NOVA Konut',
              'NOVA KONUT İNŞAAT YATIRIM A.Ş. corporate principles on lawful working conditions, occupational health and safety, and expectations of contractors and suppliers.',
              'ethical-principles.html') + page(
    'Ethical Principles &amp; Labour Standards', '28 September 2026',
    'NOVA KONUT İNŞAAT YATIRIM A.Ş. regards lawful working conditions, respect for human dignity, and occupational health and safety as fundamental principles of its construction and real estate development activities. This statement sets out the Company&rsquo;s expectations in its own operations and in its relationships with contractors and suppliers.',
    ethics_sections) + suffix

# -------------------------------------------------------- applicant privacy
applicant_sections = ''.join([
    section('01', 'Data controller and scope',
            P('This notice explains how NOVA KONUT İNŞAAT YATIRIM A.Ş. (&ldquo;NOVA&rdquo; or the &ldquo;Company&rdquo;) processes the personal data of candidates who apply for a position, in accordance with the information obligation under Article 10 of Turkish Personal Data Protection Law No. 6698 (&ldquo;Law No. 6698&rdquo;).') +
            '          <dl class="legal-meta">\n'
            '            <dt>Data controller</dt>\n'
            '            <dd>NOVA KONUT İNŞAAT YATIRIM A.Ş.</dd>\n'
            '            <dt>Registered electronic notification address (KEP)</dt>\n'
            '            <dd><a href="mailto:%s">%s</a></dd>\n'
            '          </dl>\n' % (KEP, KEP) +
            P('It applies to applications made through the application form on a vacancy page and to applications sent by e-mail to the Company&rsquo;s application address. This notice is provided for information. It is not a consent form, and acknowledging that you have read it does not authorise processing that is not otherwise permitted under Law No. 6698.')),

    section('02', 'Data processed',
            P('The Company processes the information you choose to submit with your application:') +
            UL(['your name, e-mail address, telephone number and city;',
                'the position applied for and your stated years of active construction-site experience;',
                'the projects and responsibilities you describe;',
                'the contents of the CV or other document you attach, including the career, education and reference information it contains;',
                'the correspondence exchanged with you during the recruitment process.']) +
            P('Please do not include national identity numbers, health information, criminal-record data, biometric data, trade-union membership, religious or political information, or other special categories of personal data. Such information is not requested and is not used to assess an application.')),

    section('03', 'Purposes and legal grounds',
            P('Application data is processed to assess your suitability for the position applied for, to contact you about the recruitment process, to conduct interviews and evaluations, and to manage and keep a record of that process.') +
            P('Under Article 5(2) of Law No. 6698 the applicable grounds may include processing directly necessary for the establishment of an employment contract, and the Company&rsquo;s legitimate interests in conducting recruitment where these do not prejudice your fundamental rights and freedoms. Where a specific processing activity is not covered by such a ground, it is carried out only with your explicit consent, which you may withdraw at any time.')),

    section('04', 'Recipients',
            P('Application data is shared only to the extent necessary for the purposes above, with the following categories of recipient:') +
            UL(['the Company personnel involved in the recruitment decision for the position concerned;',
                'information technology and communication service providers that operate the Company&rsquo;s e-mail and application infrastructure;',
                'professional advisers acting on the Company&rsquo;s behalf, where relevant to the process;',
                'competent public authorities and courts, where disclosure is legally required.']) +
            P('Applications are not sold and are not shared with third parties for their own purposes, including advertising.')),

    section('05', 'International transfers',
            P('Any transfer of personal data abroad is subject to the conditions set out in Article 9 of Law No. 6698. This notice does not assert that a particular transfer condition or safeguard applies to a given transfer.')),

    section('06', 'Retention',
            P('Application data is retained for the period necessary to conduct the recruitment process for the position applied for and to meet the Company&rsquo;s applicable legal obligations, including periods relevant to potential legal claims. When the grounds for processing and retention cease to apply, the data is deleted, destroyed or anonymised in accordance with applicable law. The applicable periods are set out in the Company&rsquo;s internal retention schedule and can be requested using the contact details in this notice.')),

    section('07', 'Your rights',
            P('Subject to Article 11 of Law No. 6698, you may ask whether your personal data is processed, request information about its processing, learn its purpose and recipients, request correction of inaccurate or incomplete data, request deletion or destruction where the statutory conditions are met, and exercise your other rights under the Law. You may also ask the Company to withdraw your application from consideration.') +
            P('Requests may be submitted to NOVA KONUT İNŞAAT YATIRIM A.Ş. in accordance with the applicable request procedures; the Company&rsquo;s KEP address for submissions through that channel is <a href="mailto:%s">%s</a>. Requests are assessed within the applicable statutory period. General information about the processing of personal data through this website is in the <a href="privacy-notice.html">Website Privacy Notice</a>.' % (KEP, KEP))),
])

applicant = head('Applicant Privacy Notice | NOVA Konut',
                 'How NOVA KONUT İNŞAAT YATIRIM A.Ş. processes the personal data of job applicants under Turkish Personal Data Protection Law No. 6698.',
                 'applicant-privacy-notice.html') + page(
    'Applicant Privacy Notice', '28 September 2026',
    'This notice sets out how NOVA KONUT İNŞAAT YATIRIM A.Ş. processes the personal data of candidates who apply for a position, the purposes and legal grounds for that processing, the categories of recipient involved and the rights available under Turkish Personal Data Protection Law No. 6698.',
    applicant_sections) + suffix


if __name__ == '__main__':
    for name, content in [('privacy-notice.html', privacy),
                          ('cookie-notice.html', cookies),
                          ('ethical-principles.html', ethics),
                          ('applicant-privacy-notice.html', applicant)]:
        open('/app/frontend/' + name, 'w', encoding='utf-8').write(content)
        print('wrote', name, len(content))
