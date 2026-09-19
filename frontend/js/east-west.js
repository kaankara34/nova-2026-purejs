/* East West — Project Page Interactions */
(function () {
  'use strict';

  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));

  /* ========== Hero video — force play as soon as data is ready ========== */
  (function initHeroVideo() {
    const v = document.querySelector('.ew-hero-video');
    if (!v) return;
    v.muted = true;
    const tryPlay = () => {
      const p = v.play();
      if (p && typeof p.catch === 'function') p.catch(() => { /* blocked until user gesture */ });
    };
    if (v.readyState >= 2) tryPlay();
    else v.addEventListener('loadeddata', tryPlay, { once: true });
    v.addEventListener('canplay', tryPlay, { once: true });
    const onFirstInteract = () => {
      tryPlay();
      window.removeEventListener('pointerdown', onFirstInteract);
      window.removeEventListener('touchstart', onFirstInteract);
    };
    window.addEventListener('pointerdown', onFirstInteract, { passive: true });
    window.addEventListener('touchstart', onFirstInteract, { passive: true });
  })();

  /* ========== Lightbox Gallery (finger-tracking swipe) ========== */
  const lightbox = $('#ewLightbox');
  const lightboxViewport = $('#ewLightboxViewport');
  const lightboxTrack = $('#ewLightboxTrack');
  const lightboxCount = $('#ewLightboxCount');
  const closeBtn = $('#ewLightboxClose');
  const prevBtn = $('#ewLightboxPrev');
  const nextBtn = $('#ewLightboxNext');
  const slideEls = $$('.ew-slide');
  const viewAllBtn = $('#ewViewAll');
  const galleryTriggerBtn = $('#ewGalleryTrigger');

  const images = slideEls.map(it => ({ src: it.src, alt: it.alt || '' }));
  let lbSwiper = null;

  function buildLightboxTrack() {
    if (!lightboxTrack || lightboxTrack.dataset.built === '1') return;
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
    if (!lbSwiper && window.NovaSwiper && lightboxViewport) {
      lbSwiper = new window.NovaSwiper(lightboxViewport, {
        loop: true,
        clones: true,
        onChange: updateLbCounter,
        onSettle: updateLbCounter
      });
    } else if (lbSwiper) {
      lbSwiper.refresh();
    }
    if (lbSwiper) lbSwiper.goTo(idx, false);
    updateLbCounter();
  }
  function closeLightbox() {
    if (!lightbox) return;
    lightbox.classList.remove('open');
    lightbox.setAttribute('aria-hidden', 'true');
    window.unlockScroll();
  }

  slideEls.forEach((item, i) => {
    item.addEventListener('click', e => { e.preventDefault(); openLightbox(i); });
  });
  if (viewAllBtn) viewAllBtn.addEventListener('click', e => { e.preventDefault(); openLightbox(0); });
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
    if (e.key === 'ArrowLeft') lbSwiper && lbSwiper.prev();
    if (e.key === 'ArrowRight') lbSwiper && lbSwiper.next();
  });

  /* ========== Hero Slider (auto-play, arrows only) ========== */
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

    function next() { setSlide((sliderIdx + 1) % slides.length); }
    function prev() { setSlide((sliderIdx - 1 + slides.length) % slides.length); }

    function scheduleAuto() {
      if (autoTimer) clearTimeout(autoTimer);
      autoTimer = setTimeout(function tick() {
        next();
        autoTimer = setTimeout(tick, DURATION);
      }, DURATION);
    }
    function restartTimer() { scheduleAuto(); }

    scheduleAuto();

    arrows.forEach(btn => {
      btn.addEventListener('click', () => {
        if (btn.dataset.dir === 'next') next();
        else prev();
        restartTimer();
      });
    });

    segs.forEach((seg, i) => {
      seg.addEventListener('click', () => {
        setSlide(i);
        restartTimer();
      });
    });

    /* ---- Swipe / drag support (touch + mouse via Pointer Events) ---- */
    const viewport = $('.ew-slider-viewport', sliderRoot);
    if (viewport && window.PointerEvent) {
      const THRESHOLD = 50;
      let startX = 0, startY = 0, isDown = false, pointerId = null, didDrag = false;
      viewport.style.touchAction = 'pan-y';
      viewport.style.cursor = 'grab';

      viewport.addEventListener('pointerdown', (e) => {
        if (e.pointerType === 'mouse' && e.button !== 0) return;
        isDown = true;
        didDrag = false;
        pointerId = e.pointerId;
        startX = e.clientX;
        startY = e.clientY;
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
        isDown = false;
        pointerId = null;
        viewport.style.cursor = 'grab';
        if (Math.abs(dx) > THRESHOLD && Math.abs(dx) > Math.abs(dy)) {
          if (dx < 0) next();
          else prev();
          restartTimer();
        }
      });

      viewport.addEventListener('pointercancel', () => {
        isDown = false; pointerId = null; didDrag = false;
        viewport.style.cursor = 'grab';
      });

      // If a drag happened, swallow the follow-up click so lightbox/other handlers don't fire
      viewport.addEventListener('click', (e) => {
        if (didDrag) {
          e.preventDefault();
          e.stopPropagation();
          didDrag = false;
        }
      }, true);

      // Prevent default HTML5 image drag ghost
      $$('.ew-slide', viewport).forEach(img => img.addEventListener('dragstart', e => e.preventDefault()));
    }
  }


  /* ========== Typical Apartments (tabs + plans + lightbox) ========== */
  const plansRoot = $('.ew-plans');
  if (plansRoot) {
    const PLANS_BY_TOWER = window.EW_PLANS;
    const towerTabs = $$('.ew-plans-tab--tower', plansRoot);
    const tabs = $$('.ew-plans-tab:not(.ew-plans-tab--tower)', plansRoot);
    const titleEl = $('#ewPlansTitle');
    const trackEl = $('#ewPlansTrack');
    const planViewport = $('#ewPlansViewport');
    const rowsEl = $('#ewPlansRows');
    const arrows = $$('.ew-plans-arrow', plansRoot);
    const expandBtn = $('#ewPlansExpand');
    const lightbox = $('#ewPlansLightbox');
    const lightboxImg = $('#ewPlansLightboxImg');
    const lightboxClose = $('#ewPlansLightboxClose');
    let currentTower = 'EAST';
    let planIdx = 0;
    let planSwiper = null;

    function currentPlans() { return PLANS_BY_TOWER[currentTower]; }

    function buildPlanSlides() {
      if (!trackEl) return;
      const list = currentPlans();
      trackEl.innerHTML = list.map((p) =>
        `<div class="ew-plans-slide"><div class="ew-plans-figure"${p.dim ? ` data-dim="${p.dim}"` : ''}><img src="${p.img}" alt="${p.title} floor plan" draggable="false"/></div></div>`
      ).join('');
    }

    function renderPlanInfo(idx) {
      const list = currentPlans();
      planIdx = idx;
      const p = list[idx];
      tabs.forEach((t, i) => t.classList.toggle('active', i === idx));
      titleEl.textContent = p.title;
      const rows = [`<div class="ew-plans-row ew-plans-row--total"><span>Total Internal Area</span><span class="ew-plans-val">${p.total}</span></div>`];
      p.rooms.forEach((r, i) => {
        rows.push(`<div class="ew-plans-row"><span><em>${i + 1}.</em> ${r.name}</span><span class="ew-plans-val">${r.size}</span></div>`);
      });
      rowsEl.innerHTML = rows.join('');
    }

    function initPlanSwiper() {
      buildPlanSlides();
      if (planSwiper) planSwiper.destroy();
      if (window.NovaSwiper && planViewport) {
        planSwiper = new window.NovaSwiper(planViewport, {
          loop: true,
          clones: true,
          threshold: 0.18,
          duration: 380,
          onChange: (i) => renderPlanInfo(i),
          onSettle: (i) => renderPlanInfo(i)
        });
      }
      renderPlanInfo(0);
    }

    function setTower(tower) {
      currentTower = tower;
      towerTabs.forEach(t => t.classList.toggle('active', t.dataset.tower === tower));
      // Rebuild slides for new tower, keep index
      const savedIdx = planIdx;
      initPlanSwiper();
      if (planSwiper) planSwiper.goTo(Math.min(savedIdx, currentPlans().length - 1), false);
      renderPlanInfo(planSwiper ? planSwiper.getIndex() : 0);
    }

    towerTabs.forEach(t => t.addEventListener('click', () => setTower(t.dataset.tower)));
    tabs.forEach((t, i) => t.addEventListener('click', () => {
      if (planSwiper) planSwiper.goTo(i);
      else renderPlanInfo(i);
    }));
    arrows.forEach(btn => {
      btn.addEventListener('click', () => {
        if (!planSwiper) return;
        if (btn.dataset.dir === 'next') planSwiper.next();
        else planSwiper.prev();
      });
    });

    // Initial setup
    initPlanSwiper();

    function openPlanLightbox() {
      if (!lightbox) return;
      const p = currentPlans()[planIdx];
      lightboxImg.src = p.img;
      lightboxImg.alt = p.title;
      if (p.dim) lightbox.setAttribute('data-dim', p.dim);
      else lightbox.removeAttribute('data-dim');
      lightbox.classList.add('open');
      lightbox.setAttribute('aria-hidden', 'false');
      window.lockScroll();
    }
    function closePlanLightbox() {
      if (!lightbox) return;
      lightbox.classList.remove('open');
      lightbox.setAttribute('aria-hidden', 'true');
      window.unlockScroll();
    }
    if (expandBtn) expandBtn.addEventListener('click', openPlanLightbox);
    const downloadBtn = $('#ewPlansDownload');
    function downloadPlanA4() {
      const p = currentPlans()[planIdx];
      const w = window.open('', '_blank');
      if (!w) return;
      const buildingLabel = 'THE RESIDENCES EAST WEST — ' + currentTower + ' BUILDING';
      const planTitle = p.title + ' PLAN';
      const netVal = p.total || '';
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
        '<div class="metric"><div class="metric-label">Total Internal Area</div><div class="metric-value">' + netVal + '</div></div>' +
        '</div></div>' +
        '<script>window.onload = function(){ var img = document.querySelector("img"); function go(){ setTimeout(function(){ window.focus(); window.print(); }, 250); } if (img.complete) go(); else img.onload = go;'
        + '};<\/script></body></html>'
      );
      w.document.close();
    }
    if (downloadBtn) downloadBtn.addEventListener('click', downloadPlanA4);
    if (lightboxClose) lightboxClose.addEventListener('click', closePlanLightbox);
    if (lightbox) lightbox.addEventListener('click', e => { if (e.target === lightbox) closePlanLightbox(); });
    document.addEventListener('keydown', e => {
      if (!lightbox || !lightbox.classList.contains('open')) return;
      if (e.key === 'Escape') closePlanLightbox();
    });

    /* Tap-to-open lightbox — NovaSwiper only fires drag on movement, so a
       plain click on the plan image (without drag) opens the fullscreen view. */
    if (planViewport) {
      planViewport.addEventListener('click', (e) => {
        if (e.target.closest('.ew-plans-expand, .ew-plans-download')) return;
        // NovaSwiper preserves normal clicks when no drag occurred
        openPlanLightbox();
      });
    }
  }

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
