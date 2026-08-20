/* About page — register form + GSAP scroll animations */
(function () {
  'use strict';

  /* ---- Register form (UI-only mock, matches projects.html pattern) ---- */
  const form = document.getElementById('abForm');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const fullname = form.querySelector('[name="fullname"]').value.trim();
      const email = form.querySelector('[name="email"]').value.trim();
      const privacy = form.querySelector('[name="privacy"]').checked;
      if (!fullname || !email || !privacy) {
        alert('Please complete required fields and accept the privacy policy.');
        return;
      }
      alert('Thank you. Your registration has been received.');
      form.reset();
    });
  }

  /* ---- Split a text node into word spans for staggered reveal (keeps real spaces for copy/screen-readers) ---- */
  function splitWords(el) {
    const text = el.textContent;
    el.textContent = '';
    const words = text.split(' ');
    words.forEach((word, i) => {
      const span = document.createElement('span');
      span.className = 'gs-word';
      span.textContent = word;
      el.appendChild(span);
      if (i < words.length - 1) el.appendChild(document.createTextNode(' '));
    });
  }
  document.querySelectorAll('.gs-words').forEach(splitWords);

  /* ---- Fallback: reveal static content + final stat values if GSAP/ScrollTrigger unavailable ---- */
  const themeMeta0 = document.querySelector('meta[name="theme-color"]');
  const firstThemed = document.querySelector('[data-theme]');
  if (firstThemed) {
    document.body.style.backgroundColor = firstThemed.dataset.theme;
    if (themeMeta0) themeMeta0.setAttribute('content', firstThemed.dataset.theme);
  }
  function revealStatic() {
    document.querySelectorAll('.gs-fade-up, .gs-fade-left, .gs-line, .gs-blur-up, .gs-word').forEach(el => { el.style.opacity = 1; });
    document.querySelectorAll('.gs-clip-reveal').forEach(el => { el.style.clipPath = 'none'; });
    document.querySelectorAll('.ab-stat-num[data-count]').forEach(el => {
      el.textContent = el.dataset.count + (el.dataset.suffix || '');
    });
  }

  /* ---- GSAP scroll animations ---- */
  if (!window.gsap || !window.ScrollTrigger) { revealStatic(); return; }
  gsap.registerPlugin(ScrollTrigger);

  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce) { revealStatic(); return; }

  const EASE = 'power3.out';

  /* Hero — load-in zoom-out + scroll parallax drift */
  const heroImg = document.querySelector('.ab-hero-media img');
  if (heroImg) {
    gsap.fromTo(heroImg, { scale: 1.12 }, { scale: 1, duration: 1.8, ease: 'power2.out' });
    gsap.to(heroImg, {
      yPercent: 14,
      ease: 'none',
      scrollTrigger: { trigger: '.ab-hero', start: 'top top', end: 'bottom top', scrub: true }
    });
  }

  /* Heading line-by-line reveal */
  document.querySelectorAll('.gs-lines').forEach(wrap => {
    const lines = wrap.querySelectorAll('.gs-line');
    if (!lines.length) return;
    gsap.set(lines, { y: 34 });
    gsap.to(lines, {
      opacity: 1, y: 0, duration: 0.9, ease: EASE, stagger: 0.12,
      scrollTrigger: { trigger: wrap, start: 'top 82%' }
    });
  });

  /* Generic fade-up */
  document.querySelectorAll('.gs-fade-up').forEach(el => {
    gsap.set(el, { y: 28 });
    gsap.to(el, {
      opacity: 1, y: 0, duration: 0.9, ease: EASE,
      scrollTrigger: { trigger: el, start: 'top 85%' }
    });
  });

  /* Word-by-word cascade reveal (manifesto lead paragraph) — quick + smooth */
  document.querySelectorAll('.gs-words').forEach(wrap => {
    const words = wrap.querySelectorAll('.gs-word');
    if (!words.length) return;
    gsap.set(words, { y: 10 });
    gsap.to(words, {
      opacity: 1, y: 0, duration: 0.38, ease: 'power2.out', stagger: 0.006,
      scrollTrigger: { trigger: wrap, start: 'top 92%' }
    });
  });

  /* Fade in from the left (LEED text column) */
  document.querySelectorAll('.gs-fade-left').forEach(el => {
    gsap.set(el, { x: -50 });
    gsap.to(el, {
      opacity: 1, x: 0, duration: 1, ease: EASE,
      scrollTrigger: { trigger: el, start: 'top 80%' }
    });
  });

  /* Blur-to-focus reveal (leadership quote) */
  document.querySelectorAll('.gs-blur-up').forEach(el => {
    gsap.set(el, { filter: 'blur(10px)', y: 16 });
    gsap.to(el, {
      opacity: 1, y: 0, filter: 'blur(0px)', duration: 1.1, ease: EASE,
      scrollTrigger: { trigger: el, start: 'top 82%' }
    });
  });

  /* Clip-path wipe reveal — scrubbed to scroll position (LEED image).
     invalidateOnRefresh + image-load refresh keeps it reliable when lazy images resize the layout. */
  document.querySelectorAll('.gs-clip-reveal').forEach(el => {
    gsap.set(el, { clipPath: 'inset(0 0 100% 0)' });
    gsap.to(el, {
      clipPath: 'inset(0 0 0% 0)', ease: 'none',
      scrollTrigger: {
        trigger: el,
        start: 'top bottom',
        end: 'bottom 35%',
        scrub: 1.2,
        invalidateOnRefresh: true
      }
    });
  });

  /* Keep trigger positions correct once lazy media/fonts settle */
  const refresh = () => ScrollTrigger.refresh();
  window.addEventListener('load', refresh);
  document.querySelectorAll('img').forEach(img => {
    if (!img.complete) img.addEventListener('load', refresh, { once: true });
  });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(refresh);

  /* Section images — slow zoom-out parallax as they cross the viewport */
  document.querySelectorAll('.gs-parallax-img').forEach(wrap => {
    const img = wrap.querySelector('img');
    if (!img) return;
    gsap.fromTo(img, { scale: 1.18 }, {
      scale: 1,
      ease: 'none',
      scrollTrigger: { trigger: wrap, start: 'top bottom', end: 'bottom top', scrub: true }
    });
  });

  /* Stat number count-up */
  document.querySelectorAll('.ab-stat-num[data-count]').forEach(el => {
    const target = parseInt(el.dataset.count, 10);
    const suffix = el.dataset.suffix || '';
    ScrollTrigger.create({
      trigger: el,
      start: 'top 85%',
      once: true,
      onEnter: () => {
        gsap.to({ val: 0 }, {
          val: target,
          duration: 1.4,
          ease: 'power1.out',
          onUpdate: function () { el.textContent = Math.round(this.targets()[0].val) + suffix; }
        });
      }
    });
  });

  /* Stat divider grows in once stats are in view */
  const divider = document.querySelector('.ab-stat-divider');
  if (divider) {
    gsap.set(divider, { scaleY: 0 });
    ScrollTrigger.create({
      trigger: '.ab-stats-inner',
      start: 'top 82%',
      once: true,
      onEnter: () => gsap.to(divider, { scaleY: 1, duration: 0.9, ease: EASE })
    });
  }

  /* ---- Manifesto compass motif — slow continuous spin + scroll-linked breathing ---- */
  const orbit = document.querySelector('.ab-manifesto-orbit');
  if (orbit) {
    gsap.to(orbit, { rotation: 360, duration: 100, ease: 'none', repeat: -1, transformOrigin: '50% 50%' });
    gsap.fromTo(orbit, { scale: 0.85, opacity: 0.05 }, {
      scale: 1.05, opacity: 0.14, ease: 'none',
      scrollTrigger: { trigger: '.ab-manifesto', start: 'top bottom', end: 'bottom top', scrub: true }
    });
  }

  /* ---- Section colour theming: body background + mobile theme-color bleed through on scroll ---- */
  const themeMeta = themeMeta0;
  const themedSections = document.querySelectorAll('[data-theme]');
  themedSections.forEach(el => {
    ScrollTrigger.create({
      trigger: el,
      start: 'top center',
      end: 'bottom center',
      onToggle: self => {
        if (!self.isActive) return;
        const color = el.dataset.theme;
        document.body.style.backgroundColor = color;
        if (themeMeta) themeMeta.setAttribute('content', color);
      }
    });
  });

  /* ---- Living background: subtle in-section colour shift as flat-colour sections scroll by ---- */
  const colorBreaths = [
    { sel: '.ab-discover', from: '#ffffff', to: '#fbf6ec' },
    { sel: '.ab-manifesto', from: '#f8f5ef', to: '#f1e8d3' },
    { sel: '.ab-quote', from: '#cdc0a6', to: '#ddc99e' },
    { sel: '.ab-split--gray', from: '#f2efe9', to: '#eae2d2' },
    { sel: '.ab-story', from: '#0d0c0a', to: '#171310' },
    { sel: '.ab-leed', from: '#0b0b0b', to: '#171310' },
    { sel: '.ab-collab', from: '#0d0c0a', to: '#191410' }
  ];
  colorBreaths.forEach(({ sel, from, to }) => {
    const el = document.querySelector(sel);
    if (!el) return;
    gsap.fromTo(el, { backgroundColor: from }, {
      backgroundColor: to, ease: 'none',
      scrollTrigger: { trigger: el, start: 'top bottom', end: 'bottom top', scrub: true }
    });
  });
})();
