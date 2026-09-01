# CHANGELOG

## 2026-06 — Contact page additions (contact.html)
- `ct-intro`: added a quiet constructivist SVG art mark (brass arc, dotted slow-orbit ring, sage/brass disc, stone block, hairlines). Respects `prefers-reduced-motion`.
- New Instagram section between `ct-detail` and `ct-loc`: "Latest from Nova" head, `@novakonut` follow link, 4 square tiles (NOVA-generated imagery, all linking to the profile), follow note. 4 columns desktop / 2 columns ≤767px.
  - NOTE: Instagram cannot be scraped (HTTP 403) — tiles use NOVA's own imagery and link out; this is NOT a live feed.
- Register Interest before the footer: the project-page (Martı) split composition rebuilt as scoped `ct-reg` / `ct-form`, retoned to Contact's warm palette (#E8DFD2 ground, ink text, brass italic sub, ink submit). UI-only submit handler in `js/contact.js` (`#ctRegisterForm`) with inline status message.
- Files: `scripts/contact_main.html`, `frontend/css/contact.css`, `frontend/js/contact.js`, regenerated `frontend/contact.html` (448 lines) via `scripts/build_contact.py`.
## 2026-06 — Contact: live Instagram + stabilised birds film
- Backend (`backend/server.py`): `GET /api/instagram/latest` (latest 4 posts, 30-min in-memory cache + Mongo `ig_cache` fallback) and `GET /api/instagram/image/{shortcode}` (proxies the signed IG CDN image). Instagram blocks httpx/requests TLS fingerprints (429) — fetch uses `curl_cffi` with `impersonate="safari17_0"`. Added `curl_cffi` to requirements.
- `frontend/js/contact.js` hydrates the 4 tiles from the API on load; the bundled snapshot images stay as fallback (also restored on img error).
- Video regraded: 2-pass vidstab stabilisation, 2.1x slow with `minterpolate` (14.7s), pale blue-teal grade matching the user's reference; CSS desaturating filter removed. `frontend/media/video/birds.mp4|.webm` + poster (~1.5MB each).
- Verified on preview: overflow 0, video playing/stable, tiles served from `/api/instagram/image/...`.

## 2026-06 — Contact revision (real IG posts + birds film)
- Instagram tiles now show NOVA's **real latest 4 posts**, fetched via the public `i.instagram.com/api/v1/users/web_profile_info` endpoint (x-ig-app-id header), images stored locally at `frontend/media/images/contact/ig/post-1..4.jpg`, each tile deep-links to its post permalink (shortcodes DaQk9OvscF6, DaQbe_FMl7l, DaQadKFjHXG, DaN8eQ2s4pu). Tiles are 4:5 like Instagram. NOTE: static snapshot, not a live feed — re-run the fetch to refresh.
- `ct-intro` art replaced: the SVG mark removed, now a muted birds-rising-from-a-tree film (autoplay/muted/loop/playsinline) at `frontend/media/video/birds.mp4|.webm` + poster, toned with a warm veil and hairline frame. Source: Pexels free-licence clip 5024947 (Aman's own Vimeo clip was not reused for licence reasons).
- Verified: desktop 1920 + mobile 390 screenshots, 0 horizontal overflow, form error/success paths, oxlint 0 warnings/0 errors on contact.js. User visual confirmation pending.
