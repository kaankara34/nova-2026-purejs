/* ==========================================================
   ARCHITECTS & DESIGNERS — seamless card marquee.
   rAF transform loop with drag/swipe takeover. No library.
   ========================================================== */
(function () {
  'use strict';

  const viewport = document.getElementById('architectsMarquee');
  const track = document.getElementById('architectsTrack');
  if (!viewport || !track) return;

  const groups = Array.prototype.slice.call(track.querySelectorAll('[data-ad-group]'));
  if (groups.length < 2) return;

  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const RESUME_DELAY = 2000;
  const LOOP_SECONDS = 36;

  let groupWidth = 0;
  let offset = 0;
  let speed = 0;            // px per ms
  let last = 0;
  let raf = null;
  let hovering = false;
  let focused = false;
  let dragging = false;
  let inView = true;
  let resumeTimer = null;
  let dragStartX = 0;
  let dragStartOffset = 0;
  let dragMoved = 0;

  function measure() {
    const styles = window.getComputedStyle(track);
    const gap = parseFloat(styles.columnGap || styles.gap || '0') || 0;
    groupWidth = groups[0].getBoundingClientRect().width + gap;
    speed = groupWidth / (LOOP_SECONDS * 1000);
    normalise();
    apply();
  }

  function normalise() {
    if (!groupWidth) return;
    while (offset <= -groupWidth) offset += groupWidth;
    while (offset > 0) offset -= groupWidth;
  }

  function apply() {
    track.style.transform = 'translate3d(' + offset.toFixed(2) + 'px, 0, 0)';
  }

  function running() {
    return !reduced.matches && inView && !hovering && !focused && !dragging && !document.hidden;
  }

  function tick(now) {
    raf = requestAnimationFrame(tick);
    if (!last) last = now;
    const delta = now - last;
    last = now;
    viewport.dataset.adRunning = running() ? '1' : '0';
    if (!running() || delta > 400) return;
    offset -= speed * delta;
    normalise();
    apply();
  }

  function startLoop() {
    if (raf || reduced.matches) return;
    last = 0;
    raf = requestAnimationFrame(tick);
  }

  function stopLoop() {
    if (raf) { cancelAnimationFrame(raf); raf = null; }
  }

  function scheduleResume() {
    clearTimeout(resumeTimer);
    resumeTimer = setTimeout(function () { last = 0; }, RESUME_DELAY);
  }

  /* ---- pointer drag / touch swipe ---- */
  function pointerDown(event) {
    if (reduced.matches) return;
    if (event.pointerType === 'mouse' && event.button !== 0) return;
    dragging = true;
    dragMoved = 0;
    dragStartX = event.clientX;
    dragStartOffset = offset;
    viewport.classList.add('is-dragging');
    try { viewport.setPointerCapture(event.pointerId); } catch (err) { /* capture is optional */ }
  }

  function pointerMove(event) {
    if (!dragging) return;
    const delta = event.clientX - dragStartX;
    dragMoved = Math.abs(delta);
    // Let the browser keep vertical scrolling: only take over past a small threshold.
    if (dragMoved < 8) return;
    offset = dragStartOffset + delta;
    normalise();
    apply();
  }

  function pointerUp(event) {
    if (!dragging) return;
    dragging = false;
    viewport.classList.remove('is-dragging');
    try {
      if (event && viewport.hasPointerCapture && viewport.hasPointerCapture(event.pointerId)) {
        viewport.releasePointerCapture(event.pointerId);
      }
    } catch (err) { /* already released */ }
    scheduleResume();
  }

  viewport.addEventListener('pointerdown', pointerDown);
  viewport.addEventListener('pointermove', pointerMove);
  viewport.addEventListener('pointerup', pointerUp);
  viewport.addEventListener('pointercancel', pointerUp);
  window.addEventListener('pointerup', pointerUp);
  window.addEventListener('mouseup', function () { pointerUp(null); });
  window.addEventListener('blur', function () { pointerUp(null); });
  viewport.addEventListener('dragstart', function (event) { event.preventDefault(); });
  viewport.addEventListener('click', function (event) {
    if (dragMoved > 8) { event.preventDefault(); event.stopPropagation(); }
  }, true);

  viewport.addEventListener('mouseenter', function () { hovering = true; });
  viewport.addEventListener('mouseleave', function () { hovering = false; last = 0; });
  viewport.addEventListener('focusin', function (event) {
    // Pause for keyboard focus only — a pointer drag also focuses the strip.
    try {
      const target = event.target;
      focused = viewport.matches(':focus-visible') ||
        !!(target && target.matches && target.matches(':focus-visible'));
    } catch (err) {
      focused = true;
    }
  });
  viewport.addEventListener('focusout', function () { focused = false; last = 0; });
  document.addEventListener('visibilitychange', function () { last = 0; });

  viewport.addEventListener('keydown', function (event) {
    focused = true;
    const step = groupWidth / groups[0].children.length;
    if (event.key === 'ArrowRight') { offset -= step; normalise(); apply(); event.preventDefault(); }
    if (event.key === 'ArrowLeft') { offset += step; normalise(); apply(); event.preventDefault(); }
  });

  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        inView = entry.isIntersecting;
        if (inView) { last = 0; startLoop(); } else { stopLoop(); }
      });
    }, { rootMargin: '150px 0px' });
    io.observe(viewport);
  }

  let resizeTimer = null;
  window.addEventListener('resize', function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(measure, 150);
  });

  if (reduced.addEventListener) {
    reduced.addEventListener('change', function () {
      if (reduced.matches) { stopLoop(); track.style.transform = 'none'; } else { measure(); startLoop(); }
    });
  }

  measure();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(measure);
  window.addEventListener('load', measure, { once: true });
  startLoop();
})();
