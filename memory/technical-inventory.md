# NOVA website — internal technical inventory (not published)

Verified 28 September 2026 against `/app/frontend` and a runtime inspection of the preview
deployment (Chromium). Kept internally because the public Cookie Notice and Privacy Notice
describe categories rather than every dependency. **Public text must stay consistent with
this file — update both together.**

## First-party storage
| Item | Type | Purpose | Expiry |
|---|---|---|---|
| `dg_cookie_ok` | localStorage | Marks the cookie information notice as dismissed (`js/script.js`) | No expiry; cleared by the user |
| `nova-news-feed:en`, `nova-news-feed:tr` | localStorage | Cached copy of the last valid news JSON (`js/news.js`), 30-minute freshness window | No expiry; overwritten on refresh |

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
- Speak Up report form (`anonymous-reporting.html` + `js/speak-up.js`): `REPORT_ENDPOINT = null`;
  nothing is transmitted or stored. Single adapter: `submitReport()`.
- Careers application form (`careers.html` + `js/careers.js`): `APPLICATION_ENDPOINT = null`;
  nothing is transmitted or stored. Single adapter: `submitApplication()`.

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
8. Whether the production host injects analytics/security scripts or cookies of its own.
