/* East West feature: one visible-time clock, compositor-only perimeter and glint. */
(function () {
  'use strict';
  const section = document.getElementById('eastWestFeature');
  const media = document.getElementById('ewFeatureMedia');
  if (!section || !media || section.dataset.progressReady) return;
  const panel = section.querySelector('.ew-feature-inner') || section;
  const slides = [...media.querySelectorAll('[data-ew-slide]')];
  if (slides.length < 2) return;
  section.dataset.progressReady = 'true';
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const canHover = matchMedia('(hover: hover) and (pointer: fine)');
  const DURATION = 5000;
  let index = 0, animations = [], dimensions = '', running = false;
  let inView = false, hovering = false, pagePresent = true;
  let elapsed = 0, startedAt = 0, completedCycles = 0, cycleTimer = null, scrollFrame = null;
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
  const glint = document.createElement('span');
  glint.className = 'ew-progress-glint';
  glint.dataset.testid = 'ew-progress-glint';
  frame.appendChild(glint);
  panel.appendChild(frame);

  // Window focus is NOT visibility: mobile browser chrome may blur without a focus return.
  const eligible = () => !reduced.matches && !document.hidden && pagePresent && inView && !hovering;
  const clock = () => elapsed + (running ? performance.now() - startedAt : 0);
  function showCycle(time) {
    const cycle = Math.floor(time / DURATION);
    if (cycle === completedCycles) return;
    slides[index].classList.remove('is-active');
    index = (index + cycle - completedCycles) % slides.length;
    slides[index].classList.add('is-active');
    completedCycles = cycle;
  }
  function preloadNext() {
    const next = slides[(index + 1) % slides.length];
    if (!next?.dataset.srcDeferred) return;
    delete next.dataset.srcDeferred;
    const image = new Image();
    image.src = next.currentSrc || next.src;
  }
  function stop() {
    elapsed = clock();
    running = false;
    clearTimeout(cycleTimer);
    cycleTimer = null;
    animations.forEach(animation => animation.pause());
  }
  function alignAnimations(time) {
    const timeline = document.timeline.currentTime;
    animations.forEach(animation => {
      animation.currentTime = time;
      animation.play();
      if (timeline !== null) animation.startTime = timeline - time;
    });
  }
  function scheduleCycle() {
    clearTimeout(cycleTimer);
    // One callback per slideshow cycle, never per frame. Infinite native animations
    // do not depend on a finish event arriving to restart the border on mobile.
    cycleTimer = setTimeout(() => {
      cycleTimer = null;
      if (!eligible()) { sync(); return; }
      const time = clock();
      showCycle(time);
      preloadNext();
      if (animations.some(a => a.playState !== 'running') ||
          Math.abs(Number(animations[0]?.currentTime) - time) > 250) alignAnimations(time);
      scheduleCycle();
    }, DURATION - (clock() % DURATION) + 20);
  }
  function sync() {
    frame.hidden = reduced.matches;
    if (!eligible()) { if (running) stop(); return; }
    if (!animations.length) return;
    if (running) {
      if (animations.some(a => !a.pending && a.playState !== 'running')) alignAnimations(clock());
      return;
    }
    startedAt = performance.now();
    running = true;
    showCycle(elapsed);
    alignAnimations(elapsed);
    scheduleCycle();
    preloadNext();
  }
  function measure() {
    const rect = panel.getBoundingClientRect();
    const w = Math.max(1, Math.round(rect.width));
    const h = Math.max(1, Math.round(rect.height));
    const size = w + ':' + h;
    if (size === dimensions) return;
    stop();
    dimensions = size;
    animations.forEach(animation => animation.cancel());
    const lengths = [w, h, w, h], perimeter = (w + h) * 2;
    let offset = 0;
    animations = edges.map((edge, i) => {
      const from = offset / perimeter;
      offset += lengths[i];
      const to = offset / perimeter;
      const axis = i % 2 ? 'Y' : 'X';
      return edge.animate([
        { transform: `scale${axis}(0)`, offset: 0 },
        { transform: `scale${axis}(0)`, offset: from },
        { transform: `scale${axis}(1)`, offset: to },
        { transform: `scale${axis}(1)`, offset: 1 }
      ], { duration: DURATION, iterations: Infinity, easing: 'linear', fill: 'both' });
    });
    const x = Math.max(0, w - 5), y = Math.max(0, h - 5);
    animations.push(glint.animate([
      { transform: 'translate(0px, 0px)', offset: 0 },
      { transform: `translate(${x}px, 0px)`, offset: w / perimeter },
      { transform: `translate(${x}px, ${y}px)`, offset: (w + h) / perimeter },
      { transform: `translate(0px, ${y}px)`, offset: (2 * w + h) / perimeter },
      { transform: 'translate(0px, 0px)', offset: 1 }
    ], { duration: DURATION, iterations: Infinity, easing: 'linear', fill: 'both' }));
    animations.forEach(animation => { animation.pause(); animation.currentTime = elapsed; });
    sync();
  }
  function restore() {
    hovering = false;
    const rect = section.getBoundingClientRect();
    inView = rect.bottom > -120 && rect.top < innerHeight + 120;
    sync();
  }
  media.addEventListener('pointermove', event => {
    if (event.pointerType !== 'mouse' || !canHover.matches || hovering) return;
    hovering = true;
    sync();
  });
  media.addEventListener('pointerleave', () => { hovering = false; sync(); });
  // Touch/pointer recovery also clears a stale desktop-hover flag on hybrid devices.
  section.addEventListener('pointerdown', event => { if (event.pointerType !== 'mouse') restore(); }, { passive: true });
  window.addEventListener('scroll', () => {
    if (scrollFrame !== null) return;
    scrollFrame = requestAnimationFrame(() => { scrollFrame = null; restore(); });
  }, { passive: true });
  document.addEventListener('visibilitychange', () => { if (document.hidden) stop(); else restore(); });
  window.addEventListener('pagehide', () => {
    pagePresent = false;
    hovering = false;
    cancelAnimationFrame(scrollFrame);
    scrollFrame = null;
    stop();
  });
  window.addEventListener('pageshow', () => { pagePresent = true; restore(); });
  window.addEventListener('focus', restore); // Optional recovery, never a required gate.
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