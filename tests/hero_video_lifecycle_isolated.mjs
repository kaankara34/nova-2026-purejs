import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

class Emitter {
  constructor() { this.listeners = new Map(); }
  addEventListener(type, cb) {
    if (!this.listeners.has(type)) this.listeners.set(type, []);
    this.listeners.get(type).push(cb);
  }
  dispatchEvent(event) {
    const list = this.listeners.get(event.type) || [];
    for (const cb of list) cb(event);
  }
  listenerCount(type) { return (this.listeners.get(type) || []).length; }
}

class FakeClock {
  constructor() { this.now = 0; this.jobs = []; this.nextId = 1; }
  setTimeout(fn, delay = 0) {
    const id = this.nextId++;
    this.jobs.push({ id, at: this.now + delay, fn, cleared: false });
    return id;
  }
  clearTimeout(id) {
    const job = this.jobs.find(j => j.id === id);
    if (job) job.cleared = true;
  }
  advance(ms) {
    const target = this.now + ms;
    while (true) {
      let next = null;
      for (const job of this.jobs) {
        if (!job.cleared && job.at <= target && (!next || job.at < next.at)) next = job;
      }
      if (!next) break;
      this.now = next.at;
      next.cleared = true;
      next.fn();
    }
    this.now = target;
  }
  activeJobs() { return this.jobs.filter(j => !j.cleared).length; }
}

class FakeMediaQuery extends Emitter {
  constructor(matches = false) {
    super();
    this.matches = matches;
  }
  setMatches(value) {
    this.matches = value;
    this.dispatchEvent({ type: 'change' });
  }
}

class FakeVideo extends Emitter {
  constructor(opts = {}) {
    super();
    this.dataset = {};
    this.attrs = {};
    this.paused = opts.paused ?? true;
    this.ended = false;
    this.error = null;
    this.defaultMuted = false;
    this.muted = false;
    this.playsInline = false;
    this.readyState = opts.readyState ?? 4;
    this._currentTime = opts.currentTime ?? 0;
    this._rect = opts.rect ?? { top: 0, left: 0, right: 100, bottom: 100, width: 100, height: 100 };
    this.playCalls = 0;
    this.pauseCalls = 0;
    this.loadCalls = 0;
    this.currentTimeWrites = 0;
    this.srcWrites = 0;
    this.pendingResolvers = [];
    this._mode = 'resolve';
    this._errorName = 'AbortError';
    this._rvfc = null;
    this._cancelledFrame = false;
  }
  get currentTime() { return this._currentTime; }
  set currentTime(v) { this.currentTimeWrites++; this._currentTime = v; }
  get src() { return this._src || ''; }
  set src(v) { this.srcWrites++; this._src = v; }
  setAttribute(k, v) { this.attrs[k] = v; }
  getBoundingClientRect() { return this._rect; }
  setRect(rect) { this._rect = rect; }
  load() { this.loadCalls++; }
  configurePlay(mode, errorName = 'AbortError') {
    this._mode = mode;
    this._errorName = errorName;
  }
  play() {
    this.playCalls++;
    if (this._mode === 'resolve') {
      this.paused = false;
      this.dispatchEvent({ type: 'play' });
      return Promise.resolve();
    }
    if (this._mode === 'reject') {
      const err = new Error(this._errorName);
      err.name = this._errorName;
      return Promise.reject(err);
    }
    return new Promise((resolve, reject) => {
      this.pendingResolvers.push({ resolve, reject });
    });
  }
  resolvePending(index = 0) {
    const pending = this.pendingResolvers[index];
    if (!pending) return;
    this.paused = false;
    this.dispatchEvent({ type: 'play' });
    pending.resolve();
  }
  rejectPending(index = 0, name = 'AbortError') {
    const pending = this.pendingResolvers[index];
    if (!pending) return;
    const err = new Error(name);
    err.name = name;
    pending.reject(err);
  }
  pause() {
    this.pauseCalls++;
    this.paused = true;
    this.dispatchEvent({ type: 'pause' });
  }
  requestVideoFrameCallback(cb) {
    this._rvfc = cb;
    return 1;
  }
  cancelVideoFrameCallback() {
    this._cancelledFrame = true;
    this._rvfc = null;
  }
  emitFrame(mediaTime) {
    if (this._rvfc) {
      const cb = this._rvfc;
      this._rvfc = null;
      cb(0, { mediaTime });
    }
  }
}

function makeEnv({ reduced = false, hidden = false, hasFocus = true, video } = {}) {
  const win = new Emitter();
  const doc = new Emitter();
  const mq = new FakeMediaQuery(reduced);
  const clock = new FakeClock();
  const v = video || new FakeVideo();

  doc.hidden = hidden;
  doc.hasFocus = () => hasFocus;
  doc.querySelectorAll = selector => selector.includes('video') ? [v] : [];

  win.innerWidth = 1920;
  win.innerHeight = 1080;
  win.matchMedia = () => mq;
  win.requestAnimationFrame = fn => clock.setTimeout(() => fn(clock.now), 16);
  win.clearTimeout = id => clock.clearTimeout(id);
  win.setTimeout = (fn, ms) => clock.setTimeout(fn, ms);
  win.IntersectionObserver = class {
    constructor(cb) { this.cb = cb; }
    observe(target) { this.cb([{ target, isIntersecting: true, intersectionRatio: 1 }]); }
  };

  globalThis.window = win;
  globalThis.document = doc;
  globalThis.innerWidth = win.innerWidth;
  globalThis.innerHeight = win.innerHeight;
  globalThis.matchMedia = win.matchMedia;
  globalThis.requestAnimationFrame = win.requestAnimationFrame;
  globalThis.setTimeout = win.setTimeout;
  globalThis.clearTimeout = win.clearTimeout;
  globalThis.IntersectionObserver = win.IntersectionObserver;

  return { win, doc, mq, clock, video: v };
}

async function loadHeroModuleFresh() {
  const src = await readFile('/app/frontend/js/hero-video.js', 'utf8');
  const encoded = Buffer.from(`${src}\n//# sourceURL=hero-video.js?${Date.now()}-${Math.random()}`).toString('base64');
  return import(`data:text/javascript;base64,${encoded}`);
}

async function flush() {
  await Promise.resolve();
  await Promise.resolve();
}

async function run(name, fn) {
  try {
    await fn();
    console.log(`PASS ${name}`);
  } catch (err) {
    console.error(`FAIL ${name}: ${err.stack || err.message}`);
    process.exitCode = 1;
  }
}

await run('idempotent init and no duplicate listeners', async () => {
  const env = makeEnv();
  const { initHeroVideos } = await loadHeroModuleFresh();
  initHeroVideos();
  const firstPauseListeners = env.video.listenerCount('pause');
  initHeroVideos();
  assert.equal(env.video.listenerCount('pause'), firstPauseListeners);
  assert.equal(env.video.playCalls, 1);
});

await run('max 3 attempts and bounded watchdog retries', async () => {
  const env = makeEnv();
  env.video.configurePlay('resolve');
  env.video._currentTime = 0;
  const { initHeroVideos } = await loadHeroModuleFresh();
  initHeroVideos();
  await flush();
  env.clock.advance(1800);
  await flush();
  env.clock.advance(1800);
  await flush();
  env.clock.advance(1800);
  await flush();
  assert.equal(env.video.playCalls, 3);
  assert.ok(env.clock.activeJobs() <= 1);
});

await run('only one pending play while unresolved', async () => {
  const env = makeEnv();
  env.video.configurePlay('pending');
  const { initHeroVideos } = await loadHeroModuleFresh();
  initHeroVideos();
  env.video.dispatchEvent({ type: 'loadeddata' });
  await flush();
  assert.equal(env.video.playCalls, 1);
});

await run('NotAllowed waits for real gesture then retries', async () => {
  const env = makeEnv();
  env.video.configurePlay('reject', 'NotAllowedError');
  const { initHeroVideos } = await loadHeroModuleFresh();
  initHeroVideos();
  await flush();
  assert.equal(env.video.dataset.heroPlayback, 'gesture-required');
  env.video.configurePlay('resolve');
  env.win.dispatchEvent({ type: 'touchstart' });
  await flush();
  assert.equal(env.video.playCalls, 2);
  assert.equal(env.video.dataset.heroPlayback, 'playing');
});

await run('late play resolution does not override latest token state', async () => {
  const env = makeEnv();
  env.video.configurePlay('pending');
  const { initHeroVideos } = await loadHeroModuleFresh();
  initHeroVideos();
  env.win.dispatchEvent({ type: 'blur' });
  env.video.configurePlay('resolve');
  env.win.dispatchEvent({ type: 'focus' });
  await flush();
  assert.equal(env.video.playCalls, 2);
  env.video.resolvePending(0);
  await flush();
  assert.equal(env.video.dataset.heroPlayback, 'playing');
});

await run('visibility/pagehide pauses and resume works', async () => {
  const env = makeEnv();
  const { initHeroVideos } = await loadHeroModuleFresh();
  initHeroVideos();
  await flush();
  env.doc.hidden = true;
  env.doc.dispatchEvent({ type: 'visibilitychange' });
  assert.equal(env.video.paused, true);
  env.doc.hidden = false;
  env.doc.dispatchEvent({ type: 'visibilitychange' });
  await flush();
  assert.equal(env.video.paused, false);
  env.win.dispatchEvent({ type: 'pagehide' });
  assert.equal(env.video.paused, true);
  env.win.dispatchEvent({ type: 'pageshow' });
  await flush();
  assert.equal(env.video.paused, false);
});

await run('manual visible pause persists until explicit resume', async () => {
  const env = makeEnv();
  const { initHeroVideos } = await loadHeroModuleFresh();
  initHeroVideos();
  await flush();
  env.video.pause();
  assert.equal(env.video.dataset.heroPlayback, 'user-paused');
  env.win.dispatchEvent({ type: 'focus' });
  await flush();
  assert.equal(env.video.paused, true);
  env.video.dispatchEvent({ type: 'nova:hero-resume' });
  await flush();
  assert.equal(env.video.paused, false);
});

await run('reduced motion blocks autoplay until motion allowed', async () => {
  const env = makeEnv({ reduced: true });
  const { initHeroVideos } = await loadHeroModuleFresh();
  initHeroVideos();
  await flush();
  assert.equal(env.video.playCalls, 0);
  env.mq.setMatches(false);
  await flush();
  assert.equal(env.video.playCalls, 1);
});

await run('no load/seek/source mutation side-effects', async () => {
  const env = makeEnv();
  const { initHeroVideos } = await loadHeroModuleFresh();
  initHeroVideos();
  env.video.dispatchEvent({ type: 'stalled' });
  env.clock.advance(1800);
  await flush();
  assert.equal(env.video.loadCalls, 0);
  assert.equal(env.video.currentTimeWrites, 0);
  assert.equal(env.video.srcWrites, 0);
});

await run('progress proof accepts clock OR frame callback evidence', async () => {
  // clock-only proof
  {
    const env = makeEnv();
    env.video.requestVideoFrameCallback = undefined;
    const { initHeroVideos } = await loadHeroModuleFresh();
    initHeroVideos();
    await flush();
    env.video._currentTime = 0.12;
    env.clock.advance(1800);
    await flush();
    assert.equal(env.video.playCalls, 1);
  }
  // frame-only proof with no clock change
  {
    const env = makeEnv();
    const { initHeroVideos } = await loadHeroModuleFresh();
    initHeroVideos();
    await flush();
    env.video.emitFrame(0.08);
    env.clock.advance(1800);
    await flush();
    assert.equal(env.video.playCalls, 1);
  }
});

if (!process.exitCode) console.log('ALL HERO LIFECYCLE ISOLATED TESTS PASSED');