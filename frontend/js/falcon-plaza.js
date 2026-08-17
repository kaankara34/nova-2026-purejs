/* Martı Residence — Project Page Interactions
   Reuses the same class-based hooks as East-West so we share all
   gallery/slider/plans/form/lightbox behaviour. Plans data + FAQ are
   Marti-specific.
*/
(function () {
  'use strict';

  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));

  /* ========== Hero video — force play the moment data is ready ==========
     Removes the visible poster→video swap: as soon as the first frame is
     decoded we start playback. Handles iOS Safari where autoplay can be
     deferred until the video is fully parsed. */
  (function initHeroVideo() {
    const v = document.querySelector('.ew-hero-video');
    if (!v) return;
    v.muted = true;                       // required for iOS autoplay
    const tryPlay = () => {
      const p = v.play();
      if (p && typeof p.catch === 'function') p.catch(() => { /* browsers block until user gesture */ });
    };
    if (v.readyState >= 2) tryPlay();
    else v.addEventListener('loadeddata', tryPlay, { once: true });
    v.addEventListener('canplay', tryPlay, { once: true });
    // Retry once on first pointerdown / touchstart as a fallback for
    // aggressive iOS power-saving modes.
    const onFirstInteract = () => {
      tryPlay();
      window.removeEventListener('pointerdown', onFirstInteract);
      window.removeEventListener('touchstart', onFirstInteract);
    };
    window.addEventListener('pointerdown', onFirstInteract, { passive: true });
    window.addEventListener('touchstart', onFirstInteract, { passive: true });
  })();

  /* ========== Lightbox Gallery (finger-tracking swipe) ==========
     Sources: manifesto grid images (3) + key-features block images (3).
     Both #ewGalleryBtn, #ewGalleryTrigger and .fplaza-view-all-btn open this
     same combined set, and clicking any of those tiles opens at its index.
     Uses NovaSwiper for Instagram-style drag-to-swipe. */
  const lightbox = $('#ewLightbox');
  const lightboxViewport = $('#ewLightboxViewport');
  const lightboxTrack = $('#ewLightboxTrack');
  const lightboxCount = $('#ewLightboxCount');
  const closeBtn = $('#ewLightboxClose');
  const prevBtn = $('#ewLightboxPrev');
  const nextBtn = $('#ewLightboxNext');
  const galleryTriggerBtn = $('#ewGalleryTrigger');

  const manifestoImgs = $$('.fplaza-manifesto-img img');
  const featureImgs   = $$('.fplaza-features-img img');
  const galleryTiles  = [...manifestoImgs, ...featureImgs];
  const images        = galleryTiles.map(el => ({ src: el.src, alt: el.alt || '' }));

  let lbSwiper = null;

  function buildLightboxTrack() {
    if (!lightboxTrack) return;
    if (lightboxTrack.dataset.built === '1') return;
    lightboxTrack.innerHTML = images.map(im =>
      `<div class="ew-lightbox-slide"><img src="${im.src}" alt="${im.alt}" draggable="false"/></div>`
    ).join('');
    lightboxTrack.dataset.built = '1';
  }

  function updateLbCounter() {
    if (!lightboxCount || !lbSwiper) return;
    lightboxCount.textContent = `${lbSwiper.getIndex() + 1} / ${images.length}`;
  }

  function openLightbox(idx) {
    if (!lightbox || !images.length) return;
    /* Capture scrollY IMMEDIATELY — before any DOM changes that could shift
       the viewport (focus, sticky-header re-layout, etc). */
    window.lockScroll();
    buildLightboxTrack();
    lightbox.classList.add('open');
    lightbox.setAttribute('aria-hidden', 'false');

    // Initialize swiper on first open (viewport has real dimensions now)
    if (!lbSwiper && window.NovaSwiper && lightboxViewport) {
      lbSwiper = new window.NovaSwiper(lightboxViewport, {
        loop: true,
        clones: true,
        onChange: updateLbCounter,
        onSettle: updateLbCounter
      });
    } else if (lbSwiper) {
      // Ensure measured width is fresh (viewport size may have changed)
      lbSwiper.refresh();
    }
    if (lbSwiper) {
      lbSwiper.goTo(idx, false);
    }
    updateLbCounter();
  }
  function closeLightbox() {
    if (!lightbox) return;
    lightbox.classList.remove('open');
    lightbox.setAttribute('aria-hidden', 'true');
    window.unlockScroll();
  }

  // Tap on any manifesto / feature image opens the lightbox at that index
  galleryTiles.forEach((item, i) => {
    item.style.cursor = 'pointer';
    item.addEventListener('click', e => { e.preventDefault(); openLightbox(i); });
  });

  // Any "View All Images" or GALLERY entry point opens at first slide
  $$('.fplaza-view-all-btn').forEach(btn => {
    btn.addEventListener('click', e => { e.preventDefault(); openLightbox(0); });
  });
  if (galleryTriggerBtn) galleryTriggerBtn.addEventListener('click', () => openLightbox(0));
  const galleryBtn = $('#ewGalleryBtn');
  if (galleryBtn) galleryBtn.addEventListener('click', () => openLightbox(0));
  if (closeBtn) closeBtn.addEventListener('click', closeLightbox);
  if (prevBtn) prevBtn.addEventListener('click', () => lbSwiper && lbSwiper.prev());
  if (nextBtn) nextBtn.addEventListener('click', () => lbSwiper && lbSwiper.next());
  if (lightbox) lightbox.addEventListener('click', e => {
    if (e.target === lightbox) closeLightbox();
  });
  document.addEventListener('keydown', e => {
    if (!lightbox || !lightbox.classList.contains('open')) return;
    if (e.key === 'Escape') closeLightbox();
    if (e.key === 'ArrowLeft')  lbSwiper && lbSwiper.prev();
    if (e.key === 'ArrowRight') lbSwiper && lbSwiper.next();
  });

  /* ========== Hero Slider (auto-play, arrows) ========== */
  const sliderRoot = $('#ewSlider');
  if (sliderRoot) {
    const slides = $$('.ew-slide', sliderRoot);
    const arrows = $$('.ew-slider-arrow', sliderRoot);
    const segs = $$('.ew-progress-seg', sliderRoot);
    const DURATION = 3500;
    let sliderIdx = 0;
    let autoTimer = null;

    function setSlide(idx) {
      slides.forEach(s => s.classList.remove('active'));
      segs.forEach(s => s.classList.remove('active'));
      sliderIdx = idx;
      slides[sliderIdx].classList.add('active');
      if (segs[sliderIdx]) segs[sliderIdx].classList.add('active');
    }
    function nextS() { setSlide((sliderIdx + 1) % slides.length); }
    function prevS() { setSlide((sliderIdx - 1 + slides.length) % slides.length); }
    function scheduleAuto() {
      if (autoTimer) clearTimeout(autoTimer);
      autoTimer = setTimeout(function tick() {
        nextS();
        autoTimer = setTimeout(tick, DURATION);
      }, DURATION);
    }
    function restartTimer() { scheduleAuto(); }
    scheduleAuto();

    arrows.forEach(btn => {
      btn.addEventListener('click', () => {
        if (btn.dataset.dir === 'next') nextS();
        else prevS();
        restartTimer();
      });
    });
    segs.forEach((seg, i) => {
      seg.addEventListener('click', () => {
        setSlide(i);
        restartTimer();
      });
    });

    /* Swipe / drag */
    const viewport = $('.ew-slider-viewport', sliderRoot);
    if (viewport && window.PointerEvent) {
      const THRESHOLD = 50;
      let startX = 0, startY = 0, isDown = false, pointerId = null, didDrag = false;
      viewport.style.touchAction = 'pan-y';
      viewport.style.cursor = 'grab';

      viewport.addEventListener('pointerdown', (e) => {
        if (e.pointerType === 'mouse' && e.button !== 0) return;
        isDown = true; didDrag = false; pointerId = e.pointerId;
        startX = e.clientX; startY = e.clientY;
        viewport.style.cursor = 'grabbing';
        try { viewport.setPointerCapture(e.pointerId); } catch (_) { /* noop */ }
      });
      viewport.addEventListener('pointermove', (e) => {
        if (!isDown || e.pointerId !== pointerId) return;
        if (Math.abs(e.clientX - startX) > 8) didDrag = true;
      });
      viewport.addEventListener('pointerup', (e) => {
        if (!isDown || e.pointerId !== pointerId) return;
        const dx = e.clientX - startX;
        const dy = e.clientY - startY;
        isDown = false; pointerId = null;
        viewport.style.cursor = 'grab';
        if (Math.abs(dx) > THRESHOLD && Math.abs(dx) > Math.abs(dy)) {
          if (dx < 0) nextS(); else prevS();
          restartTimer();
        }
      });
      viewport.addEventListener('pointercancel', () => {
        isDown = false; pointerId = null; didDrag = false;
        viewport.style.cursor = 'grab';
      });
      viewport.addEventListener('click', (e) => {
        if (didDrag) { e.preventDefault(); e.stopPropagation(); didDrag = false; }
      }, true);
      $$('.ew-slide', viewport).forEach(img => img.addEventListener('dragstart', e => e.preventDefault()));
    }
  }

  /* ========== Form submit (UI-only) ========== */
  const form = $('#ewEnquireForm');
  if (form) {
    form.addEventListener('submit', e => {
      e.preventDefault();
      const fullname = form.querySelector('[name="fullname"]').value.trim();
      const email = form.querySelector('[name="email"]').value.trim();
      const privacy = form.querySelector('[name="privacy"]').checked;
      if (!fullname || !email || !privacy) {
        alert('Please fill required fields and accept the privacy policy.');
        return;
      }
      alert('Thank you. Your enquiry has been received.');
      form.reset();
    });
  }

  /* ========== Typical Apartments (Marti plans) ========== */
  const plansRoot = $('.ew-plans');
  if (plansRoot) {
    const PLANS = [
      {
        title: '2+1',
        img: 'https://customer-assets-agu9un31.emergentagent.net/job_darg-clone-1/artifacts/fe9f3f7t_3%2B1.png',
        total: '~115 m² / 1238 sq ft',
        net: '115 m²', gross: '138 m²',
        rooms: [
          { i: 1, name: 'Living Room', size: '36.20 m²' },
          { i: 2, name: 'Master Bedroom', size: '19.40 m²' },
          { i: 3, name: 'Bedroom', size: '12.10 m²' },
          { i: 4, name: 'Kitchen', size: '12.80 m²' },
          { i: 5, name: 'Balcony', size: '6.90 m²' }
        ]
      },
      {
        title: '3+1',
        img: 'https://customer-assets-agu9un31.emergentagent.net/job_darg-clone-1/artifacts/fe9f3f7t_3%2B1.png',
        total: '~145 m² / 1560 sq ft',
        net: '145 m²', gross: '176 m²',
        rooms: [
          { i: 1, name: 'Living Room', size: '42.10 m²' },
          { i: 2, name: 'Master Bedroom', size: '22.60 m²' },
          { i: 3, name: 'Bedroom', size: '13.40 m²' },
          { i: 4, name: 'Bedroom', size: '12.05 m²' },
          { i: 5, name: 'Kitchen', size: '14.20 m²' },
          { i: 6, name: 'Balcony', size: '8.10 m²' }
        ]
      },
      {
        title: '4+1',
        img: 'https://customer-assets-agu9un31.emergentagent.net/job_darg-clone-1/artifacts/6l1vxd82_4%2B1.png',
        total: '~185 m² / 1991 sq ft',
        net: '185 m²', gross: '221 m²',
        rooms: [
          { i: 1, name: 'Living Room', size: '48.40 m²' },
          { i: 2, name: 'Master Bedroom', size: '24.10 m²' },
          { i: 3, name: 'Bedroom', size: '14.20 m²' },
          { i: 4, name: 'Bedroom', size: '13.40 m²' },
          { i: 5, name: 'Bedroom', size: '11.60 m²' },
          { i: 6, name: 'Kitchen', size: '15.10 m²' },
          { i: 7, name: 'Balcony', size: '9.20 m²' }
        ]
      },
      {
        title: 'PENTHOUSE',
        img: 'https://customer-assets-agu9un31.emergentagent.net/job_darg-clone-1/artifacts/4tvpokq3_DubleksAlt.png',
        total: '~340 m² / 3660 sq ft',
        net: '340 m²', gross: '395 m²',
        rooms: [
          { i: 1, name: 'Living / Dining', size: '82.40 m²' },
          { i: 2, name: 'Master Suite', size: '38.20 m²' },
          { i: 3, name: 'Bedroom Suite', size: '22.10 m²' },
          { i: 4, name: 'Bedroom Suite', size: '20.80 m²' },
          { i: 5, name: 'Study', size: '14.20 m²' },
          { i: 6, name: 'Kitchen', size: '18.90 m²' },
          { i: 7, name: 'Terrace', size: '46.30 m²' }
        ]
      }
    ];

    const tabs = $$('.ew-plans-tab', plansRoot);
    const titleEl = $('#ewPlansTitle');
    const imgEl = $('#ewPlansImg');
    const rowsEl = $('#ewPlansRows');
    const arrows = $$('.ew-plans-arrow', plansRoot);
    const expandBtn = $('#ewPlansExpand');
    const planLightbox = $('#ewPlansLightbox');
    const planLightboxImg = $('#ewPlansLightboxImg');
    const planLightboxClose = $('#ewPlansLightboxClose');
    let planIdx = 0;

    function renderPlan(idx) {
      planIdx = idx;
      const p = PLANS[idx];
      tabs.forEach((t, i) => t.classList.toggle('active', i === idx));
      titleEl.textContent = p.title;
      imgEl.src = p.img;
      imgEl.alt = p.title + ' floor plan';
      const rows = [`<div class="ew-plans-row ew-plans-row--total"><span>Total Internal Area</span><span class="ew-plans-val">${p.total}</span></div>`];
      p.rooms.forEach(r => {
        rows.push(`<div class="ew-plans-row"><span><em>${r.i}.</em> ${r.name}</span><span class="ew-plans-val">${r.size}</span></div>`);
      });
      rowsEl.innerHTML = rows.join('');
    }

    tabs.forEach((t, i) => t.addEventListener('click', () => renderPlan(i)));
    arrows.forEach(btn => {
      btn.addEventListener('click', () => {
        const dir = btn.dataset.dir === 'next' ? 1 : -1;
        renderPlan((planIdx + dir + PLANS.length) % PLANS.length);
      });
    });

    function openPlanLightbox() {
      if (!planLightbox) return;
      window.lockScroll();
      planLightboxImg.src = PLANS[planIdx].img;
      planLightboxImg.alt = PLANS[planIdx].title;
      planLightbox.classList.add('open');
      planLightbox.setAttribute('aria-hidden', 'false');
    }
    function closePlanLightbox() {
      if (!planLightbox) return;
      planLightbox.classList.remove('open');
      planLightbox.setAttribute('aria-hidden', 'true');
      window.unlockScroll();
    }
    if (expandBtn) expandBtn.addEventListener('click', openPlanLightbox);

    const downloadBtn = $('#ewPlansDownload');
    function downloadPlanA4() {
      const p = PLANS[planIdx];
      const w = window.open('', '_blank');
      if (!w) return;
      const buildingLabel = 'MARTI RESIDENCE — SUADIYE';
      const planTitle = p.title + ' PLAN';
      const netVal = p.net || '';
      const grossVal = p.gross || '';
      w.document.write(
        '<!doctype html><html lang="en"><head><title>' + planTitle + '</title>' +
        '<meta charset="utf-8"/>' +
        '<style>' +
        '@page { size: A4 portrait; margin: 12mm; }' +
        '* { box-sizing: border-box; }' +
        'html, body { margin: 0; padding: 0; background: #fff; font-family: Georgia, "Cormorant Garamond", serif; color: #1a1a1a; }' +
        '.wrap { display: flex; flex-direction: column; align-items: center; padding: 8mm 6mm; }' +
        '.company { font-family: Arial, Helvetica, sans-serif; font-size: 10px; letter-spacing: 0.22em; text-transform: uppercase; color: #6a6555; text-align: center; margin: 0 0 6px; }' +
        '.building { font-family: Arial, Helvetica, sans-serif; font-size: 11px; letter-spacing: 0.28em; text-transform: uppercase; color: #1a1a1a; text-align: center; margin: 0 0 18px; }' +
        'h1 { font-size: 32px; font-weight: 500; letter-spacing: 0.06em; text-transform: uppercase; text-align: center; margin: 0 0 14px; font-variant-numeric: lining-nums; }' +
        '.rule { width: 64px; height: 1px; background: #b3a37e; margin: 0 auto 24px; }' +
        '.plan-img-wrap { width: 100%; text-align: center; margin: 0 0 18px; }' +
        'img { max-width: 100%; max-height: 195mm; width: auto; height: auto; display: block; margin: 0 auto; }' +
        '.metrics { display: flex; justify-content: center; gap: 40px; margin-top: 14px; font-family: Arial, Helvetica, sans-serif; }' +
        '.metric { text-align: center; }' +
        '.metric-label { font-size: 9px; letter-spacing: 0.24em; text-transform: uppercase; color: #8a8471; margin-bottom: 4px; }' +
        '.metric-value { font-size: 16px; font-weight: 500; color: #1a1a1a; font-variant-numeric: lining-nums; }' +
        '.divider-v { width: 1px; height: 34px; background: #d4cec0; align-self: center; }' +
        '</style></head><body>' +
        '<div class="wrap">' +
        '<div class="company">Nova Konut İnşaat Yatırım A.Ş.</div>' +
        '<div class="building">' + buildingLabel + '</div>' +
        '<h1>' + planTitle + '</h1>' +
        '<div class="rule"></div>' +
        '<div class="plan-img-wrap"><img src="' + p.img + '" alt="' + p.title + ' floor plan" crossorigin="anonymous"/></div>' +
        '<div class="metrics">' +
        '<div class="metric"><div class="metric-label">Net Area</div><div class="metric-value">' + netVal + '</div></div>' +
        '<div class="divider-v"></div>' +
        '<div class="metric"><div class="metric-label">Gross Area</div><div class="metric-value">' + grossVal + '</div></div>' +
        '</div></div>' +
        '<script>window.onload = function(){ var img = document.querySelector("img"); function go(){ setTimeout(function(){ window.focus(); window.print(); }, 250); } if (img.complete) go(); else img.onload = go;'
        + '};<\/script></body></html>'
      );
      w.document.close();
    }
    if (downloadBtn) downloadBtn.addEventListener('click', downloadPlanA4);
    if (planLightboxClose) planLightboxClose.addEventListener('click', closePlanLightbox);
    if (planLightbox) planLightbox.addEventListener('click', e => { if (e.target === planLightbox) closePlanLightbox(); });
    document.addEventListener('keydown', e => {
      if (!planLightbox || !planLightbox.classList.contains('open')) return;
      if (e.key === 'Escape') closePlanLightbox();
    });

    /* Swipe on plan image */
    const planViewport = $('.ew-plans-image', plansRoot);
    if (planViewport && window.PointerEvent) {
      const T = 40;
      let sx = 0, sy = 0, down = false, pid = null, dragged = false;
      planViewport.style.touchAction = 'pan-y';
      planViewport.addEventListener('pointerdown', (e) => {
        if (e.pointerType === 'mouse' && e.button !== 0) return;
        if (e.target.closest('.ew-plans-expand, .ew-plans-download')) return;
        down = true; dragged = false; pid = e.pointerId;
        sx = e.clientX; sy = e.clientY;
        try { planViewport.setPointerCapture(e.pointerId); } catch (_) { /* noop */ }
      });
      planViewport.addEventListener('pointermove', (e) => {
        if (!down || e.pointerId !== pid) return;
        if (Math.abs(e.clientX - sx) > 8) dragged = true;
      });
      planViewport.addEventListener('pointerup', (e) => {
        if (!down || e.pointerId !== pid) return;
        const dx = e.clientX - sx;
        const dy = e.clientY - sy;
        down = false; pid = null;
        if (Math.abs(dx) > T && Math.abs(dx) > Math.abs(dy)) {
          renderPlan((planIdx + (dx < 0 ? 1 : -1) + PLANS.length) % PLANS.length);
        }
      });
      planViewport.addEventListener('pointercancel', () => { down = false; pid = null; dragged = false; });
      planViewport.addEventListener('click', (e) => {
        if (e.target.closest('.ew-plans-expand, .ew-plans-download')) return;
        if (dragged) { e.preventDefault(); e.stopPropagation(); dragged = false; return; }
        openPlanLightbox();
      });
      if (imgEl) imgEl.addEventListener('dragstart', e => e.preventDefault());
    }

    // Initial render
    renderPlan(0);
  }

  /* ========== FAQ accordion ========== */
  const faqList = $('#fplazaFaqList');
  if (faqList) {
    $$('.fplaza-faq-q', faqList).forEach(btn => {
      btn.addEventListener('click', () => {
        const item = btn.parentElement;
        const answer = item.querySelector('.fplaza-faq-a');
        const expanded = btn.getAttribute('aria-expanded') === 'true';
        // Close others
        $$('.fplaza-faq-q', faqList).forEach(b => {
          if (b !== btn) {
            b.setAttribute('aria-expanded', 'false');
            const a = b.parentElement.querySelector('.fplaza-faq-a');
            if (a) a.style.maxHeight = null;
          }
        });
        if (expanded) {
          btn.setAttribute('aria-expanded', 'false');
          answer.style.maxHeight = null;
        } else {
          btn.setAttribute('aria-expanded', 'true');
          answer.style.maxHeight = answer.scrollHeight + 'px';
        }
      });
    });
  }

  /* Reveal-on-scroll animations are already handled by script.js
     (watches .reveal-up / .reveal-fade / .reveal-stagger and toggles .in-view) */

  /* ========== Smooth scroll for [data-scroll] buttons ========== */
  $$('[data-scroll]').forEach(btn => {
    btn.addEventListener('click', e => {
      const target = btn.dataset.scroll;
      const el = document.getElementById(target);
      if (el) {
        e.preventDefault();
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
})();
