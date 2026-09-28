"""Generate the Speak Up (anonymous reporting) and Careers pages on the shared
NOVA page skeleton. Both forms are frontend-complete; no backend is connected."""
import sys

sys.path.insert(0, '/app/scripts')
import build_legal_pages as base  # noqa: E402

KEP = base.KEP
MAIL = base.MAIL


def head(title, description, canonical, extra_css, extra_js):
    out = base.head(title, description, canonical)
    out = out.replace('  <link rel="stylesheet" href="css/legal.css" />',
                      '  <link rel="stylesheet" href="css/legal.css" />\n'
                      '  <link rel="stylesheet" href="css/%s" />' % extra_css)
    suffix = base.suffix.replace('  <script src="js/script.js"></script>',
                                 '  <script src="js/script.js"></script>\n'
                                 '  <script src="js/%s" defer></script>' % extra_js)
    return out, suffix


# ==================================================================== SPEAK UP
speak_body = """
  <main class="legal action-page" id="speakUpTop">
    <section class="legal-head">
      <div class="legal-wrap">
        <p class="legal-eyebrow">Ethics &amp; Compliance</p>
        <h1 class="legal-title">Speak Up</h1>
        <p class="legal-subtitle">Confidential and Anonymous Reporting</p>
        <p class="legal-lead">NOVA KONUT İNŞAAT YATIRIM A.Ş. asks anyone who becomes aware of a serious concern on its projects &mdash; employees, workers, contractors, suppliers, residents and neighbours &mdash; to report it. Reports are assessed on their substance, and no name is required to submit one.</p>
      </div>
    </section>

    <section class="legal-body">
      <div class="legal-wrap">
        <div class="notice-block notice-block--alert" role="note" data-testid="speakup-status-notice">
          <h2 class="notice-title">Online submission is not yet active</h2>
          <p>The reporting form below is complete, but the channel that receives and stores reports is not yet in operation. Anything entered in the form <strong>is not sent and is not saved</strong>. Until the channel is activated, please use one of the identified channels listed under &ldquo;How to report now&rdquo;, or return to this page later.</p>
        </div>

        <article class="legal-article">
          <section class="legal-section">
            <h2><span class="legal-num">01</span> What to report</h2>
            <p>Speak Up is for serious concerns relating to NOVA&rsquo;s activities, projects, employees, contractors and suppliers, including:</p>
            <ul class="legal-list">
              <li>occupational health and safety concerns on site or in the workplace;</li>
              <li>unlawful or unethical conduct;</li>
              <li>harassment or discrimination;</li>
              <li>coercion, forced labour or any restriction of a person&rsquo;s freedom to leave work;</li>
              <li>corruption, bribery or a serious conflict of interest;</li>
              <li>serious concerns involving a contractor, subcontractor or supplier.</li>
            </ul>
            <p>Please describe what happened as specifically as you can. A concrete description &mdash; what, where, when and who was involved &mdash; can be assessed; a general allegation often cannot.</p>
          </section>

          <section class="legal-section">
            <h2><span class="legal-num">02</span> Emergencies</h2>
            <p>Speak Up is not an emergency service and is not monitored continuously. If there is an immediate risk to life, health or safety, or a suspected offence in progress, contact the competent emergency or public authorities first. In Türkiye the general emergency number is 112.</p>
          </section>

          <section class="legal-section">
            <h2><span class="legal-num">03</span> How to report now</h2>
            <p>Until the online channel is active, the following channels are available. <strong>Both identify you to the Company</strong>, because your e-mail address or electronic notification identity is visible to the recipient. Neither is an anonymous channel.</p>
            <dl class="legal-meta">
              <dt>E-mail (identified)</dt>
              <dd><a href="mailto:__MAIL__?subject=Speak%20Up%20%E2%80%94%20Report%20%E2%80%94%20NOVA%20Konut">__MAIL__</a></dd>
              <dt>Registered electronic notification, KEP (identified, formal)</dt>
              <dd><a href="mailto:__KEP__">__KEP__</a></dd>
            </dl>
            <p>If you need to report anonymously, do not use these channels. You may also raise a concern directly with the competent public authority.</p>
          </section>

          <section class="legal-section">
            <h2><span class="legal-num">04</span> Anonymity and how reports are handled</h2>
            <p>The form asks for no name, e-mail address or telephone number, and you can submit it without any contact details. If you choose to provide a contact method so that the Company can ask follow-up questions, that information may identify you.</p>
            <p>NOVA does not promise absolute anonymity, encrypted transmission or a case reference number, because the channel that would provide those features is not yet in operation. When it is activated, this page will state exactly how reports are transmitted, who receives them, how long they are kept and what protections apply. Retaliation against a person who raises a concern in good faith is not accepted.</p>
          </section>

          <section class="legal-section" id="reportForm">
            <h2><span class="legal-num">05</span> Report form</h2>
            <p class="form-intro">All fields except the description are optional. Nothing you type is stored in your browser or sent anywhere while the channel is inactive &mdash; you can use &ldquo;Copy report text&rdquo; to keep your own copy.</p>

            <form class="nova-ui-form" id="reportFormEl" novalidate onsubmit="return false;" data-testid="report-form">
              <div class="form-alert" id="reportErrorSummary" role="alert" tabindex="-1" hidden data-testid="report-error-summary"></div>

              <div class="form-row">
                <label class="form-label" for="reportCategory">Category <span class="req">*</span></label>
                <select id="reportCategory" name="category" class="form-control" required data-testid="report-category">
                  <option value="">Please select a category</option>
                  <option>Occupational health and safety</option>
                  <option>Unlawful or unethical conduct</option>
                  <option>Harassment or discrimination</option>
                  <option>Coercion or forced labour</option>
                  <option>Corruption or conflict of interest</option>
                  <option>Concern involving a contractor or supplier</option>
                  <option>Other serious concern</option>
                </select>
                <p class="form-error" id="reportCategoryError" hidden></p>
              </div>

              <div class="form-row">
                <label class="form-label" for="reportDescription">Description of the concern <span class="req">*</span></label>
                <p class="form-hint" id="reportDescriptionHint">Describe what happened, where and when, and who was involved. Minimum 60 characters, maximum 5,000.</p>
                <textarea id="reportDescription" name="description" class="form-control" rows="9" required minlength="60" maxlength="5000" aria-describedby="reportDescriptionHint reportDescriptionCount" data-testid="report-description"></textarea>
                <p class="form-count" id="reportDescriptionCount" aria-live="polite">0 / 5,000 characters</p>
                <p class="form-error" id="reportDescriptionError" hidden></p>
              </div>

              <div class="form-grid-2">
                <div class="form-row">
                  <label class="form-label" for="reportDate">Approximate date of the incident</label>
                  <input type="date" id="reportDate" name="incidentDate" class="form-control" data-testid="report-date" />
                  <p class="form-hint">Leave empty if you do not know.</p>
                </div>
                <div class="form-row">
                  <label class="form-label" for="reportLocation">Project or location</label>
                  <input type="text" id="reportLocation" name="location" class="form-control" maxlength="140" placeholder="Site, building or district" data-testid="report-location" />
                </div>
              </div>

              <fieldset class="form-row form-fieldset">
                <legend class="form-label">Is the issue ongoing?</legend>
                <div class="form-radios">
                  <label><input type="radio" name="ongoing" value="Yes" data-testid="report-ongoing-yes" /> Yes</label>
                  <label><input type="radio" name="ongoing" value="No" data-testid="report-ongoing-no" /> No</label>
                  <label><input type="radio" name="ongoing" value="Unknown" data-testid="report-ongoing-unknown" /> I do not know</label>
                </div>
              </fieldset>

              <div class="form-row">
                <label class="form-label" for="reportInvolved">People or organisations involved</label>
                <p class="form-hint">Roles, company names or descriptions are enough; only include what you consider necessary.</p>
                <textarea id="reportInvolved" name="involved" class="form-control" rows="3" maxlength="600" data-testid="report-involved"></textarea>
              </div>

              <div class="form-row">
                <label class="form-label" for="reportFile">Supporting document (optional)</label>
                <p class="form-hint" id="reportFileHint">PDF, JPG, PNG, DOC or DOCX, up to 10 MB. The file stays on your device while the channel is inactive.</p>
                <div class="file-field">
                  <input type="file" id="reportFile" name="attachment" class="file-input" accept=".pdf,.jpg,.jpeg,.png,.doc,.docx" aria-describedby="reportFileHint" data-testid="report-file" />
                  <label class="file-button" for="reportFile">Choose file</label>
                  <span class="file-name" id="reportFileName" aria-live="polite">No file selected</span>
                  <button type="button" class="file-remove" id="reportFileRemove" hidden data-testid="report-file-remove">Remove</button>
                </div>
                <p class="form-error" id="reportFileError" hidden></p>
              </div>

              <div class="form-row">
                <label class="form-label" for="reportContact">Contact method for follow-up (optional)</label>
                <p class="form-hint">An e-mail address, telephone number or any other way of reaching you. <strong>Providing it may identify you.</strong> Leave it empty to remain anonymous.</p>
                <input type="text" id="reportContact" name="contact" class="form-control" maxlength="180" data-testid="report-contact" />
              </div>

              <div class="form-actions">
                <button type="submit" class="form-submit" id="reportSubmit" data-testid="report-submit">Submit report</button>
                <button type="button" class="form-secondary" id="reportCopy" data-testid="report-copy">Copy report text</button>
              </div>

              <p class="form-result" id="reportResult" role="status" aria-live="polite" hidden data-testid="report-result"></p>
            </form>
          </section>
        </article>
      </div>
    </section>
  </main>

""".replace('__MAIL__', MAIL).replace('__KEP__', KEP)

speak_head, speak_suffix = head(
    'Speak Up | Confidential and Anonymous Reporting | NOVA Konut',
    'Report occupational health and safety, ethical, labour or supplier concerns relating to NOVA Konut projects. No name is required.',
    'anonymous-reporting.html', 'action-pages.css', 'speak-up.js')

# ==================================================================== CAREERS
careers_body = """
  <main class="legal action-page" id="careersTop">
    <section class="legal-head">
      <div class="legal-wrap">
        <p class="legal-eyebrow">Careers</p>
        <h1 class="legal-title">Careers at NOVA Konut</h1>
        <p class="legal-lead">NOVA KONUT İNŞAAT YATIRIM A.Ş. develops high-end residential buildings along the Kadıköy&ndash;Bağdat Caddesi corridor in Istanbul. Our projects are delivered by small, experienced teams in which architects, engineers and site staff work directly with one another. We look for people who take responsibility for the quality of what is built and who make sound decisions on site.</p>
      </div>
    </section>

    <section class="legal-body">
      <div class="legal-wrap">
        <div class="notice-block notice-block--alert" role="note" data-testid="careers-status-notice">
          <h2 class="notice-title">Online applications are not yet being received</h2>
          <p>The application form below is complete, but the system that receives applications and CVs is not yet in operation. Anything entered in the form <strong>is not sent and is not saved</strong>. Until it is active, please apply by e-mail using the details under &ldquo;Apply by e-mail&rdquo;.</p>
        </div>

        <article class="legal-article">
          <section class="legal-section" id="openPositions">
            <h2><span class="legal-num">01</span> Open positions</h2>
            <ul class="vacancy-list">
              <li class="vacancy-item">
                <div class="vacancy-item-main">
                  <h3 class="vacancy-item-title">Construction Site Manager (Architect)</h3>
                  <p class="vacancy-item-meta">Kadıköy / Bağdat Caddesi, Istanbul &middot; Full time &middot; On site</p>
                </div>
                <a class="vacancy-item-link" href="#vacancyDetail">View details</a>
              </li>
            </ul>
            <p class="form-hint">No other positions are open at present.</p>
          </section>

          <section class="legal-section" id="vacancyDetail">
            <h2><span class="legal-num">02</span> Construction Site Manager (Architect)</h2>
            <dl class="legal-meta">
              <dt>Location</dt>
              <dd>Kadıköy / Bağdat Caddesi, Istanbul</dd>
              <dt>Discipline</dt>
              <dd>Architecture &mdash; construction site management</dd>
              <dt>Reports to</dt>
              <dd>Project management</dd>
            </dl>
            <p>The role is a hands-on site management position on NOVA&rsquo;s high-end residential construction projects. The selected architect will run the site from structural works through finishing, handover and the occupancy-permit stage, and will be expected to take practical decisions on site rather than direct the work from a distance.</p>
            <p>Appointment as a legally designated şantiye şefi is not granted by meeting the requirements of this advertisement. Professional eligibility and project-specific legal conditions are assessed separately in accordance with the applicable legislation and chamber requirements.</p>

            <h3>Requirements</h3>
            <ul class="legal-list">
              <li>University degree in Architecture.</li>
              <li>At least 10 years of active, hands-on construction-site experience.</li>
              <li>Direct personal management of both structural and finishing works.</li>
              <li>Practical experience in quantity take-offs, cost estimates and progress-payment assessments.</li>
              <li>Strong subcontractor management, construction scheduling and site coordination.</li>
              <li>Ability to interpret drawings, resolve details and translate designs into correct site execution.</li>
              <li>Ability to prepare work programmes, anticipate delay risks and take corrective action.</li>
              <li>Ability to establish and manage the entire site organisation.</li>
              <li>Active on-site application of occupational health and safety requirements.</li>
              <li>Effective use of AutoCAD and Microsoft Office.</li>
              <li>Disciplined, accountable and solution-oriented approach.</li>
              <li>Active driver with a valid Class B driving licence.</li>
              <li>Good English reading, writing and speaking ability where relevant to the role.</li>
            </ul>

            <h3>Responsibilities</h3>
            <ul class="legal-list">
              <li>Direct all assigned construction activities on site.</li>
              <li>Organise daily site operations.</li>
              <li>Prepare and review quantity take-offs and progress-payment assessments.</li>
              <li>Coordinate subcontractors, trades and site teams.</li>
              <li>Monitor progress against the work programme and address delays.</li>
              <li>Implement quality, occupational health and safety, and construction standards on site.</li>
              <li>Report regularly and transparently to project management.</li>
              <li>Coordinate delivery from structural construction through finishing and occupancy-permit stages within the responsibilities of the role.</li>
            </ul>
          </section>

          <section class="legal-section" id="applyByEmail">
            <h2><span class="legal-num">03</span> Apply by e-mail</h2>
            <p>Applications are currently accepted by e-mail. Send your CV as an attachment to the address below using this exact subject line:</p>
            <dl class="legal-meta">
              <dt>Address</dt>
              <dd><a href="mailto:__MAIL__?subject=Application%20%E2%80%94%20Construction%20Site%20Manager%20(Architect)%20%E2%80%94%20NOVA%20Konut">__MAIL__</a></dd>
              <dt>Subject</dt>
              <dd>Application &mdash; Construction Site Manager (Architect) &mdash; NOVA Konut</dd>
            </dl>
            <p>Opening the link prepares a message in your own e-mail programme. It cannot attach your CV for you: please attach the file yourself before sending. Your application reaches NOVA only when you send that e-mail &mdash; opening the mail programme does not submit anything to this website.</p>
            <p><a class="mail-cta" href="mailto:__MAIL__?subject=Application%20%E2%80%94%20Construction%20Site%20Manager%20(Architect)%20%E2%80%94%20NOVA%20Konut" data-testid="careers-mail-cta">Open e-mail application</a></p>
          </section>

          <section class="legal-section" id="applicationForm">
            <h2><span class="legal-num">04</span> Application form</h2>
            <p class="form-intro">The form is ready for the application system that will be connected later. While it is inactive, nothing you enter is transmitted or stored.</p>

            <form class="nova-ui-form" id="careersFormEl" novalidate onsubmit="return false;" data-testid="careers-form">
              <div class="form-alert" id="careersErrorSummary" role="alert" tabindex="-1" hidden data-testid="careers-error-summary"></div>

              <div class="form-grid-2">
                <div class="form-row">
                  <label class="form-label" for="appName">Full name <span class="req">*</span></label>
                  <input type="text" id="appName" name="fullName" class="form-control" required maxlength="120" autocomplete="name" data-testid="careers-name" />
                  <p class="form-error" id="appNameError" hidden></p>
                </div>
                <div class="form-row">
                  <label class="form-label" for="appEmail">E-mail address <span class="req">*</span></label>
                  <input type="email" id="appEmail" name="email" class="form-control" required maxlength="160" autocomplete="email" data-testid="careers-email" />
                  <p class="form-error" id="appEmailError" hidden></p>
                </div>
                <div class="form-row">
                  <label class="form-label" for="appPhone">Telephone <span class="req">*</span></label>
                  <input type="tel" id="appPhone" name="phone" class="form-control" required maxlength="40" autocomplete="tel" data-testid="careers-phone" />
                  <p class="form-error" id="appPhoneError" hidden></p>
                </div>
                <div class="form-row">
                  <label class="form-label" for="appCity">City <span class="req">*</span></label>
                  <input type="text" id="appCity" name="city" class="form-control" required maxlength="80" autocomplete="address-level2" data-testid="careers-city" />
                  <p class="form-error" id="appCityError" hidden></p>
                </div>
                <div class="form-row">
                  <label class="form-label" for="appPosition">Position</label>
                  <input type="text" id="appPosition" name="position" class="form-control" value="Construction Site Manager (Architect)" readonly data-testid="careers-position" />
                </div>
                <div class="form-row">
                  <label class="form-label" for="appYears">Years of active site experience <span class="req">*</span></label>
                  <input type="number" id="appYears" name="years" class="form-control" required min="0" max="60" step="1" inputmode="numeric" data-testid="careers-years" />
                  <p class="form-error" id="appYearsError" hidden></p>
                </div>
              </div>

              <div class="form-row">
                <label class="form-label" for="appExperience">Relevant residential projects and your responsibilities <span class="req">*</span></label>
                <p class="form-hint" id="appExperienceHint">Name the projects you managed on site, their scope and stage, and what you were personally responsible for. Minimum 80 characters, maximum 2,000.</p>
                <textarea id="appExperience" name="experience" class="form-control" rows="7" required minlength="80" maxlength="2000" aria-describedby="appExperienceHint appExperienceCount" data-testid="careers-experience"></textarea>
                <p class="form-count" id="appExperienceCount" aria-live="polite">0 / 2,000 characters</p>
                <p class="form-error" id="appExperienceError" hidden></p>
              </div>

              <div class="form-row">
                <label class="form-label" for="appCv">CV <span class="req">*</span></label>
                <p class="form-hint" id="appCvHint">PDF, DOC or DOCX, up to 10 MB. The file stays on your device while the system is inactive.</p>
                <div class="file-field">
                  <input type="file" id="appCv" name="cv" class="file-input" accept=".pdf,.doc,.docx" aria-describedby="appCvHint" data-testid="careers-cv" />
                  <label class="file-button" for="appCv">Choose CV</label>
                  <span class="file-name" id="appCvName" aria-live="polite">No file selected</span>
                  <button type="button" class="file-remove" id="appCvRemove" hidden data-testid="careers-cv-remove">Remove</button>
                </div>
                <p class="form-error" id="appCvError" hidden></p>
              </div>

              <div class="form-row form-check">
                <label><input type="checkbox" id="appPrivacy" name="privacy" required data-testid="careers-privacy" /> I have read the <a href="#applicantPrivacy">applicant privacy information</a> and I am submitting my application on that basis. <span class="req">*</span></label>
                <p class="form-error" id="appPrivacyError" hidden></p>
              </div>

              <div class="form-actions">
                <button type="submit" class="form-submit" id="careersSubmit" data-testid="careers-submit">Submit application</button>
              </div>

              <p class="form-result" id="careersResult" role="status" aria-live="polite" hidden data-testid="careers-result"></p>
            </form>
          </section>

          <section class="legal-section" id="applicantPrivacy">
            <h2><span class="legal-num">05</span> Applicant privacy information</h2>
            <p>NOVA KONUT İNŞAAT YATIRIM A.Ş. is the data controller for personal data submitted in a job application. Its registered electronic notification address (KEP) is <a href="mailto:__KEP__">__KEP__</a>.</p>
            <p><strong>Data processed.</strong> Your name, contact details, city, the position applied for, your stated years of site experience, the project and responsibility information you provide and the contents of the CV you send. Please do not include national identity numbers, health information, criminal-record data, biometric data, religious or political information, or other special categories of personal data; if you send such information it will not be used to assess your application.</p>
            <p><strong>Purposes and legal grounds.</strong> The data is processed to assess your suitability for the position, to contact you about the recruitment process and to manage that process. Under Article 5(2) of Law No. 6698 the applicable grounds may include processing directly necessary for the establishment of an employment contract and NOVA&rsquo;s legitimate interests in conducting recruitment, where these do not prejudice your fundamental rights and freedoms.</p>
            <p><strong>Recipients.</strong> Within NOVA, your application is available to the personnel involved in the recruitment decision. It may also be shared with information technology and communication service providers that operate the Company&rsquo;s e-mail and application infrastructure, and with competent authorities where legally required. Applications are not shared with third parties for their own purposes.</p>
            <p><strong>Retention.</strong> Applications are retained for the period necessary to conduct the recruitment process and to meet applicable legal obligations, after which they are deleted, destroyed or anonymised. The specific period is set out in the Company&rsquo;s internal retention schedule.</p>
            <p><strong>International transfers.</strong> Whether application data is transferred outside Türkiye depends on where the Company&rsquo;s e-mail and application infrastructure is operated. This is being verified; a transfer abroad requires a condition under Article 9 of Law No. 6698, and this notice will be updated once the position is confirmed. No assertion is made here that a particular transfer condition or safeguard is currently in place.</p>
            <p><strong>Your rights.</strong> You may exercise your rights under Article 11 of Law No. 6698, including access, correction and deletion, using the applicable request procedures; the Company&rsquo;s KEP address is <a href="mailto:__KEP__">__KEP__</a>. General information about the processing of personal data through this website is in the <a href="privacy-notice.html">Website Privacy Notice</a>.</p>
          </section>
        </article>
      </div>
    </section>
  </main>

""".replace('__MAIL__', MAIL).replace('__KEP__', KEP)

careers_head, careers_suffix = head(
    'Careers | Construction Site Manager (Architect) | NOVA Konut',
    'Open positions at NOVA KONUT İNŞAAT YATIRIM A.Ş., including Construction Site Manager (Architect) for high-end residential projects in Kadıköy, Istanbul.',
    'careers.html', 'action-pages.css', 'careers.js')

for name, content in [('anonymous-reporting.html', speak_head + speak_body + speak_suffix),
                      ('careers.html', careers_head + careers_body + careers_suffix)]:
    open('/app/frontend/' + name, 'w', encoding='utf-8').write(content)
    print('wrote', name, len(content))
