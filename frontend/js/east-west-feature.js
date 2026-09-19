/* ==========================================================
   THE RESIDENCES EAST WEST — homepage media carousel.
   Local East West renders only. One timing source drives both the
   crossfade and the perimeter progress line, so they never drift.
   ========================================================== */
(function () {
  'use strict';

  const section = document.getElementById('eastWestFeature');
  const media = document.getElementById('ewFeatureMedia');
  if (!section || !media) return;

  const panel = section.querySelector('.ew-feature-inner') || section;
  const slides = Array.prototype.slice.call(media.querySelectorAll('[data-ew-slide]'));
  if (slides.length < 2) return;

  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const DURATION = 5000;
  const SVG_NS = 'http://www.w3.org/2000/svg';

  let index = 0;
  let elapsed = 0;
  let lastFrame = 0;
  let frame = null;
  let inView = false;
  let hovering = false;

  /* ---------------------------------------------- perimeter progress line */
  const svg = document.createElementNS(SVG_NS, 'svg');
  svg.setAttribute('class', 'ew-progress');
  svg.setAttribute('aria-hidden', 'true');
  svg.setAttribute('preserveAspectRatio', 'none');
  const base = document.createElementNS(SVG_NS, 'rect');
  const active = document.createElementNS(SVG_NS, 'rect');
  base.setAttribute('class', 'ew-progress-base');
  active.setAttribute('class', 'ew-progress-active');
  svg.appendChild(base);
  svg.appendChild(active);
  panel.appendChild(svg);

  let perimeter = 0;

  function measure() {
    const rect = panel.getBoundingClientRect();
    const w = Math.max(1, Math.round(rect.width));
    const h = Math.max(1, Math.round(rect.height));
    const inset = 1;
    const rw = Math.max(1, w - inset * 2);
    const rh = Math.max(1, h - inset * 2);
    svg.setAttribute('viewBox', '0 0 ' + w + ' ' + h);
    [base, active].forEach(function (node) {
      node.setAttribute('x', String(inset));
      node.setAttribute('y', String(inset));
      node.setAttribute('width', String(rw));
      node.setAttribute('height', String(rh));
    });
    perimeter = (rw + rh) * 2;
    active.style.strokeDasharray = perimeter + ' ' + perimeter;
    paint();
  }

  function paint() {
    const ratio = Math.min(1, elapsed / DURATION);
    active.style.strokeDashoffset = String(perimeter * (1 - ratio));
  }

  /* ---------------------------------------------- slides */
  function preloadNext() {
    const next = slides[(index + 1) % slides.length];
    if (next && next.dataset.srcDeferred) {
      delete next.dataset.srcDeferred;
      const preload = new Image();
      preload.src = next.currentSrc || next.src;
    }
  }

  function advance() {
    slides[index].classList.remove('is-active');
    index = (index + 1) % slides.length;
    slides[index].classList.add('is-active');
    preloadNext();
  }

  function tick(now) {
    if (!lastFrame) lastFrame = now;
    elapsed += now - lastFrame;
    lastFrame = now;
    if (elapsed >= DURATION) {
      elapsed = 0;
      advance();
    }
    paint();
    frame = window.requestAnimationFrame(tick);
  }

  function stop() {
    if (frame) window.cancelAnimationFrame(frame);
    frame = null;
    lastFrame = 0;
  }

  function start() {
    if (frame) return;
    if (reduced.matches || document.hidden || !inView || hovering) return;
    preloadNext();
    lastFrame = 0;
    frame = window.requestAnimationFrame(tick);
  }

  function applyReducedMotion() {
    if (reduced.matches) {
      stop();
      elapsed = 0;
      svg.style.display = 'none';
      paint();
    } else {
      svg.style.display = '';
      start();
    }
  }

  media.addEventListener('mouseenter', function () { hovering = true; stop(); });
  media.addEventListener('mouseleave', function () { hovering = false; start(); });
  document.addEventListener('visibilitychange', function () {
    if (document.hidden) stop(); else start();
  });
  window.addEventListener('resize', measure);
  if ('ResizeObserver' in window) new ResizeObserver(measure).observe(panel);

  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        inView = entry.isIntersecting;
        if (inView) start(); else stop();
      });
    }, { rootMargin: '120px 0px' });
    io.observe(section);
  } else {
    inView = true;
  }

  if (reduced.addEventListener) reduced.addEventListener('change', applyReducedMotion);

  measure();
  applyReducedMotion();
})();
