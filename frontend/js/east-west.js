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
    const PLANS = [
      {
        title: 'SUITE',
        img: 'https://placehold.co/700x560/f5f1ea/8a7f5e?font=lora&text=SUITE',
        total: '42.3 sq m / 455 sq ft',
        rooms: [
          { i: 1, name: 'Living Area', size: '6370 &times; 4079 mm' },
          { i: 2, name: 'Bedroom', size: '3908 &times; 2100 mm' }
        ]
      },
      {
        title: 'ONE BEDROOM',
        img: 'https://placehold.co/700x560/f5f1ea/8a7f5e?font=lora&text=ONE+BEDROOM',
        total: '68.5 sq m / 737 sq ft',
        rooms: [
          { i: 1, name: 'Living / Dining', size: '5480 &times; 4200 mm' },
          { i: 2, name: 'Bedroom', size: '4100 &times; 3500 mm' },
          { i: 3, name: 'Kitchen', size: '3200 &times; 2400 mm' }
        ]
      },
      {
        title: 'TWO BEDROOM',
        img: 'https://placehold.co/700x560/f5f1ea/8a7f5e?font=lora&text=TWO+BEDROOM',
        total: '112.8 sq m / 1214 sq ft',
        rooms: [
          { i: 1, name: 'Living / Dining', size: '6820 &times; 4900 mm' },
          { i: 2, name: 'Master Bedroom', size: '4600 &times; 3800 mm' },
          { i: 3, name: 'Bedroom 2', size: '3900 &times; 3200 mm' },
          { i: 4, name: 'Kitchen', size: '3500 &times; 2600 mm' }
        ]
      },
      {
        title: 'THREE BEDROOM',
        img: 'https://placehold.co/700x560/f5f1ea/8a7f5e?font=lora&text=THREE+BEDROOM',
        total: '156.4 sq m / 1684 sq ft',
        rooms: [
          { i: 1, name: 'Living / Dining', size: '7400 &times; 5200 mm' },
          { i: 2, name: 'Master Bedroom', size: '5100 &times; 3900 mm' },
          { i: 3, name: 'Bedroom 2', size: '4200 &times; 3400 mm' },
          { i: 4, name: 'Bedroom 3', size: '3800 &times; 3200 mm' },
          { i: 5, name: 'Kitchen', size: '3800 &times; 2800 mm' }
        ]
      }
    ];
    const tabs = $$('.ew-plans-tab', plansRoot);
    const titleEl = $('#ewPlansTitle');
    const imgEl = $('#ewPlansImg');
    const rowsEl = $('#ewPlansRows');
    const arrows = $$('.ew-plans-arrow', plansRoot);
    const expandBtn = $('#ewPlansExpand');
    const lightbox = $('#ewPlansLightbox');
    const lightboxImg = $('#ewPlansLightboxImg');
    const lightboxClose = $('#ewPlansLightboxClose');
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
      if (!lightbox) return;
      lightboxImg.src = PLANS[planIdx].img;
      lightboxImg.alt = PLANS[planIdx].title;
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
