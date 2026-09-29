"""Generate the Careers landing page, the Construction Site Manager (Architect)
vacancy page and the Speak Up reporting page on the shared NOVA page skeleton.

Both forms are frontend-complete and visible. Their submission adapters
(js/careers.js, js/speak-up.js) have no endpoint configured yet, so nothing is
transmitted, stored or falsely confirmed. No visitor-facing text discusses that.
"""
import sys

sys.path.insert(0, '/app/scripts')
import build_legal_pages as base  # noqa: E402

KEP = base.KEP
MAIL = base.MAIL
SUBJECT = 'Application%20%E2%80%94%20Construction%20Site%20Manager%20(Architect)%20%E2%80%94%20NOVA%20Konut'
MAILTO = 'mailto:%s?subject=%s' % (MAIL, SUBJECT)


def head(title, description, canonical, extra_js=None):
    out = base.head(title, description, canonical)
    out = out.replace('  <link rel="stylesheet" href="css/legal.css" />',
                      '  <link rel="stylesheet" href="css/legal.css" />\n'
                      '  <link rel="stylesheet" href="css/action-pages.css" />')
    suffix = base.suffix
    if extra_js:
        suffix = suffix.replace('  <script src="js/script.js"></script>',
                                '  <script src="js/script.js"></script>\n'
                                '  <script src="js/%s" defer></script>' % extra_js)
    return out, suffix


# =========================================================== CAREERS LANDING
careers_body = """
  <main class="legal action-page" id="careersTop">
    <section class="legal-head">
      <div class="legal-wrap">
        <p class="legal-eyebrow">Careers</p>
        <h1 class="legal-title">Careers at NOVA Konut</h1>
        <p class="legal-lead">NOVA KONUT İNŞAAT YATIRIM A.Ş. develops high-end residential buildings along the Kadıköy&ndash;Bağdat Caddesi corridor in Istanbul. Our projects are delivered by small, experienced teams in which architects, engineers and site staff work directly with one another. We look for people who take responsibility for what is built and who make sound decisions in the field.</p>
      </div>
    </section>

    <section class="legal-body">
      <div class="legal-wrap">
        <section class="positions" aria-labelledby="openPositionsTitle">
          <div class="positions-head">
            <h2 class="positions-title" id="openPositionsTitle">Open positions</h2>
            <p class="positions-count">One position</p>
          </div>

          <ul class="vacancy-list">
            <li class="vacancy-row">
              <a class="vacancy-link" href="construction-site-manager-architect.html" data-testid="vacancy-link-csm">
                <span class="vacancy-text">
                  <span class="vacancy-title">Construction Site Manager (Architect)</span>
                  <span class="vacancy-meta">
                    <span class="vacancy-place">Kadıköy / Bağdat Caddesi, Istanbul</span>
                    <span class="vacancy-dot" aria-hidden="true"></span>
                    <span class="vacancy-mode">Full time &middot; On site</span>
                  </span>
                </span>
                <span class="vacancy-action" aria-hidden="true">
                  <span class="vacancy-action-label">View Details</span>
                  <svg class="vacancy-arrow" width="26" height="8" viewBox="0 0 26 8" fill="none" stroke="currentColor" stroke-width="1"><path d="M0 4h24M20.5 1L24 4l-3.5 3"/></svg>
                </span>
              </a>
            </li>
          </ul>
        </section>
      </div>
    </section>
  </main>

"""

careers_head, careers_suffix = head(
    'Careers | NOVA Konut',
    'Open positions at NOVA KONUT İNŞAAT YATIRIM A.Ş., developer of high-end residential buildings on Bağdat Caddesi, Istanbul.',
    'careers.html')

# ============================================================== VACANCY PAGE
vacancy_body = """
  <main class="legal action-page" id="vacancyTop">
    <section class="legal-head">
      <div class="legal-wrap">
        <p class="legal-eyebrow"><a class="legal-back" href="careers.html" data-testid="vacancy-back">Careers</a></p>
        <h1 class="legal-title">Construction Site Manager (Architect)</h1>
        <ul class="vacancy-facts">
          <li>Kadıköy / Bağdat Caddesi, Istanbul</li>
          <li>Full time &middot; On site</li>
          <li>Architecture &mdash; construction site management</li>
        </ul>
        <p class="legal-lead">NOVA is seeking an experienced architect to manage the delivery of high-end residential projects along Istanbul&rsquo;s Kadıköy&ndash;Bağdat Caddesi corridor. The role calls for direct site leadership from structural works through finishing, handover and the occupancy-permit stage. The candidate must coordinate teams, resolve construction details and make sound decisions in the field.</p>
      </div>
    </section>

    <section class="legal-body">
      <div class="legal-wrap">
        <article class="legal-article">
          <section class="legal-section" id="requirements">
            <h2><span class="legal-num">01</span> Requirements</h2>
            <ul class="legal-list">
              <li>University degree in Architecture.</li>
              <li>At least 10 years of active construction-site experience.</li>
              <li>Direct management of structural and finishing works.</li>
              <li>Practical experience in quantity take-offs, cost estimates and progress-payment assessments.</li>
              <li>Strong subcontractor management, scheduling and site coordination.</li>
              <li>Ability to interpret drawings, resolve construction details and implement them correctly on site.</li>
              <li>Ability to prepare and manage work programmes, anticipate delays and take corrective action.</li>
              <li>Experience establishing and leading a site organisation.</li>
              <li>Active application of occupational health and safety requirements.</li>
              <li>Proficiency in AutoCAD and Microsoft Office.</li>
              <li>Strong judgement, accountability, discipline and problem-solving ability.</li>
              <li>Active driver with a valid Class B driving licence.</li>
              <li>Good working English in reading, writing and speaking where relevant to the role.</li>
            </ul>
          </section>

          <section class="legal-section" id="responsibilities">
            <h2><span class="legal-num">02</span> Responsibilities</h2>
            <ul class="legal-list">
              <li>Lead daily construction activities and site organisation.</li>
              <li>Coordinate subcontractors, trades and site teams.</li>
              <li>Prepare and review quantity take-offs and progress-payment assessments.</li>
              <li>Monitor the programme and address delays.</li>
              <li>Enforce quality, occupational health and safety, and construction standards.</li>
              <li>Resolve site issues with the design and project teams.</li>
              <li>Report progress, risks and decisions clearly to project management.</li>
              <li>Manage assigned work from structural construction through finishing, handover and the occupancy-permit stage.</li>
            </ul>
          </section>

          <section class="legal-section" id="apply">
            <h2><span class="legal-num">03</span> Apply for this position</h2>

            <form class="nova-ui-form" id="careersFormEl" novalidate data-testid="careers-form">
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
                <p class="form-hint" id="appCvHint">PDF, DOC or DOCX, up to 10 MB.</p>
                <div class="file-field">
                  <input type="file" id="appCv" name="cv" class="file-input" accept=".pdf,.doc,.docx" aria-describedby="appCvHint" data-testid="careers-cv" />
                  <label class="file-button" for="appCv">Choose CV</label>
                  <span class="file-name" id="appCvName" aria-live="polite">No file selected</span>
                  <button type="button" class="file-remove" id="appCvRemove" hidden data-testid="careers-cv-remove">Remove</button>
                </div>
                <p class="form-error" id="appCvError" hidden></p>
              </div>

              <div class="form-row form-check">
                <label><input type="checkbox" id="appPrivacy" name="privacy" required data-testid="careers-privacy" /> I have read the <a href="applicant-privacy-notice.html" data-testid="careers-privacy-link">Applicant Privacy Notice</a>. <span class="req">*</span></label>
                <p class="form-error" id="appPrivacyError" hidden></p>
              </div>

              <div class="form-actions">
                <button type="submit" class="form-submit" id="careersSubmit" data-testid="careers-submit">Submit application</button>
                <p class="form-result" id="careersResult" role="status" aria-live="polite" hidden data-testid="careers-result"></p>
              </div>
            </form>

            <div class="apply-alt">
              <h3>Apply by email</h3>
              <p>Please attach your CV and briefly describe the residential projects you have managed on site.</p>
              <dl class="legal-meta">
                <dt>Address</dt>
                <dd><a href="mailto:__MAIL__">__MAIL__</a></dd>
                <dt>Subject</dt>
                <dd>Application &mdash; Construction Site Manager (Architect) &mdash; NOVA Konut</dd>
              </dl>
              <p><a class="mail-cta" href="__MAILTO__" data-testid="careers-mail-cta">Apply by Email</a></p>
              <p class="apply-alt-note">How NOVA handles applicant data is set out in the <a href="applicant-privacy-notice.html" data-testid="careers-privacy-link-email">Applicant Privacy Notice</a>.</p>
            </div>
          </section>
        </article>
      </div>
    </section>
  </main>

""".replace('__MAILTO__', MAILTO).replace('__MAIL__', MAIL)

vacancy_head, vacancy_suffix = head(
    'Construction Site Manager (Architect) | Careers | NOVA Konut',
    'NOVA KONUT İNŞAAT YATIRIM A.Ş. is seeking an experienced architect to lead the delivery of high-end residential projects in Kadıköy / Bağdat Caddesi, Istanbul.',
    'construction-site-manager-architect.html', 'careers.js')

# ================================================================= SPEAK UP
speak_body = """
  <main class="legal action-page" id="speakUpTop">
    <section class="legal-head">
      <div class="legal-wrap">
        <p class="legal-eyebrow">Ethics &amp; Compliance</p>
        <h1 class="legal-title">Speak Up</h1>
        <p class="legal-lead">NOVA KONUT İNŞAAT YATIRIM A.Ş. asks anyone who becomes aware of a serious concern on its projects &mdash; employees, workers, contractors, suppliers, residents and neighbours &mdash; to report it. Reports are assessed on their substance. The expectations behind this page are set out in our <a href="ethical-principles.html" data-testid="speakup-ethics-link">Ethical Principles &amp; Labour Standards</a>.</p>
      </div>
    </section>

    <section class="legal-body">
      <div class="legal-wrap">
        <article class="legal-article">
          <section class="legal-section" id="whatToReport">
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
            <p>Please describe what happened as specifically as you can. A concrete account &mdash; what, where, when and who was involved &mdash; can be assessed; a general allegation often cannot. Retaliation against a person who raises a concern in good faith is not accepted.</p>
          </section>

          <section class="legal-section" id="identity">
            <h2><span class="legal-num">02</span> Your identity</h2>
            <p>The form below does not ask for your name or contact details. If you would like NOVA to be able to ask follow-up questions, you may add a contact method in the optional field at the end of the form; anything you enter there may identify you. Please include in the description only the personal information you consider necessary.</p>
          </section>

          <section class="legal-section" id="immediateDanger">
            <h2><span class="legal-num">03</span> Immediate danger</h2>
            <p>This page is not an emergency service and is not monitored continuously. If there is an immediate risk to life, health or safety, or a suspected offence in progress, contact the competent emergency or public authorities first. In Türkiye the general emergency number is 112.</p>
          </section>

          <section class="legal-section" id="reportForm">
            <h2><span class="legal-num">04</span> Submit a report</h2>

            <form class="nova-ui-form" id="reportFormEl" novalidate data-testid="report-form">
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
                <p class="form-hint" id="reportFileHint">PDF, JPG, PNG, DOC or DOCX, up to 10 MB.</p>
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
                <p class="form-hint">An e-mail address, telephone number or any other way of reaching you. Providing it may identify you.</p>
                <input type="text" id="reportContact" name="contact" class="form-control" maxlength="180" data-testid="report-contact" />
              </div>

              <div class="form-actions">
                <button type="submit" class="form-submit" id="reportSubmit" data-testid="report-submit">Submit report</button>
                <p class="form-result" id="reportResult" role="status" aria-live="polite" hidden data-testid="report-result"></p>
              </div>
            </form>

            <div class="apply-alt">
              <h3>Other ways to raise a concern</h3>
              <p>These channels identify you to the Company, because your e-mail address or electronic notification identity is visible to the recipient. Neither is anonymous.</p>
              <dl class="legal-meta">
                <dt>E-mail</dt>
                <dd><a href="mailto:__MAIL__?subject=Speak%20Up%20%E2%80%94%20NOVA%20Konut">__MAIL__</a></dd>
                <dt>Registered electronic notification (KEP)</dt>
                <dd><a href="mailto:__KEP__">__KEP__</a></dd>
              </dl>
              <p class="apply-alt-note">You may also raise a concern directly with the competent public authority.</p>
            </div>
          </section>
        </article>
      </div>
    </section>
  </main>

""".replace('__MAIL__', MAIL).replace('__KEP__', KEP)

speak_head, speak_suffix = head(
    'Speak Up | Confidential Reporting | NOVA Konut',
    'Report occupational health and safety, ethical, labour or supplier concerns relating to NOVA Konut projects. The form does not ask for your name.',
    'anonymous-reporting.html', 'speak-up.js')

for name, content in [
    ('careers.html', careers_head + careers_body + careers_suffix),
    ('construction-site-manager-architect.html', vacancy_head + vacancy_body + vacancy_suffix),
    ('anonymous-reporting.html', speak_head + speak_body + speak_suffix),
]:
    open('/app/frontend/' + name, 'w', encoding='utf-8').write(content)
    print('wrote', name, len(content))
