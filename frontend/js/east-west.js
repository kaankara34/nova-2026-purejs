/* East West — Project Page Interactions */
(function () {
  'use strict';

  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));

  /* ========== Lightbox Gallery ========== */
  const lightbox = $('#ewLightbox');
  const lightboxImg = $('#ewLightboxImg');
  const lightboxCount = $('#ewLightboxCount');
  const closeBtn = $('#ewLightboxClose');
  const prevBtn = $('#ewLightboxPrev');
  const nextBtn = $('#ewLightboxNext');
  const slideEls = $$('.ew-slide');
  const viewAllBtn = $('#ewViewAll');
  const galleryTriggerBtn = $('#ewGalleryTrigger');

  const images = slideEls.map(it => it.src);
  let currentIdx = 0;

  function openLightbox(idx) {
    if (!lightbox || !images.length) return;
    currentIdx = idx;
    updateLightbox();
    lightbox.classList.add('open');
    lightbox.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }
  function closeLightbox() {
    if (!lightbox) return;
    lightbox.classList.remove('open');
    lightbox.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }
  function updateLightbox() {
    if (!lightboxImg) return;
    lightboxImg.src = images[currentIdx];
    if (lightboxCount) lightboxCount.textContent = `${currentIdx + 1} / ${images.length}`;
  }
  function prev() { currentIdx = (currentIdx - 1 + images.length) % images.length; updateLightbox(); }
  function next() { currentIdx = (currentIdx + 1) % images.length; updateLightbox(); }

  slideEls.forEach((item, i) => {
    item.addEventListener('click', e => { e.preventDefault(); openLightbox(i); });
  });
  if (viewAllBtn) viewAllBtn.addEventListener('click', e => { e.preventDefault(); openLightbox(0); });
  if (galleryTriggerBtn) galleryTriggerBtn.addEventListener('click', () => openLightbox(0));
  const galleryBtn = $('#ewGalleryBtn');
  if (galleryBtn) galleryBtn.addEventListener('click', () => openLightbox(0));
  if (closeBtn) closeBtn.addEventListener('click', closeLightbox);
  if (prevBtn) prevBtn.addEventListener('click', prev);
  if (nextBtn) nextBtn.addEventListener('click', next);
  if (lightbox) lightbox.addEventListener('click', e => {
    if (e.target === lightbox) closeLightbox();
  });
  document.addEventListener('keydown', e => {
    if (!lightbox || !lightbox.classList.contains('open')) return;
    if (e.key === 'Escape') closeLightbox();
    if (e.key === 'ArrowLeft') prev();
    if (e.key === 'ArrowRight') next();
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
        try { viewport.setPointerCapture(e.pointerId); } catch (_) {}
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

  /* ========== Typical Apartments (tabs + plans + lightbox) ========== */
  const plansRoot = $('.ew-plans');
  if (plansRoot) {
    const EAST_PLANS = [
      {
        title: '3+1',
        img: 'https://customer-assets-agu9un31.emergentagent.net/job_darg-clone-1/artifacts/fe9f3f7t_3%2B1.png',
        total: '~127 m² / 1367 sq ft',
        rooms: [
          { i: 1, name: 'Living Room', size: '39.33 m²' },
          { i: 2, name: 'Master Bedroom', size: '20.22 m²' },
          { i: 3, name: 'Bedroom', size: '12.05 m²' },
          { i: 4, name: 'Bedroom', size: '11.84 m²' },
          { i: 5, name: 'Kitchen', size: '13.29 m²' },
          { i: 6, name: 'Balcony', size: '7.11 m²' }
        ]
      },
      {
        title: '4+1',
        img: 'https://customer-assets-agu9un31.emergentagent.net/job_darg-clone-1/artifacts/6l1vxd82_4%2B1.png',
        total: '~150 m² / 1614 sq ft',
        rooms: [
          { i: 1, name: 'Living Room', size: '39.33 m²' },
          { i: 2, name: 'Master Bedroom', size: '20.22 m²' },
          { i: 3, name: 'Bedroom', size: '12.05 m²' },
          { i: 4, name: 'Bedroom', size: '11.84 m²' },
          { i: 5, name: 'Bedroom', size: '9.86 m²' },
          { i: 6, name: 'Kitchen', size: '13.29 m²' },
          { i: 7, name: 'Balcony', size: '7.11 m²' }
        ]
      },
      {
        title: 'DUBLEKS ALT',
        img: 'https://customer-assets-agu9un31.emergentagent.net/job_darg-clone-1/artifacts/4tvpokq3_DubleksAlt.png',
        total: '~135 m² / 1453 sq ft',
        rooms: [
          { i: 1, name: 'Living Room', size: '59.05 m²' },
          { i: 2, name: 'Master Bedroom', size: '16.75 m²' },
          { i: 3, name: 'Kitchen', size: '18.83 m²' },
          { i: 4, name: 'Utility Room', size: '4.89 m²' },
          { i: 5, name: 'Entrance', size: '6.66 m²' },
          { i: 6, name: 'Master Bathroom', size: '4.60 m²' },
          { i: 7, name: 'Balcony', size: '7.00 m²' }
        ]
      },
      {
        title: 'DUBLEKS ÜST',
        img: 'https://customer-assets-agu9un31.emergentagent.net/job_darg-clone-1/artifacts/jaq8uvnq_DubleksU%CC%88st.png',
        total: '~85 m² / 915 sq ft',
        rooms: [
          { i: 1, name: 'Master Bedroom', size: '29.81 m²' },
          { i: 2, name: 'Bedroom', size: '17.90 m²' },
          { i: 3, name: 'Bedroom', size: '10.00 m²' },
          { i: 4, name: 'Master Bathroom', size: '7.92 m²' },
          { i: 5, name: 'Bathroom', size: '3.06 m²' },
          { i: 6, name: 'Terrace', size: '4.37 m²' }
        ]
      }
    ];
    // WEST plans reuse same layouts by default — replace image URLs / dims when supplied
    const WEST_PLANS = EAST_PLANS.map(p => ({ ...p, rooms: p.rooms.slice() }));

    const PLANS_BY_TOWER = { EAST: EAST_PLANS, WEST: WEST_PLANS };
    const towerTabs = $$('.ew-plans-tab--tower', plansRoot);
    const tabs = $$('.ew-plans-tab:not(.ew-plans-tab--tower)', plansRoot);
    const titleEl = $('#ewPlansTitle');
    const imgEl = $('#ewPlansImg');
    const rowsEl = $('#ewPlansRows');
    const arrows = $$('.ew-plans-arrow', plansRoot);
    const expandBtn = $('#ewPlansExpand');
    const lightbox = $('#ewPlansLightbox');
    const lightboxImg = $('#ewPlansLightboxImg');
    const lightboxClose = $('#ewPlansLightboxClose');
    let currentTower = 'EAST';
    let planIdx = 0;

    function currentPlans() { return PLANS_BY_TOWER[currentTower]; }

    function renderPlan(idx) {
      const list = currentPlans();
      planIdx = idx;
      const p = list[idx];
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

    function setTower(tower) {
      currentTower = tower;
      towerTabs.forEach(t => t.classList.toggle('active', t.dataset.tower === tower));
      renderPlan(planIdx);
    }

    towerTabs.forEach(t => t.addEventListener('click', () => setTower(t.dataset.tower)));
    tabs.forEach((t, i) => t.addEventListener('click', () => renderPlan(i)));
    arrows.forEach(btn => {
      btn.addEventListener('click', () => {
        const dir = btn.dataset.dir === 'next' ? 1 : -1;
        const len = currentPlans().length;
        renderPlan((planIdx + dir + len) % len);
      });
    });

    function openPlanLightbox() {
      if (!lightbox) return;
      lightboxImg.src = currentPlans()[planIdx].img;
      lightboxImg.alt = currentPlans()[planIdx].title;
      lightbox.classList.add('open');
      lightbox.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
    }
    function closePlanLightbox() {
      if (!lightbox) return;
      lightbox.classList.remove('open');
      lightbox.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
    }
    if (expandBtn) expandBtn.addEventListener('click', openPlanLightbox);
    if (imgEl) imgEl.addEventListener('click', openPlanLightbox);
    if (lightboxClose) lightboxClose.addEventListener('click', closePlanLightbox);
    if (lightbox) lightbox.addEventListener('click', e => { if (e.target === lightbox) closePlanLightbox(); });
    document.addEventListener('keydown', e => {
      if (!lightbox || !lightbox.classList.contains('open')) return;
      if (e.key === 'Escape') closePlanLightbox();
    });

    /* ---- Swipe / drag support on floor plan image (touch + mouse) ---- */
    const planViewport = $('.ew-plans-image', plansRoot);
    if (planViewport && window.PointerEvent) {
      const T = 40;
      let sx = 0, sy = 0, down = false, pid = null, dragged = false;
      planViewport.style.touchAction = 'pan-y';

      planViewport.addEventListener('pointerdown', (e) => {
        if (e.pointerType === 'mouse' && e.button !== 0) return;
        // Skip if pointer starts on the expand button — let its own click work
        if (e.target.closest('.ew-plans-expand')) return;
        down = true; dragged = false; pid = e.pointerId;
        sx = e.clientX; sy = e.clientY;
        try { planViewport.setPointerCapture(e.pointerId); } catch (_) {}
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
          const len = currentPlans().length;
          renderPlan((planIdx + (dx < 0 ? 1 : -1) + len) % len);
        }
      });
      planViewport.addEventListener('pointercancel', () => { down = false; pid = null; dragged = false; });
      // Swallow follow-up click only if user actually dragged and the target isn't the expand button
      planViewport.addEventListener('click', (e) => {
        if (dragged && !e.target.closest('.ew-plans-expand')) {
          e.preventDefault(); e.stopPropagation();
        }
        dragged = false;
      }, true);
      if (imgEl) imgEl.addEventListener('dragstart', e => e.preventDefault());
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
