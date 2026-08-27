/* ==========================================================
   CONSTRUCTION & ENGINEERING
   Mechanical motion language: assembly, rotation, load transfer,
   sectional cuts, alignment, measurement.
   GSAP ScrollTrigger + three.js reinforcement models.
   ========================================================== */
import * as THREE from 'three';

const body = document.body;
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
const seg = (p, a, b) => clamp((p - a) / (b - a), 0, 1);
const $ = s => document.querySelector(s);
const $$ = s => Array.from(document.querySelectorAll(s));

/* ---------------- always-on interactions ---------------- */
/* MEP layer tabs */
const mepTabs = $$('.cx-mep-tab');
const mepLayers = $$('.cx-mep-layer');
const mepCap = $('.cx-mep-cap');
const mepCaps = [
  'Structure \u2014 columns, slabs and beams; no unplanned penetrations',
  'Architecture \u2014 occupied spaces, access and maintenance zones',
  'HVAC \u2014 duct routes within the coordinated zone and below slab soffit',
  'Electrical \u2014 containment and risers coordinated with fire-safety zones',
  'Water \u2014 distribution, plant and access zones',
  'Drainage \u2014 gravity stacks and falls coordinated with structural zones',
  'Fire & life-safety interfaces \u2014 service penetrations through fire-resisting construction'
];
const mepSet = i => {
  mepTabs.forEach((o, j) => o.classList.toggle('is-on', j === i));
  mepLayers.forEach((l, j) => l.classList.toggle('is-on', j === i));
  if (mepCap) mepCap.textContent = mepCaps[i] || '';
};
mepTabs.forEach((t, i) => t.addEventListener('click', () => mepSet(i)));
if (mepTabs.length) mepSet(0);

/* structural element labels are also navigation into the pinned range */
const structSection = $('.cx-struct');
const els = $$('.cx-el');
els.forEach((el, i) => el.addEventListener('click', () => {
  if (!structSection) return;
  const r = structSection.getBoundingClientRect();
  const top = r.top + scrollY;
  const usable = structSection.offsetHeight - innerHeight;
  if (usable <= 40) { // static mode — just highlight
    els.forEach((o, j) => o.classList.toggle('is-on', j === i));
    return;
  }
  scrollTo({ top: top + usable * ((i + 0.45) / els.length), behavior: 'smooth' });
}));

if (reduce) {
  body.classList.add('cx-static', 'cx-nogl');
  $$('[data-cx-in]').forEach(el => el.classList.add('is-in'));
  $$('.cx-plot').forEach(el => el.classList.add('is-in'));
  $$('.cx-el, .cx-state, .cx-prin, .cx-wp-node, .cx-stepcard, .cx-insp-col, .cx-gr').forEach(el => el.classList.add('is-on'));
  $$('[data-draw] [pathLength]').forEach(el => { el.style.strokeDashoffset = '0'; });
} else {
  gsap.registerPlugin(ScrollTrigger);
  boot();
}

function boot() {
  /* drawing captions are measured against their own viewBox so a long annotation
     is condensed instead of being cut at the drawing edge on small screens */
  const fitSvgText = () => {
    $$('.cx-dwg text').forEach(t => {
      const svg = t.ownerSVGElement;
      const vb = svg && svg.viewBox && svg.viewBox.baseVal;
      if (!vb || !vb.width) return;
      t.removeAttribute('textLength');
      const x = parseFloat(t.getAttribute('x') || '0');
      const anchor = getComputedStyle(t).textAnchor;
      const avail = anchor === 'end'
        ? x - vb.x - 2
        : anchor === 'middle'
          ? Math.min(x - vb.x, vb.x + vb.width - x) * 2 - 2
          : vb.x + vb.width - x - 4;
      let len = 0;
      try { len = t.getComputedTextLength(); } catch (e) { return; }
      if (avail > 24 && len > avail) {
        t.setAttribute('lengthAdjust', 'spacingAndGlyphs');
        t.setAttribute('textLength', avail.toFixed(1));
      }
    });
  };
  fitSvgText();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitSvgText);
  let fitT;
  addEventListener('resize', () => { clearTimeout(fitT); fitT = setTimeout(fitSvgText, 180); });

  /* ---------------- reveals + measurement draws ---------------- */
  const io = new IntersectionObserver(es => es.forEach(e => {
    /* also reveal anything the reader jumped past, so a fast jump never leaves
       an approved paragraph invisible */
    if (e.isIntersecting || e.boundingClientRect.bottom < 0) { e.target.classList.add('is-in'); io.unobserve(e.target); }
  }), { rootMargin: '0px 0px -10% 0px', threshold: .1 });
  $$('[data-cx-in], .cx-plot').forEach(el => io.observe(el));
  /* a jump that skips a block entirely never triggers the observer: sweep once
     the scroll settles so no approved paragraph can stay invisible */
  const sweep = () => $$('[data-cx-in]:not(.is-in), .cx-plot:not(.is-in)').forEach(el => {
    if (el.getBoundingClientRect().bottom < 0) { el.classList.add('is-in'); io.unobserve(el); }
  });
  let swT;
  addEventListener('scroll', () => { clearTimeout(swT); swT = setTimeout(sweep, 140); }, { passive: true });
  ScrollTrigger.addEventListener('refresh', sweep);

  $$('[data-draw]').forEach(host => {
    const paths = Array.from(host.querySelectorAll('[pathLength]'));
    if (!paths.length) return;
    paths.forEach(p => { p.style.strokeDasharray = 1; p.style.strokeDashoffset = 1; });
    ScrollTrigger.create({
      trigger: host, start: host.dataset.start || 'top 84%', end: host.dataset.end || 'bottom 62%', scrub: .5,
      onUpdate: self => {
        const n = paths.length, p = self.progress;
        paths.forEach((el, i) => {
          const s = (i / n) * .8;
          el.style.strokeDashoffset = (1 - clamp((p - s) / (1 / n), 0, 1)).toFixed(4);
        });
      }
    });
  });

  /* ---------------- 3D: reinforcement ---------------- */
  const gl = (() => { try { const c = document.createElement('canvas'); return !!(c.getContext('webgl2') || c.getContext('webgl')); } catch (e) { return false; } })();
  if (!gl) body.classList.add('cx-nogl');
  const mobile = innerWidth <= 900;

  function steelMat() {
    return new THREE.MeshStandardMaterial({ color: 0x87817a, roughness: .45, metalness: .86 });
  }
  /* deformed reinforcing bar: core + two longitudinal ribs + inclined transverse ribs
     wrapping both halves of the circumference (deformation pattern stays visible while rotating) */
  function rebar(len, r, mat) {
    const g = new THREE.Group();
    const rs = mobile ? 16 : 28;
    g.add(new THREE.Mesh(new THREE.CylinderGeometry(r * .96, r * .96, len, rs, 1), mat));
    const lrg = new THREE.BoxGeometry(r * .3, len, r * .22);
    [-1, 1].forEach(sd => {
      const m = new THREE.Mesh(lrg, mat);
      m.position.x = sd * r * .93;
      g.add(m);
    });
    const pitch = r * (mobile ? 1.55 : 1.12);
    const count = Math.max(6, Math.floor(len / pitch));
    const arc = Math.PI * .66;
    const trg = new THREE.TorusGeometry(r * .93, r * .135, mobile ? 5 : 8, mobile ? 12 : 20, arc);
    const AX = new THREE.Vector3(1, 0, 0), AY = new THREE.Vector3(0, 1, 0);
    const base = new THREE.Quaternion().setFromAxisAngle(AX, Math.PI / 2);
    [1, -1].forEach(side => {
      const inst = new THREE.InstancedMesh(trg, mat, count);
      const m4 = new THREE.Matrix4(), one = new THREE.Vector3(1, 1, 1);
      const tilt = new THREE.Quaternion().setFromAxisAngle(AX, side * .34);
      const spin = new THREE.Quaternion().setFromAxisAngle(AY, (side > 0 ? 0 : Math.PI) - arc / 2 + .18);
      const q = spin.clone().multiply(tilt).multiply(base);
      for (let i = 0; i < count; i++) {
        const y = -len / 2 + pitch * .6 + i * pitch + (side > 0 ? 0 : pitch * .5);
        m4.compose(new THREE.Vector3(0, y, 0), q, one);
        inst.setMatrixAt(i, m4);
      }
      inst.instanceMatrix.needsUpdate = true;
      g.add(inst);
    });
    return g;
  }
  /* --- reinforcement primitives -------------------------------------------
     Each transverse component is one continuous bent bar generated from a
     single polyline, so every hook is an integral continuation of the same bar
     and never a separate piece. Geometry is conceptual: no dimension, diameter,
     spacing or cover value is expressed. */
  function bentBar(pts, r, mat, closed, ribbed) {
    const g = new THREE.Group();
    const curve = new THREE.CatmullRomCurve3(pts, !!closed, 'catmullrom', 0);
    const len = curve.getLength();
    const seg = clamp(Math.round(len / (r * .8)), 20, 240);
    g.add(new THREE.Mesh(new THREE.TubeGeometry(curve, seg, r, mobile ? 5 : 9, !!closed), mat));
    if (ribbed) {
      const n = clamp(Math.floor(len / (r * 3.2)), 4, 80);
      const trg = new THREE.TorusGeometry(r * 1.01, r * .13, 4, 9);
      const inst = new THREE.InstancedMesh(trg, mat, n);
      const m4 = new THREE.Matrix4(), one = new THREE.Vector3(1, 1, 1);
      const q = new THREE.Quaternion(), zAx = new THREE.Vector3(0, 0, 1);
      for (let i = 0; i < n; i++) {
        const t = (i + .5) / n;
        q.setFromUnitVectors(zAx, curve.getTangentAt(t));
        m4.compose(curve.getPointAt(t), q, one);
        inst.setMatrixAt(i, m4);
      }
      inst.instanceMatrix.needsUpdate = true;
      g.add(inst);
    }
    return g;
  }
  /* closed perimeter hoop, horizontal plane: one continuous rectangular loop
     enclosing the longitudinal bars, closed at a corner by two inward-turned
     135-degree seismic hooks that continue from the loop itself */
  function perimeterHoop(hx, hz, r, mat, corner, ribbed) {
    const g = new THREE.Group();
    const cr = Math.min(hx, hz) * .26;
    const pts = [];
    [[hx - cr, hz - cr, 0], [-(hx - cr), hz - cr, Math.PI / 2],
     [-(hx - cr), -(hz - cr), Math.PI], [hx - cr, -(hz - cr), -Math.PI / 2]]
      .forEach(([cx, cz, a0]) => {
        for (let i = 0; i <= 6; i++) {
          const a = a0 + (i / 6) * Math.PI / 2;
          pts.push(new THREE.Vector3(cx + Math.cos(a) * cr, 0, cz + Math.sin(a) * cr));
        }
      });
    g.add(bentBar(pts, r, mat, true, ribbed));
    const sx = corner[0], sz = corner[1];
    const hl = Math.min(hx, hz) * .5;
    const dir = new THREE.Vector3(-sx, 0, -sz).normalize();
    [-1, 1].forEach(side => {
      /* the two loop ends turn back into the confined core at 135 degrees; the bend
         stays on the loop itself, so nothing projects outside the cage */
      const p0 = new THREE.Vector3(sx * (hx - cr * .12), side * r * 1.8, sz * (hz - cr * .12));
      const p1 = p0.clone().addScaledVector(dir, hl * .32).add(new THREE.Vector3(0, side * r * 1.1, 0));
      const p2 = p0.clone().addScaledVector(dir, hl).add(new THREE.Vector3(0, side * r * 2.4, 0));
      g.add(bentBar([p0, p1, p2], r, mat, false, ribbed));
    });
    return g;
  }
  /* single-leg cross-tie (TBDY 2018 detailing principle): one continuous bar
     across the short direction of the confined core; both ends bend around the
     longitudinal bar they restrain and turn back into the core as 135-degree
     seismic hooks, so the hooked ends read on the face of the cage */
  function crossTie(zBar, rBar, r, mat, flip, ribbed) {
    const hk = zBar * .5, y = 0;
    /* the leg reaches the longitudinal bar it restrains, bends around it against the
       perimeter hoop leg and returns into the core as a 135-degree hook; the bend
       never passes outside the hoop, so no bar end projects from the cage */
    const end = (sz, sy) => [
      new THREE.Vector3(0, y, sz * (zBar - r)),
      new THREE.Vector3(0, y + sy * r * .7, sz * (zBar + rBar * .75)),
      new THREE.Vector3(0, y + sy * (hk * .8 + r * 1.5), sz * (zBar - hk * .5))
    ];
    const a = end(-1, flip), b = end(1, -flip);
    const pts = [a[2], a[1], a[0], b[0], b[1], b[2]];
    return bentBar(pts, r, mat, false, ribbed);
  }
  function setMat(obj, m) {
    obj.traverse(o => { if (o.isMesh || o.isInstancedMesh) o.material = m; });
  }
  function scene3(canvas) {
    const renderer = new THREE.WebGLRenderer({ canvas, antialias: !mobile, alpha: true, powerPreference: 'high-performance' });
    renderer.setPixelRatio(Math.min(devicePixelRatio, mobile ? 1.5 : 2));
    const scene = new THREE.Scene();
    const cam = new THREE.PerspectiveCamera(34, 1, .1, 200);
    scene.add(new THREE.HemisphereLight(0xb7c0c6, 0x14171a, .95));
    const key = new THREE.DirectionalLight(0xfff2e2, 3.1); key.position.set(4, 6, 5); scene.add(key);
    const rim = new THREE.DirectionalLight(0xa9c0d6, 1.7); rim.position.set(-6, 2, -4); scene.add(rim);
    const fill = new THREE.DirectionalLight(0xffffff, .6); fill.position.set(0, -4, 6); scene.add(fill);
    function size() {
      const w = canvas.clientWidth || canvas.parentElement.clientWidth;
      const h = canvas.clientHeight || canvas.parentElement.clientHeight;
      renderer.setSize(w, h, false);
      cam.aspect = w / Math.max(1, h); cam.updateProjectionMatrix();
    }
    size();
    addEventListener('resize', size);
    return { renderer, scene, cam, key, rim, size };
  }

  /* ---------------- 01 hero ---------------- */
  const hero = $('.cx-hero');
  if (hero) {
    const canvas = $('#cxRebarCanvas');
    const readout = $('[data-testid="cx-hero-readout"]');
    const cue = $('.cx-cue');
    const grid = $$('.cx-hero-grid [pathLength]');
    const labels = ['MATERIAL', 'GEOMETRY', 'STRUCTURAL FUNCTION'];
    let last = -1, world = null;
    if (gl && canvas) {
      world = scene3(canvas);
      const mat = steelMat();
      const bars = [];
      const defs = mobile ? [[.5, .3, 5.6], [1.7, .26, 5.3], [2.85, .23, 5.1], [-.55, .27, 5.4]] : [[.75, .34, 6.6], [1.85, .28, 6.3], [2.8, .24, 6.1], [3.7, .3, 6.4], [-.35, .26, 6.2]];
      defs.forEach(([x, r, len], i) => {
        const b = rebar(len, r, mat);
        b.position.set(x, 0, -i * .55);
        b.rotation.z = 0.3 + i * .04;
        world.scene.add(b);
        bars.push(b);
      });
      world.cam.position.set(1.5, 0, 6.2);
      world.cam.lookAt(1.5, 0, 0);
      let need = true;
      const draw = () => { if (need) { world.renderer.render(world.scene, world.cam); need = false; } requestAnimationFrame(draw); };
      requestAnimationFrame(draw);
      ScrollTrigger.create({
        trigger: hero, start: 'top top', end: 'bottom bottom', scrub: .6,
        onUpdate: self => {
          const p = self.progress;
          /* the three reading phases are visible, not decorative:
             MATERIAL — close reading of the ribbed surface
             GEOMETRY — camera pulls back, bar spacing becomes readable
             STRUCTURAL FUNCTION — bars align into a structural arrangement */
          const pMat = seg(p, 0, .30), pGeo = seg(p, .30, .66), pFun = seg(p, .66, 1);
          bars.forEach((b, i) => {
            b.rotation.y = THREE.MathUtils.degToRad(p * (250 + i * 16));   // slow rotation about own axis
            b.position.x = defs[i][0] * (1 + pGeo * .42);                  // spacing opens up
            b.position.y = (i % 2 ? -1 : 1) * p * (.22 + i * .05);          // slight parallax
            b.position.z = -i * .55 + p * .3;
            b.rotation.z = (0.3 + i * .04) * (1 - pFun);                   // aligns into the cage
          });
          world.key.position.set(4 - p * 3.4, 6 - p * 2.2, 5 - p * 1.4);
          world.rim.intensity = 1.1 + pMat * .55;
          world.cam.position.z = 6.2 - pMat * .55 + pGeo * 1.25;
          world.cam.lookAt(1.5, 0, 0);
          need = true;
        }
      });
    }
    ScrollTrigger.create({
      trigger: hero, start: 'top top', end: 'bottom bottom', scrub: .5,
      onUpdate: self => {
        const p = self.progress;
        grid.forEach((g, i) => {
          g.style.strokeDashoffset = (1 - seg(p, i * .04, i * .04 + .26)).toFixed(3);
        });
        if (cue) cue.style.opacity = (1 - seg(p, 0, .12)).toFixed(3);
        const li = p < .30 ? 0 : p < .66 ? 1 : 2;
        if (li !== last && readout) { last = li; readout.textContent = labels[li]; }
      }
    });
  }

  /* ---------------- pinned copy tracking (content-aware) ----------------
     The pinned stages keep their original 100vh composition. When the approved
     copy is taller than the available column, the copy block is tracked to the
     canonical active state instead of being cut off. */
  function copyTracker(sec, itemSel, expandSel, keepActive) {
    if (!sec) return null;
    const win = sec.querySelector('.cx-copywin');
    const move = win && win.querySelector('.cx-copymove');
    if (!win || !move) return null;
    const rows = Array.from(win.querySelectorAll(itemSel));
    const exp = rows.map(r => (expandSel ? r.querySelector(expandSel) : null));
    let geo = null;
    function measure() {
      exp.forEach(d => { if (d) { d.style.transition = 'none'; d.style.maxHeight = '0px'; } });
      const top = move.getBoundingClientRect().top;
      const base = rows.map(r => { const b = r.getBoundingClientRect(); return { top: b.top - top, h: b.height }; });
      const collapsed = move.scrollHeight;
      const dh = exp.map(d => (d ? d.scrollHeight : 0));
      exp.forEach((d, i) => { if (d) { d.style.setProperty('--cx-dh', dh[i] + 'px'); d.style.maxHeight = ''; } });
      requestAnimationFrame(() => exp.forEach(d => { if (d) d.style.transition = ''; }));
      geo = { base, collapsed, dh, avail: win.clientHeight };
    }
    measure();
    ScrollTrigger.addEventListener('refreshInit', measure);
    return (idx, p) => {
      if (!geo || !geo.base[idx]) return;
      const grow = geo.dh[idx] ? geo.dh[idx] + 5 : 0;
      const total = geo.collapsed + grow;
      const over = total - geo.avail;
      win.classList.toggle('is-tracking', over > 0);
      const prog = clamp(p || 0, 0, 1);
      /* fits: the block drifts slowly from the top to the bottom of the column
         across the section, so neither transition leaves a dead band.
         taller than the column: track the canonical active state into view and,
         on the last state, continue to the end so the closing note is readable */
      let shift;
      if (over <= 0) {
        shift = -(geo.avail - total) * prog;
      } else {
        const aTop = geo.base[idx].top, aH = geo.base[idx].h + grow;
        const keepTop = Math.max(0, aTop - 14);
        const base = clamp(Math.min(Math.max(0, aTop + aH + 24 - geo.avail), keepTop), 0, over);
        if (idx === rows.length - 1) {
          const sub = clamp(prog * rows.length - idx, 0, 1);
          /* keepActive: the closing note is tracked into view but the active
             state is never scrolled above the top of the reading window */
          const end = keepActive ? Math.min(over, Math.max(base, aTop)) : over;
          shift = base + (end - base) * sub;
        } else {
          shift = base;
        }
      }
      move.style.transform = Math.abs(shift) > .5 ? `translate3d(0,${(-shift).toFixed(1)}px,0)` : 'none';
    };
  }

  /* ---------------- generic pinned state driver ---------------- */
  function stateDriver(sectionSel, itemSel, onIndex, mode) {
    const sec = $(sectionSel);
    if (!sec) return;
    const items = Array.from(sec.querySelectorAll(itemSel));
    const n = items.length || 1;
    let last = -1;
    /* deterministic first paint: state 01 is active before the first scroll tick */
    items.forEach((it, i) => it.classList.toggle('is-on', i === 0));
    if (onIndex) onIndex(0, 0);
    ScrollTrigger.create({
      trigger: sec, start: 'top top', end: 'bottom bottom', scrub: .3,
      onUpdate: self => {
        const idx = clamp(Math.floor(self.progress * n * 1.02), 0, n - 1);
        if (idx !== last) {
          last = idx;
          items.forEach((it, i) => it.classList.toggle('is-on', mode === 'cumulative' ? i <= idx : i === idx));
          if (onIndex) onIndex(idx, self.progress);
        } else if (onIndex) onIndex(idx, self.progress);
      }
    });
  }

  /* ---------------- 02 structural system ---------------- */
  {
    const groups = $$('.cx-struct .cx-gr');
    const track = copyTracker($('.cx-struct'), '.cx-el', '.cx-el-d');
    stateDriver('.cx-struct', '.cx-el', (idx, p) => {
      groups.forEach(g => g.classList.toggle('is-on', +g.dataset.el === idx));
      if (track) track(idx, p);
    });
  }

  /* ---------------- 03 seismic analysis ---------------- */
  {
    const sec = $('.cx-seis');
    if (sec) {
      const parts = Array.from(sec.querySelectorAll('[data-sq]'));
      const shape = sec.querySelector('#cxDefShape');
      const frames = Array.from(sec.querySelectorAll('.cx-defframe'));
      const track = copyTracker(sec, '.cx-state', null);
      stateDriver('.cx-seis', '.cx-state', (idx, p) => {
        parts.forEach(el => el.style.opacity = +el.dataset.sq <= idx ? 1 : 0.08);
        if (track) track(idx, p);
        const sq0 = sec.querySelector('.cx-sq0-label');
        if (sq0) sq0.style.opacity = idx >= 2 ? 0 : 1;
        const d = seg(p, .32, .82);
        frames.forEach((f, i) => {
          const k = (i + 1) / frames.length;
          f.setAttribute('transform', `translate(${(d * 44 * k * k).toFixed(2)} 0)`);
        });
        if (shape) shape.style.opacity = d > .04 ? 1 : 0;
      });
    }
  }

  /* ---------------- 04 ground cutaway (depth readout) ---------------- */
  {
    const out = $('[data-testid="cx-depth-readout"]');
    const cut = $('.cx-cut');
    const strata = $$('.cx-stratum');
    if (out && cut && strata.length) {
      /* one source: a level takes over when its section rule reaches the readout line */
      const pick = () => {
        const gauge = out.getBoundingClientRect();
        const line = gauge.top + gauge.height / 2;
        let best = -1;
        strata.forEach((s, i) => {
          if (s.getBoundingClientRect().top <= line) best = i;
        });
        if (best < 0) return;
        const lvl = strata[best].dataset.level;
        if (out.textContent !== lvl) out.textContent = lvl;
      };
      ScrollTrigger.create({ trigger: cut, start: 'top bottom', end: 'bottom top', onUpdate: pick, onRefresh: pick });
    }
  }

  /* ---------------- 05 concrete process (horizontal) ---------------- */
  function verticalSteps(sec, rail, items, onIndex) {
    /* small screens: the same one-state-at-a-time reading, driven by the row
       that has reached the reading line (no horizontal translation) */
    let last = -1;
    if (rail) rail.style.transform = 'none';
    const st = ScrollTrigger.create({
      trigger: sec, start: 'top bottom', end: 'bottom top',
      onUpdate: self => {
        const line = innerHeight * .55;
        let idx = 0;
        items.forEach((it, i) => { if (it.getBoundingClientRect().top <= line) idx = i; });
        if (idx !== last) {
          last = idx;
          items.forEach((it, i) => it.classList.toggle('is-on', i === idx));
          if (onIndex) onIndex(idx, self.progress);
        } else if (onIndex) onIndex(idx, self.progress);
      }
    });
    items.forEach((it, i) => it.classList.toggle('is-on', i === 0));
    if (onIndex) onIndex(0, 0);
    return () => { st.kill(); items.forEach(it => it.classList.remove('is-on')); };
  }

  function horizontal(secSel, railSel, itemSel, onIndex, shortH, stepped) {
    const sec = $(secSel), rail = $(railSel);
    if (!sec || !rail) return;
    const items = Array.from(rail.querySelectorAll(itemSel));
    const mm = gsap.matchMedia();
    /* shortH: viewports too low to hold the approved copy in a 100vh stage read
       the same sequence vertically instead of clipping it */
    const vq = shortH ? `(max-width: 1200px), (max-height: ${shortH}px)` : '(max-width: 1200px)';
    const hq = shortH ? `(min-width: 1201px) and (min-height: ${shortH + 1}px)` : '(min-width: 1201px)';
    mm.add(vq, () => verticalSteps(sec, rail, items, onIndex));
    mm.add(hq, () => horizontalScrub(sec, rail, items, onIndex, stepped));
  }
  function horizontalScrub(sec, rail, items, onIndex, stepped) {
    let last = -1, cached = 0, stops = [];
    const measure = () => {
      cached = Math.max(0, rail.scrollWidth - innerWidth + 40);
      /* stepped: position is the single source of truth — each state has a
         translation that puts its own column fully inside the track, so a column
         can never become active while it is still off screen */
      const max = Math.max(0, rail.scrollWidth - innerWidth);
      const pad = items.length ? items[0].offsetLeft : 0;
      stops = items.map(it => clamp(it.offsetLeft - pad, 0, max));
    };
    const apply = (p) => {
      let idx, tx;
      if (stepped) {
        const n = items.length;
        const t = clamp(p, 0, 1) * n;
        const cur = clamp(Math.floor(t), 0, n - 1);
        const u = clamp(t - cur, 0, 1);
        const e = clamp((u - .7) / .3, 0, 1);
        const s = e * e * (3 - 2 * e);
        const next = stops[Math.min(cur + 1, n - 1)];
        tx = stops[cur] + (next - stops[cur]) * s;
        /* the state index comes from the sequence itself and the rail rests at
           that state's own stop, so every state is reachable and the active
           column is at its reading position for the whole dwell */
        idx = cur;
      } else {
        idx = clamp(Math.round(p * (items.length - 1)), 0, items.length - 1);
        tx = cached * p;
      }
      rail.style.transform = `translate3d(${-tx.toFixed(1)}px,0,0)`;
      if (idx !== last) {
        last = idx;
        items.forEach((it, i) => it.classList.toggle('is-on', i === idx));
      }
      if (onIndex) onIndex(idx, p);
    };
    measure();
    const st = ScrollTrigger.create({
      trigger: sec, start: 'top top', end: 'bottom bottom', scrub: .35,
      onRefresh: self => { measure(); apply(self.progress || 0); },
      onUpdate: self => apply(self.progress)
    });
    /* deterministic first paint: state 01 is active before the first scroll tick */
    apply(0);
    return () => { st.kill(); rail.style.transform = 'none'; items.forEach(it => it.classList.remove('is-on')); };
  }
  {
    /* the material band reads as the same process: the overlay phase follows the
       one canonical stage index of the rail */
    const phases = $$('.cx-conc .cx-phase');
    const cards = $$('.cx-conc .cx-stepcard').length || 1;
    horizontal('.cx-conc', '[data-testid="cx-concrete-rail"]', '.cx-stepcard', idx => {
      if (!phases.length) return;
      const k = clamp(Math.floor(idx * phases.length / cards), 0, phases.length - 1);
      phases.forEach((e, i) => e.classList.toggle('is-on', i === k));
    });
  }

  /* ---------------- 05 reinforcement cage (WebGL assembly) ----------------
     Conceptual reinforced-concrete column reinforcement cage, built from the
     horizontal section outwards: rectangular column boundary and cover zone,
     symmetric perimeter longitudinal reinforcement, a closed perimeter hoop
     with inward 135-degree seismic hooks at every transverse level, single-leg
     cross-ties restraining the intermediate longitudinal bars, visibly denser
     transverse reinforcement in the two special confinement regions than in the
     column mid-region, and straight longitudinal continuity into a subordinate
     foundation block. No diameter, quantity, spacing, ratio, cover, anchorage
     or development value is expressed or implied. */
  {
    const sec = $('.cx-cage');
    const canvas = $('#cxCageCanvas');
    const marks = $$('.cx-cage-marks [data-mark]');
    const hasModel = !!(sec && canvas && gl);
    if (hasModel) {
      const w = scene3(canvas);
      const mat = steelMat();
      const conf = new THREE.MeshStandardMaterial({ color: 0x9fbf86, roughness: .42, metalness: .72, emissive: 0x2c3d22, emissiveIntensity: .5 });
      const ribbed = !mobile;

      /* 1 — horizontal section topology (solved before any extrusion)
         column boundary -> cover zone -> closed hoop -> longitudinal bars ->
         cross-tie positions. Every value below is a proportion, not a dimension. */
      const BX = 1.58, BZ = 1.06, L = 5.05, FD = .46;
      const COV = .085;
      const RH = .026, RL = .048, RT = .021;
      const hx = BX / 2 - COV - RH, hz = BZ / 2 - COV - RH;   // hoop centreline
      const ix = hx - RH - RL, iz = hz - RH - RL;             // longitudinal bar centres
      const u = ix / 2;
      const XS = [-ix, -u, 0, u, ix];                         // symmetric perimeter arrangement
      const TIE_X = [-u, 0, u];                               // one tie per intermediate bar, no other internal bars

      /* transverse levels: closely spaced throughout, and closer again in the two
         special confinement regions. The confinement-region length follows the
         TBDY 2018 principle (governed by the larger section dimension and the
         member height) and the mid-region spacing stays proportionally larger;
         no numerical spacing or region length is expressed. */
      const zoneT = Math.max(BX, L / 6);
      const pd = mobile ? .2 : .17;
      const pm = pd * 1.62;
      const y0 = -L / 2 + L * .02, y1 = L / 2 - L * .02;
      const levels = [];
      for (let y = y0; y <= y0 + zoneT + 1e-6; y += pd) levels.push({ y, c: true });
      for (let y = y0 + zoneT + pm; y < y1 - zoneT - 1e-6; y += pm) levels.push({ y, c: false });
      for (let y = y1 - zoneT; y <= y1 + 1e-6; y += pd) levels.push({ y, c: true });

      const cage = new THREE.Group();
      w.scene.add(cage);
      const mains = [], dowels = [], hoops = [], ties = [];

      /* 2 — longitudinal reinforcement (ribbed bars): symmetric perimeter
         arrangement on the two long faces, every intermediate bar tied */
      const BARS = [];
      XS.forEach(x => [-iz, iz].forEach(z => BARS.push([x, z])));
      BARS.forEach(([x, z]) => {
        const b = rebar(L, RL, mat);
        b.position.set(x, 0, z);
        b.userData.home = b.position.clone();
        cage.add(b); mains.push(b);
        /* 5 — continuity into the foundation: straight continuation only, the
           anchorage configuration itself is project specific */
        const d = rebar(FD * .62, RL, mat);
        d.position.set(x, -L / 2 - FD * .34, z);
        d.visible = false;
        cage.add(d); dowels.push(d);
      });

      /* 3 + 4 — closed hoops and cross-ties at every level */
      levels.forEach((lv, i) => {
        const corner = [[1, 1], [-1, 1], [-1, -1], [1, -1]][i % 4];
        const h = perimeterHoop(hx, hz, RH, mat, corner, ribbed);
        h.position.y = lv.y;
        h.userData.home = lv.y;
        h.userData.conf = lv.c;
        cage.add(h); hoops.push(h);
        TIE_X.forEach((x, k) => {
          const t = crossTie(iz, RL, RT, mat, (i + k) % 2 ? 1 : -1, false);
          t.position.set(x, lv.y, 0);
          t.userData.conf = lv.c;
          cage.add(t); ties.push(t);
        });
      });

      /* subordinate foundation block */
      const fndMat = new THREE.MeshStandardMaterial({ color: 0xb8b3ab, roughness: .95, metalness: .02, transparent: true, opacity: 0 });
      const fndGeo = new THREE.BoxGeometry(BX * 1.55, FD, BZ * 1.9);
      const fnd = new THREE.Mesh(fndGeo, fndMat);
      fnd.position.y = -L / 2 - FD / 2;
      cage.add(fnd);
      const fndEdges = new THREE.LineSegments(
        new THREE.EdgesGeometry(fndGeo),
        new THREE.LineBasicMaterial({ color: 0xa08a63, transparent: true, opacity: 0 })
      );
      fndEdges.position.copy(fnd.position);
      cage.add(fndEdges);

      /* 6 — concrete column boundary / cover zone */
      const concreteMat = new THREE.MeshStandardMaterial({ color: 0xb8b3ab, roughness: .92, metalness: .02, transparent: true, opacity: 0 });
      const coverBox = new THREE.BoxGeometry(BX, L * 1.02, BZ);
      const concrete = new THREE.Mesh(coverBox, concreteMat);
      cage.add(concrete);
      const edges = new THREE.LineSegments(
        new THREE.EdgesGeometry(coverBox),
        new THREE.LineBasicMaterial({ color: 0xa08a63, transparent: true, opacity: 0 })
      );
      cage.add(edges);

      w.cam.position.set(3.5, 1.7, 11.9);
      w.cam.lookAt(0, -.1, 0);
      let need = true;
      const draw = () => { if (need) { w.renderer.render(w.scene, w.cam); need = false; } requestAnimationFrame(draw); };
      requestAnimationFrame(draw);
      /* the six reveal windows use the same boundaries as the canonical state
         driver of the written content, so visual and text state never diverge */
      const B = i => i / (6 * 1.02);
      if (marks[0]) marks[0].classList.add('is-on');
      let matState = -1;
      const cageUpdate = p => {
        cage.rotation.y = THREE.MathUtils.degToRad(22 + p * 44);
        cage.rotation.x = -.05;
        /* 01 — longitudinal reinforcement moves into its section position */
        mains.forEach((b, i) => {
          const enter = seg(p, .002 + i * .005, .04 + i * .005);
          const h = b.userData.home;
          const out = 1 + (1 - enter) * .55;
          b.position.set(h.x * out, h.y, h.z * out);
        });
        /* 02 — closed transverse reinforcement, bottom to top */
        const hn = hoops.length;
        hoops.forEach((s, i) => {
          const t = i / hn;
          const a = seg(p, B(1) + t * .1, B(1) + .06 + t * .1);
          s.visible = a > .02;
          s.position.y = s.userData.home + (1 - a) * .42;
        });
        /* 03 — cross-ties */
        const tn = ties.length;
        ties.forEach((t, i) => {
          const a = seg(p, B(2) + (i / tn) * .1, B(2) + .06 + (i / tn) * .1);
          t.visible = a > .02;
          t.scale.set(1, 1, .35 + a * .65);
        });
        /* 04 — the two special confinement regions are highlighted against the
           mid-region while that state is active; the spacing itself keeps
           communicating the differentiation afterwards */
        const st = p >= B(3) ? 1 : 0;
        if (st !== matState) {
          matState = st;
          hoops.forEach(s => setMat(s, st && s.userData.conf ? conf : mat));
          ties.forEach(t => setMat(t, st && t.userData.conf ? conf : mat));
        }
        /* 05 — foundation continuity */
        const f = seg(p, B(4), B(4) + .1);
        dowels.forEach(d => { d.visible = f > .02; d.scale.setScalar(1); });
        fndMat.opacity = f * .26;
        fndEdges.material.opacity = f * .7;
        fnd.visible = fndEdges.visible = f > .01;
        /* 06 — concrete cover boundary */
        const c = seg(p, B(5), B(5) + .11);
        concreteMat.opacity = c * .16;
        edges.material.opacity = c * .85;
        concrete.visible = c > .01;
        w.cam.position.set(3.5 - p * .4, 1.7 - p * .55, 11.9 + p * 1.4);
        w.cam.lookAt(0, -.1 - p * .22, 0);
        need = true;
      };
      cageUpdate(0);
      /* validation hook: 4 mandatory views (top / front / side / perspective) */
      window.cxCageView = (v, p) => {
        cageUpdate(typeof p === 'number' ? p : 1);
        cage.rotation.set(0, 0, 0);
        const d = 11.9;
        if (v === 'top') w.cam.position.set(0, d, .0001);
        else if (v === 'front') w.cam.position.set(0, 0, d);
        else if (v === 'side') w.cam.position.set(d, 0, 0);
        else { cage.rotation.y = THREE.MathUtils.degToRad(34); cage.rotation.x = -.12; w.cam.position.set(2.6, 1.6, 8.2); }
        w.cam.lookAt(0, 0, 0);
        need = true;
      };
      ScrollTrigger.create({
        trigger: sec, start: 'top top', end: 'bottom bottom', scrub: .5,
        onUpdate: self => cageUpdate(self.progress)
      });
    } else if (marks.length) {
      marks.forEach(m => m.classList.add('is-on'));
    }
    const cagetrack = copyTracker(sec, '.cx-prin', '.cx-prin-d', true);
    stateDriver('.cx-cage', '.cx-prin', (idx, p) => {
      if (cagetrack) cagetrack(idx, p);
      /* one canonical index drives the copy, the annotation and the model */
      if (hasModel) marks.forEach(m => m.classList.toggle('is-on', +m.dataset.mark === idx + 1));
    });
  }

  /* ---------------- 07 execution control (horizontal inspection) ---------------- */
  {
    const sec = $('.cx-insp');
    if (sec) {
      const states = Array.from(sec.querySelectorAll('.cx-insp-state'));
      const stages = Array.from(sec.querySelectorAll('[data-elstate]'));
      const bar = sec.querySelector('.cx-insp-bar');
      const alignBar = () => {
        const svg = sec.querySelector('.cx-insp-elem--d svg');
        if (!bar || !svg || !svg.getClientRects().length) return;
        const r = svg.getBoundingClientRect(), vb = svg.viewBox.baseVal;
        const drawW = Math.min(r.width, r.height * (vb.width / vb.height));
        const scale = drawW / vb.width;
        const left = (r.width - drawW) / 2 + r.left + 20 * scale;
        const right = innerWidth - (r.left + (r.width + drawW) / 2 - 20 * scale);
        bar.style.paddingLeft = Math.max(0, Math.round(left)) + 'px';
        bar.style.paddingRight = Math.max(0, Math.round(right)) + 'px';
      };
      ScrollTrigger.addEventListener('refresh', alignBar);
      addEventListener('load', alignBar);
      setTimeout(alignBar, 400);
      /* the element build-up, its label and the active column all come from the
         same rail driver, so nothing can drift out of sync */
      /* the six verification points map one-to-one onto C.01..C.06 */
      const map = [0, 1, 2, 3, 4, 5];
      horizontal('.cx-insp', '[data-testid="cx-inspection-rail"]', '.cx-insp-col', (idx) => {
        const k = clamp(map[idx] === undefined ? idx : map[idx], 0, states.length - 1);
        states.forEach((s, i) => s.classList.toggle('is-on', i === k));
        stages.forEach(s => { s.style.opacity = +s.dataset.elstate <= k ? 1 : .08; });
      }, 820, true);
    }
  }

  /* ---------------- 08 waterproofing continuity trace ---------------- */
  {
    const sec = $('.cx-wp');
    const trace = $('#cxTrace');
    const gap = $('#cxTraceGap');
    const flag = $('.cx-wp-flag');
    if (sec && trace) {
      trace.style.strokeDasharray = 1;
      const track = copyTracker(sec, '.cx-wp-node', '.cx-wp-node-d', true);
      stateDriver('.cx-wp', '.cx-wp-node', (idx, p) => {
        if (track) track(idx, p);
        trace.style.strokeDashoffset = (1 - clamp(p * 1.08, 0, 1)).toFixed(4);
        const broken = p > .24 && p < .36;      // unresolved termination, then resolved
        trace.classList.toggle('is-broken', broken);
        if (gap) gap.style.opacity = broken ? 1 : 0;
        if (flag) flag.classList.toggle('is-on', broken);
      });
    }
  }

  /* ---------------- 12 final: drawing aligns, then becomes architecture ---------------- */
  {
    const fin = $('.cx-final');
    if (fin) {
      const layers = Array.from(fin.querySelectorAll('.cx-fl'));
      const photo = fin.querySelector('.cx-final-photo');
      const dwgs = Array.from(fin.querySelectorAll('.cx-final-dwg'));
      ScrollTrigger.create({
        trigger: fin, start: 'top top', end: 'bottom bottom', scrub: .45,
        onUpdate: self => {
          const p = self.progress;
          const align = seg(p, .06, .58);
          layers.forEach((l, i) => {
            const vb = l.ownerSVGElement && l.ownerSVGElement.viewBox.baseVal.width || 1100;
            const off = (i - (layers.length - 1) / 2) * (vb < 700 ? vb * .045 : vb * .09) * (1 - align);
            l.setAttribute('transform', `translate(${off.toFixed(1)} ${(off * .22).toFixed(1)})`);
            l.style.opacity = (0.25 + align * .75).toFixed(3);
          });
          const dis = seg(p, .62, .93);
          if (photo) photo.style.opacity = dis.toFixed(3);
          dwgs.forEach(d => { d.style.opacity = (1 - dis * .96).toFixed(3); });
        }
      });
    }
  }

  /* drawing annotations are sized from the measured viewBox scale so technical
     type never grows larger than the body copy on wide-but-short containers */
  const DWG = '.cx-cage .cx-dwg, .cx-insp .cx-dwg, .cx-wp .cx-dwg, .cx-det-fig .cx-dwg, .cx-plot .cx-dwg, .cx-mep-viz .cx-dwg, .cx-final-dwg .cx-dwg';
  const fitDwgType = () => {
    const target = innerWidth < 700 ? 10.5 : innerWidth < 1201 ? 10 : 9.5;
    $$(DWG).forEach(svg => {
      const vb = svg.viewBox && svg.viewBox.baseVal;
      const r = svg.getBoundingClientRect();
      if (!vb || !vb.width || !r.width) return;
      const drawW = Math.min(r.width, r.height * (vb.width / vb.height));
      const scale = drawW / vb.width;
      if (scale > 0) svg.style.setProperty('--dwgfs', (target / scale).toFixed(2) + 'px');
    });
  };
  fitDwgType();
  addEventListener('load', fitDwgType);
  let dwgT;
  addEventListener('resize', () => { clearTimeout(dwgT); dwgT = setTimeout(fitDwgType, 140); }, { passive: true });
  ScrollTrigger.addEventListener('refresh', fitDwgType);
  setTimeout(fitDwgType, 500);

  /* the approved copy is long: re-measure once fonts, images and layout settle */
  ScrollTrigger.refresh();
  addEventListener('load', () => ScrollTrigger.refresh());
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => ScrollTrigger.refresh());

  /* a resize that crosses a matchMedia breakpoint rebuilds the pinned sections and
     changes the document height: keep the reader where they were */
  let anchor = null;
  addEventListener('resize', () => {
    const secs = $$('.page-cx > section');
    for (const s of secs) {
      const r = s.getBoundingClientRect();
      if (r.top <= 4 && r.bottom > 4) { anchor = { el: s, frac: -r.top / Math.max(1, s.offsetHeight) }; return; }
    }
    anchor = null;
  }, { passive: true });
  ScrollTrigger.addEventListener('refresh', () => {
    if (!anchor) return;
    const a = anchor; anchor = null;
    const top = a.el.getBoundingClientRect().top + scrollY;
    scrollTo(0, Math.round(top + a.frac * a.el.offsetHeight));
  });
}
