/* East West feature: compositor-friendly perimeter, one5s clock for line and slides. */
(function () {
  'use strict';
  const section = document.getElementById('eastWestFeature');
  const media = document.getElementById('ewFeatureMedia');
  if (!section || !media) return;
  const panel = section.querySelector('.ew-feature-inner') || section;
  const slides = [...media.querySelectorAll('[data-ew-slide]')];
  if (slides.length < 2) return;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const canHover = matchMedia('(hover: hover) and (pointer: fine)');
  const DURATION = 5000;
  let index = 0, animations = [], dimensions = '', running = false;
  let inView = false, hovering = false, pagePresent = true, focused = true;
  const frame = document.createElement('div');
  frame.className = 'ew-progress';
  frame.setAttribute('aria-hidden', 'true');
  frame.dataset.testid = 'ew-feature-progress';
  const edges = ['top', 'right', 'bottom', 'left'].map(edge => {
    const node = document.createElement('span');
    node.className = 'ew-progress-active ew-progress-' + edge;
    node.dataset.testid = 'ew-progress-' + edge;
    frame.appendChild(node);
    return node;
  });
  panel.appendChild(frame);
  const eligible = () => !reduced.matches && !document.hidden && pagePresent && focused && inView && !hovering;

  function preloadNext() {
    const next = slides[(index + 1) % slides.length];
    if (!next?.dataset.srcDeferred) return;
    delete next.dataset.srcDeferred;
    const image = new Image();
    image.src = next.currentSrc || next.src;
  }
  function advance() {
    slides[index].classList.remove('is-active');
    index = (index + 1) % slides.length;
    slides[index].classList.add('is-active');
    preloadNext();
  }
  function stop() {
    animations.forEach(animation => animation.pause());
    running = false;
  }
  function sync() {
    frame.hidden = reduced.matches;
    if (!eligible()) { stop(); return; }
    if (running || !animations.length) return;
    if (Number(animations[0].currentTime) >= DURATION) {
      advance();
      animations.forEach(animation => { animation.currentTime = 0; });
    }
    // Identical start time prevents the four sides from drifting apart.
    const elapsed = Number(animations[0].currentTime) || 0;
    const start = document.timeline.currentTime - elapsed;
    animations.forEach(animation => { animation.play(); animation.startTime = start; });
    running = true;
    preloadNext();
  }
  function measure() {
    const rect = panel.getBoundingClientRect();
    const w = Math.max(1, Math.round(rect.width) - 2);
    const h = Math.max(1, Math.round(rect.height) - 2);
    const size = w + ':' + h;
    if (size === dimensions) return;
    dimensions = size;
    const elapsed = Number(animations[0]?.currentTime) || 0;
    animations.forEach(animation => { animation.onfinish = null; animation.cancel(); });
    const lengths = [w, h, w, h];
    const perimeter = (w + h) * 2;
    let offset = 0;
    animations = edges.map((edge, i) => {
      const from = offset / perimeter;
      offset += lengths[i];
      const to = offset / perimeter;
      const axis = i % 2 ? 'Y' : 'X';
      const animation = edge.animate([
        { transform: `scale${axis}(0)`, offset: 0 },
        { transform: `scale${axis}(0)`, offset: from },
        { transform: `scale${axis}(1)`, offset: to },
        { transform: `scale${axis}(1)`, offset: 1 }
      ], { duration: DURATION, easing: 'linear', fill: 'both' });
      animation.pause();
      animation.currentTime = Math.min(elapsed, DURATION);
      return animation;
    });
    animations[0].onfinish = () => {
      running = false;
      if (!eligible()) return;
      advance();
      animations.forEach(animation => { animation.currentTime = 0; });
      sync();
    };
    running = false;
    sync();
  }
  function restore() {
    hovering = false;
    const rect = section.getBoundingClientRect();
    inView = rect.bottom > -120 && rect.top < innerHeight + 120;
    running = false;
    sync();
  }
  // Real mouse movement, not synthetic touch hover or an element scrolling under a cursor.
  media.addEventListener('pointermove', event => {
    if (event.pointerType !== 'mouse' || !canHover.matches || hovering) return;
    hovering = true;
    sync();
  });
  media.addEventListener('pointerleave', () => { hovering = false; sync(); });
  window.addEventListener('scroll', () => { if (hovering) { hovering = false; sync(); } }, { passive: true });
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) stop(); else { focused = true; restore(); }
  });
  window.addEventListener('pagehide', () => { pagePresent = false; hovering = false; stop(); });
  window.addEventListener('pageshow', () => { pagePresent = true; focused = true; restore(); });
  window.addEventListener('blur', () => { focused = false; hovering = false; stop(); });
  window.addEventListener('focus', () => { focused = true; restore(); });
  if ('ResizeObserver' in window) new ResizeObserver(measure).observe(panel);
  else window.addEventListener('resize', measure);
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(entries => entries.forEach(entry => {
      inView = entry.isIntersecting;
      sync();
    }), { rootMargin: '120px 0px' }).observe(section);
  } else inView = true;
  reduced.addEventListener?.('change', sync);
  measure();
  sync();
})();