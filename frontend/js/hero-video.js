/* One lifecycle owner for decorative hero videos. Never reload or seek the media. */
let initialized = false;

export function initHeroVideos() {
  if (initialized) return;
  initialized = true;
  const videos = [...document.querySelectorAll('video[data-hero-video], video.hero-video, video.ew-hero-video, video.ana-hero-video')];
  if (!videos.length) return;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let pagePresent = true;
  let focused = true;
  const onscreen = video => {
    const r = video.getBoundingClientRect();
    return r.width > 0 && r.height > 0 && r.bottom > 0 && r.top < innerHeight && r.right > 0 && r.left < innerWidth;
  };
  const states = videos.map(video => ({ video, inView: onscreen(video), active: false,
    userPaused: false, expectedPauses: 0, pending: false, token: 0, attempts: 0,
    blocked: false, probe: null, frame: null, verified: false }));
  const available = s => pagePresent && focused && !document.hidden && !reduced.matches && s.inView;

  function clearProbe(s) {
    clearTimeout(s.probe);
    s.probe = null;
    if (s.frame !== null && s.video.cancelVideoFrameCallback) s.video.cancelVideoFrameCallback(s.frame);
    s.frame = null;
  }
  function suspend(s) {
    clearProbe(s);
    s.token++;
    s.pending = false;
    if (!s.video.paused) {
      s.expectedPauses++;
      s.video.pause();
    }
  }
  function probeProgress(s) {
    if (s.probe !== null || s.verified || !available(s) || s.userPaused || s.video.paused) return;
    const time = s.video.currentTime;
    let presented = false;
    if (s.video.requestVideoFrameCallback) {
      s.frame = s.video.requestVideoFrameCallback((_now, metadata) => {
        presented = Math.abs(metadata.mediaTime - time) > .01;
        s.frame = null;
      });
    }
    // One bounded check after activation/data recovery, NOT a permanent timer loop.
    s.probe = setTimeout(() => {
      clearProbe(s);
      if (!available(s) || s.userPaused || s.video.paused) return;
      // WebKit may throttle frame callbacks independently of playback. Either real
      // clock progress OR a presented frame proves life; never interrupt healthy media.
      const advancing = Math.abs(s.video.currentTime - time) > .04 || presented;
      if (advancing) { s.verified = true; return; }
      // Do not churn the decoder while waiting for network data. Max3 attempts/activation.
      if (s.video.readyState >= 3 && s.attempts < 3) {
        suspend(s);
        play(s);
      }
    }, 1800);
  }
  function play(s) {
    if (!available(s) || s.userPaused || s.blocked || s.pending || s.video.error || s.attempts >= 3) return;
    s.pending = true;
    s.attempts++;
    const token = ++s.token;
    let result;
    try { result = s.video.play(); } catch (error) { result = Promise.reject(error); }
    Promise.resolve(result).then(() => {
      if (token !== s.token) return;
      s.video.dataset.heroPlayback = 'playing';
      probeProgress(s);
    }).catch(error => {
      if (token !== s.token) return;
      s.blocked = error.name === 'NotAllowedError';
      s.video.dataset.heroPlayback = s.blocked ? 'gesture-required' : 'waiting';
      // No recursive play retry: data/lifecycle events or a real gesture may retry.
    }).finally(() => { if (token === s.token) s.pending = false; });
  }
  function reconcile(s) {
    const active = available(s);
    if (!active) { s.active = false; suspend(s); return; }
    if (!s.active) { s.attempts = 0; s.verified = false; }
    s.active = true;
    if (s.userPaused) return;
    if (s.video.paused || s.video.ended) play(s); else probeProgress(s);
  }
  function refresh() {
    states.forEach(s => { s.inView = onscreen(s.video); reconcile(s); });
  }

  states.forEach(s => {
    const v = s.video;
    v.muted = true;
    v.defaultMuted = true;
    v.playsInline = true;
    v.setAttribute('playsinline', '');
    v.setAttribute('webkit-playsinline', 'true');
    v.dataset.heroManaged = 'true';
    v.addEventListener('pause', () => {
      if (s.expectedPauses) { s.expectedPauses--; return; }
      // A visible, foreground pause not made by us is intentional; never override it.
      if (available(s) && onscreen(v) && document.hasFocus()) {
        s.userPaused = true;
        v.dataset.heroPlayback = 'user-paused';
      }
      clearProbe(s);
    });
    v.addEventListener('play', () => {
      if (!s.pending) s.userPaused = false; // native/user resume
      if (!available(s)) suspend(s); else probeProgress(s);
    });
    ['loadeddata', 'canplay'].forEach(event => v.addEventListener(event, () => reconcile(s)));
    ['waiting', 'stalled'].forEach(event => v.addEventListener(event, () => { s.verified = false; probeProgress(s); }));
    v.addEventListener('error', () => clearProbe(s));
    // Explicit intent hooks for any future custom playback control; native pause also works.
    v.addEventListener('nova:hero-pause', () => { s.userPaused = true; suspend(s); });
    v.addEventListener('nova:hero-resume', () => { s.userPaused = false; s.blocked = false; s.attempts = 0; reconcile(s); });
  });

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => entries.forEach(entry => {
      const s = states.find(state => state.video === entry.target);
      s.inView = entry.isIntersecting && entry.intersectionRatio > 0;
      reconcile(s);
    }), { threshold: [0, .01] });
    states.forEach(s => observer.observe(s.video));
  } else {
    let queued = false;
    window.addEventListener('scroll', () => {
      if (queued) return;
      queued = true;
      requestAnimationFrame(() => { queued = false; refresh(); });
    }, { passive: true });
  }
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) focused = true;
    refresh();
  });
  window.addEventListener('pagehide', () => { pagePresent = false; states.forEach(s => { s.active = false; suspend(s); }); });
  window.addEventListener('pageshow', () => { pagePresent = true; focused = true; refresh(); });
  window.addEventListener('blur', () => { focused = false; refresh(); });
  window.addEventListener('focus', () => { focused = true; refresh(); });
  window.addEventListener('resize', refresh, { passive: true });
  reduced.addEventListener?.('change', refresh);
  function userGesture() {
    states.forEach(s => {
      if (!s.blocked || !available(s) || s.userPaused) return;
      s.blocked = false;
      s.attempts = 0;
      play(s);
    });
  }
  window.addEventListener('PointerEvent' in window ? 'pointerdown' : 'touchstart', userGesture, { passive: true });
  window.addEventListener('keydown', userGesture);
  refresh();
}