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

  /* ========== Hero Slider (auto-play with progress bar) ========== */
  const sliderRoot = $('#ewSlider');
  if (sliderRoot) {
    const slides = $$('.ew-slide', sliderRoot);
    const segs = $$('.ew-progress-seg', sliderRoot);
    const arrows = $$('.ew-slider-arrow', sliderRoot);
    const DURATION = 3500;
    let sliderIdx = 0;
    let sliderTimer = null;

    function resetAllFills() {
      segs.forEach((s) => {
        const f = s.querySelector('.ew-progress-fill');
        f.style.transition = 'none';
        f.style.width = '0%';
      });
    }

    function setSlide(idx) {
      slides[sliderIdx].classList.remove('active');
      segs[sliderIdx].classList.remove('active');
      resetAllFills();
      sliderIdx = idx;
      slides[sliderIdx].classList.add('active');
      segs[sliderIdx].classList.add('active');
      const activeFill = segs[sliderIdx].querySelector('.ew-progress-fill');
      // Double rAF ensures the "transition:none + width:0" commits before starting new animation
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          activeFill.style.transition = `width ${DURATION}ms linear`;
          activeFill.style.width = '100%';
        });
      });
    }

    function goTo(idx) {
      idx = (idx + slides.length) % slides.length;
      setSlide(idx);
      restartTimer();
    }

    function restartTimer() {
      if (sliderTimer) clearTimeout(sliderTimer);
      sliderTimer = setTimeout(() => goTo(sliderIdx + 1), DURATION);
    }

    // Init: kick off the first slide's fill animation
    setSlide(0);
    restartTimer();

    // Arrow clicks
    arrows.forEach(btn => {
      btn.addEventListener('click', () => {
        const dir = btn.dataset.dir;
        goTo(dir === 'next' ? sliderIdx + 1 : sliderIdx - 1);
      });
    });
    // Segment clicks
    segs.forEach((seg, i) => {
      seg.addEventListener('click', () => goTo(i));
    });
    // Pause on hover
    sliderRoot.addEventListener('mouseenter', () => {
      if (sliderTimer) clearTimeout(sliderTimer);
      const activeFill = segs[sliderIdx].querySelector('.ew-progress-fill');
      const w = getComputedStyle(activeFill).width;
      activeFill.style.transition = 'none';
      activeFill.style.width = w;
    });
    sliderRoot.addEventListener('mouseleave', () => {
      const activeFill = segs[sliderIdx].querySelector('.ew-progress-fill');
      const currentWidth = parseFloat(getComputedStyle(activeFill).width);
      const totalWidth = parseFloat(getComputedStyle(activeFill.parentElement).width);
      const remainingRatio = Math.max(0, 1 - (currentWidth / totalWidth));
      const remainingMs = Math.max(400, DURATION * remainingRatio);
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          activeFill.style.transition = `width ${remainingMs}ms linear`;
          activeFill.style.width = '100%';
        });
      });
      if (sliderTimer) clearTimeout(sliderTimer);
      sliderTimer = setTimeout(() => goTo(sliderIdx + 1), remainingMs);
    });
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
