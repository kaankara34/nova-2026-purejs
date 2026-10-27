# EDSAA / mobile journal / native scrollbar delivery

Date: 2026-10-27. Static bilingual NOVA site; no deployment or Search Console operation performed.

## Delivered

- Canonical-format pages: `https://nova.istanbul/tr/edsaa.html` and
  `https://nova.istanbul/en/edsaa.html`. Existing `.html` standard retained.
- Both pages contain only the approved EDSAA H1, short description, original East West render
  and small project link, inside existing site chrome. No new form/sales section, invented logo
  or additional company facts. EDSAA header enquiry links lead to the existing contact page.
- Exact visible TR: **EDSAA, Nova Konut İnşaat Yatırım A.Ş.’nin inşaat alanında faaliyet gösteren iştirakidir.**
- Exact visible EN: **EDSAA is an affiliate of Nova Konut İnşaat Yatırım A.Ş., operating in the construction sector.**
- One normal EDSAA anchor in the existing NOVA subgroup on all68pages, same markup/styles as
  neighboring entries. Desktop/mobile hierarchy retained. EDSAA language controls cross-link
  directly to the other EDSAA page, never home.
- Homepage journal renders3cards at<=767px,6at>=768px. A breakpoint change reuses the already
  loaded feed without another fetch. Full newsroom page is unchanged.
- Native document scrollbar is thin with#6b5e43 thumb and light track. WebKit fallback and
  forced-colors handling included. No scroll interception/widget; OS overlay-scrollbar behavior
  still belongs to the browser/device. Menu scroll locking remains unchanged.

## Design and asset provenance

- Corporate reference: existing contact page's shared light header/footer and typography.
  New `css/edsaa.css` is isolated to `.page-edsaa`; no restyling of other pages.
- Existing optimized `media/images/ew/render/ew-render1.webp`,1901x1070, unchanged original bytes.
  SHA256:`32f3fef251968cf9d4ea447be17e86f018db406d53f520492b9b24563a262779`.
- Both towers remain visible with the original aspect ratio; no crop, recolor, dark overlay,
  architecture modification, parallax or new render. Width/height and aspect-ratio reserve space.
  Important first-screen image is eager/high-priority, not lazy.
- No EDSAA logo asset was found; the existing site typography is used for its H1.
- Page-specific footer contrast adapts the newer residence labels to the existing light palette.
  Tested label contrast12.86:1 and small-label contrast7.19:1. Mobile title clears both the header
  and its utility strip; no overlap. Shared footer structure/content remains unchanged.

## SEO, source content and indexability

- Exact user-approved titles and meta descriptions, one H1, selectable initial HTML text,
  self-canonicals and reciprocal tr/en alternates. x-default points to TR consistently with
  existing default-Turkish site routing.
- Localized OG and Twitter summary-large-image metadata use absolute production-domain render
  URLs. The image is identified as an architectural render, not an EDSAA logo.
- Valid JSON-LD graph: AboutPage whose mainEntity is EDSAA Organization. Both languages share
  `https://nova.istanbul/tr/edsaa.html#organization`; preferred organization URL is the TR page.
  Description is exactly the relevant approved intro. Parent is referenced only by the known
  Nova legal name and homepage. No existing Nova Organization @id was found in local markup or
  the fetched public homepage, so no contradictory new named-id graph was fabricated.
- About pages had no existing affiliate-description area; no SEO-only section was added there.
  No footer area or link group was added.
- Both canonical URLs are included through the existing `build_i18n.sitemap()` mechanism.
  Existing pages/robots sitemap declaration retained; no invented lastmod or ranking boosts.
- `robots.txt` unchanged. Preview still returns `X-Robots-Tag: noindex, nofollow`.
- Production `.htaccess` has a scoped extensionless-to-`.html`301 rule so its generic extensionless
  rewrite cannot expose a duplicate EDSAA response. Preview uses only advertised `.html` URLs;
  unadvertised extensionless preview requests may404. No production HTTP/indexing claim made.

## Changed files

- New pages: `frontend/tr/edsaa.html`, `frontend/en/edsaa.html`.
- New isolated CSS: `frontend/css/edsaa.css`.
- Existing shared changes: `frontend/js/news.js` (home count), `frontend/css/styles.css`
  (root scrollbar only), the original66HTML files (one NOVA submenu item only).
- Authoring: `scripts/edsaa_data.py`, `scripts/build_edsaa.py`, `scripts/build_i18n.py`
  (page mapping/special-page hook and existing sitemap mechanism).
- SEO/routing: `frontend/sitemap.xml`, `frontend/.htaccess`.
- Focused tests: `tests/test_edsaa_pages.py`; existing count/scope checks updated for68pages.
- `frontend/serve.json` and `robots.txt` are semantically unchanged; original render unchanged.

## Verification

- Final suite **271passed**, no skips/failures (`test_reports/pytest/iter70_final.xml`).
- Eleven focused EDSAA tests cover all68menu entries, exact metadata, JSON-LD, no forms,
  canonical HTTP200 in preview, sitemap and unchanged original66pages beyond menu insertion.
- Browser checks: mobile/tablet/desktop responsive layout;3/6home news and resize behavior;
  desktop/mobile NOVA entry; language click and CDP touch release-to-commit; native scrollbar.
- Final320px touch run: whole render visible, no form/overflow;14px swipe stays on TR until
  release, then opens EN EDSAA; mobile submenu link visible and functional. Device emulation,
  not a claim of physical-phone testing.
- Follow-up at320/390/768/1024/1440: loaded original render, comfortable header clearance,
  readable footer colors and no overflow. Source copies/SEO keep working without client rendering.
- Targeted generation rerun changed0files. **Do not run the full stale i18n rebuild** merely to
  change EDSAA; run `python scripts/build_edsaa.py` for this scoped update.

## After publication — site owner actions, NOT completed here

1. Check real production EDSAA URLs return200 with the correct pages, self-canonical metadata
   and no blocking production robots/X-Robots headers; preview restrictions must remain separate.
2. In the verified `nova.istanbul` Search Console property, review or submit the existing sitemap.
3. Inspect both exact EDSAA URLs with URL Inspection; request indexing if appropriate.

No verification tag, verified access, submission, indexing, ranking, rich result or knowledge
panel outcome is claimed. Google may choose another snippet; discoverability is supported but
neither indexing nor ranking is guaranteed. Possible later improvement: monitor EDSAA-branded
queries in Search Console after publication, without extending the approved visible copy.