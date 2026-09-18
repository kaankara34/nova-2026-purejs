/* ==========================================================
   THE RESIDENCES EAST WEST — homepage media crossfade.
   Local East West renders only; stable frame, no layout shift.
   ========================================================== */
(function () {
  'use strict';

  const media = document.getElementById('ewFeatureMedia');
  if (!media) return;

  const slides = Array.prototype.slice.call(media.querySelectorAll('[data-ew-slide]'));
  if (slides.length < 2) return;

  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const INTERVAL = 6000;
  let index = 0;
  let timer = null;
  let inView = false;
  let hovering = false;

  function preloadNext() {
    const next = slides[(index + 1) % slides.length];
    if (next && next.dataset.srcDeferred) {
      delete next.dataset.srcDeferred;
      next.loading = 'eager';
      const img = new Image();
      img.src = next.currentSrc || next.src;
    }
  }

  function advance() {
    slides[index].classList.remove('is-active');
    index = (index + 1) % slides.length;
    slides[index].classList.add('is-active');
    preloadNext();
  }

  function stop() { if (timer) { clearInterval(timer); timer = null; } }

  function start() {
    stop();
    if (reduced.matches || document.hidden || !inView || hovering) return;
    preloadNext();
    timer = setInterval(advance, INTERVAL);
  }

  media.addEventListener('mouseenter', function () { hovering = true; stop(); });
  media.addEventListener('mouseleave', function () { hovering = false; start(); });
  document.addEventListener('visibilitychange', function () {
    if (document.hidden) stop(); else start();
  });

  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        inView = entry.isIntersecting;
        if (inView) start(); else stop();
      });
    }, { rootMargin: '200px 0px' });
    io.observe(media);
  } else {
    inView = true;
    start();
  }

  if (reduced.addEventListener) {
    reduced.addEventListener('change', function () { reduced.matches ? stop() : start(); });
  }
})();
