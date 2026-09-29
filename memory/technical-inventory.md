# NOVA website — internal technical inventory (not published)

Verified 29 September 2026 against `/app/frontend` and a runtime inspection of the preview
deployment (Chromium). Kept internally because the public Cookie Notice and Privacy Notice
describe categories rather than every dependency. **Public text must stay consistent with
this file — update both together.**

## First-party storage
| Item | Type | Purpose | Expiry |
|---|---|---|---|
| `nova-news-feed:en`, `nova-news-feed:tr` | localStorage | Cached copy of the last valid news JSON (`js/news.js`), 30-minute freshness window | No expiry; overwritten on refresh |

The cookie information banner was removed on 29 September 2026 (markup deleted from
`index.html`, handler deleted from `js/script.js`). The site therefore writes exactly one
localStorage item, the news cache. No consent record of any kind is created.

No HTTP cookies are set by the site: `document.cookie` is empty at runtime and there is no
`document.cookie` write anywhere in `/app/frontend/js`.

## Third-party requests (verified in the network log)
| Host | Provider | Used by | Notes |
|---|---|---|---|
| `fonts.googleapis.com`, `fonts.gstatic.com` | Google | every page (`<link>` in `<head>`) | No cookie observed; transmits IP/UA. Candidate for self-hosting (Cormorant Garamond + Playfair Display are SIL OFL licensed). |
| `cdn.jsdelivr.net` | jsDelivr | `about.html`, `build-beyond-living.html`, `construction.html`, `contact.html`, `design.html`, `leed.html` (GSAP 3.15, three.js) | No cookie observed. Candidate for self-hosting. |
| `unpkg.com` | unpkg | Leaflet CSS/JS where used | No cookie observed. |
| `raw.githubusercontent.com` | GitHub, Inc. | `index.html`, `newsroom.html`, `news-detail.html` (news JSON feed) | No cookie observed. |
| Publisher image hosts (e.g. `images.adsttc.com`, `cdn.sanity.io`) | News publishers | news cards/detail when the feed supplies an image | Loaded per article; local category images used as fallback. |
| `www.openstreetmap.org`, `tile.openstreetmap.org` | OpenStreetMap Foundation | `east-west.html` map iframe | Third-party frame; may set its own storage. |

Preview-environment only, **not** part of the site code and not listed publicly:
`static.cloudflareinsights.com` and the `__cf_bm` cookie come from the Emergent preview host.
If the production host (Turhost/Cloudflare) injects equivalent scripts or cookies, they must be
added to the public Cookie Notice.

## Forms and data flows
- Registration of interest / contact forms (17 pages): full name, country code, phone, e-mail,
  project, "how did you hear", marketing preference, privacy confirmation → `POST /api/enquiries`
  (FastAPI + MongoDB in the preview; **not deployed** with the static site). Notification mailbox:
  `iletisim@nova.istanbul`.
- Instagram strip on `contact.html` calls `/api/instagram/latest` and falls back to static tiles.
- Speak Up report form (`anonymous-reporting.html` + `js/speak-up.js`): `REPORT_ENDPOINT = null`.
  Single adapter `submitReport(report)` builds `multipart/form-data` (category, description,
  incidentDate, location, ongoing, involved, contact, attachment) and POSTs it once an endpoint
  is set. While null it rejects with `code = 'CHANNEL_NOT_AVAILABLE'` and the UI prints only
  "Online reporting is temporarily unavailable. Your report has not been sent." Nothing is
  transmitted, stored, logged or confirmed.
- Careers application form (`construction-site-manager-architect.html` + `js/careers.js`):
  `APPLICATION_ENDPOINT = null`. Single adapter `submitApplication(application)` builds
  `multipart/form-data` (fullName, email, phone, city, position, years, experience, cv) and POSTs
  it once an endpoint is set. While null it rejects with `code = 'APPLICATIONS_NOT_AVAILABLE'` and
  the UI prints only "Online submission is temporarily unavailable. Your application has not been
  sent. Please apply by email."
  Interim real route: `mailto:iletisim@nova.istanbul` with the subject
  "Application — Construction Site Manager (Architect) — NOVA Konut".

## Open legal / infrastructure questions (blocking final legal sign-off)
1. Registered office address and trade-registry details for the legal pages.
2. Hosting provider, server location, and server-log content/retention.
3. E-mail and (future) CRM provider; whether enquiry, report or applicant data leaves Türkiye.
4. Applicable Article 9 condition/safeguard for each confirmed overseas connection
   (Google, jsDelivr, unpkg, GitHub, OpenStreetMap, publisher image hosts) — none is asserted
   in the public notices today.
5. Actual retention periods for enquiries, reports and applications.
6. Who inside NOVA receives Speak Up reports, whether retaliation protection is documented, and
   whether a reference-number/acknowledgement process will exist.
7. Recruitment data flow: who assesses applications, for how long CVs are kept, whether an
   applicant-consent record is required for talent-pool retention.
8. Whether the production host injects analytics/security scripts or cookies of its own. If it
   does, a Cookie Notice update — and, for anything optional, a real preference interface — is
   required before go-live.
9. Applicant data flow for the e-mail route: which mailbox provider serves
   `iletisim@nova.istanbul`, where its servers and backups are located, who has access, and how
   long CVs remain in the mailbox. The Applicant Privacy Notice currently states recipient
   *categories* only and asserts no Article 9 condition.
10. Whether NOVA wants a talent-pool retention period (and therefore a separate explicit consent)
    beyond the recruitment process for the advertised position.
11. Formal appointment requirements for a legally designated şantiye şefi are deliberately NOT
    mentioned in the public advertisement; they must be checked internally during recruitment.
