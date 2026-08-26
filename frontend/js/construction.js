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
mepTabs.forEach((t, i) => t.addEventListener('click', () => {
  mepTabs.forEach((o, j) => o.classList.toggle('is-on', j === i));
  mepLayers.forEach((l, j) => l.classList.toggle('is-on', j === i));
}));
if (mepTabs[0]) { mepTabs[0].classList.add('is-on'); if (mepLayers[0]) mepLayers[0].classList.add('is-on'); }

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
    if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
  }), { rootMargin: '0px 0px -10% 0px', threshold: .1 });
  $$('[data-cx-in], .cx-plot').forEach(el => io.observe(el));

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
  function stirrup(w, h, r, mat) {
    const cr = Math.min(w, h) * .18, n = 5, pts = [];
    const corners = [
      [w / 2 - cr, h / 2 - cr, 0],
      [-(w / 2 - cr), h / 2 - cr, Math.PI / 2],
      [-(w / 2 - cr), -(h / 2 - cr), Math.PI],
      [w / 2 - cr, -(h / 2 - cr), -Math.PI / 2]
    ];
    corners.forEach(([cx, cy, a0]) => {
      for (let i = 0; i <= n; i++) {
        const a = a0 + (i / n) * Math.PI / 2;
        pts.push(new THREE.Vector3(cx + Math.cos(a) * cr, cy + Math.sin(a) * cr, 0));
      }
    });
    const curve = new THREE.CatmullRomCurve3(pts, true, 'catmullrom', 0);
    return new THREE.Mesh(new THREE.TubeGeometry(curve, mobile ? 110 : 190, r, mobile ? 6 : 10, true), mat);
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
          bars.forEach((b, i) => {
            b.rotation.y = THREE.MathUtils.degToRad(p * (250 + i * 16));   // slow rotation about own axis
            b.position.y = (i % 2 ? -1 : 1) * p * (.22 + i * .05);          // slight parallax
            b.position.z = -i * .55 + p * .3;
          });
          world.key.position.set(4 - p * 3.4, 6 - p * 2.2, 5 - p * 1.4);
          world.rim.intensity = 1.1 + p * .5;
          world.cam.position.z = 6.2 - p * .8;
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
        const li = p < .3 ? 0 : p < .66 ? 1 : 2;
        if (li !== last && readout) { last = li; readout.textContent = labels[li]; }
      }
    });
  }

  /* ---------------- pinned copy tracking (content-aware) ----------------
     The pinned stages keep their original 100vh composition. When the approved
     copy is taller than the available column, the copy block is tracked to the
     canonical active state instead of being cut off. */
  function copyTracker(sec, itemSel, expandSel) {
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
    return idx => {
      if (!geo || !geo.base[idx]) return;
      const grow = geo.dh[idx] ? geo.dh[idx] + 5 : 0;
      const total = geo.collapsed + grow;
      const over = total - geo.avail;
      win.classList.toggle('is-tracking', over > 0);
      /* fits: keep the original optically centred composition.
         taller than the column: track the canonical active state into view,
         never cutting the active row's top */
      let shift;
      if (over <= 0) {
        shift = -(geo.avail - total) / 2;
      } else {
        const aTop = geo.base[idx].top, aH = geo.base[idx].h + grow;
        const keepTop = Math.max(0, aTop - 14);
        shift = idx === rows.length - 1 ? over : Math.max(0, aTop + aH + 24 - geo.avail);
        shift = clamp(Math.min(shift, keepTop), 0, over);
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
    stateDriver('.cx-struct', '.cx-el', idx => {
      groups.forEach(g => g.classList.toggle('is-on', +g.dataset.el === idx));
      if (track) track(idx);
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
        if (track) track(idx);
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
      /* one source: the panel that owns the reading line owns the readout */
      const pick = () => {
        const line = innerHeight * .38;
        let best = -1;
        strata.forEach((s, i) => {
          const r = s.getBoundingClientRect();
          if (r.top <= line) best = i;              // last panel whose head has passed the line
        });
        if (best < 0) {
          let d0 = Infinity;
          strata.forEach((s, i) => {
            const r = s.getBoundingClientRect();
            if (r.bottom < 0 || r.top > innerHeight) return;
            const d = Math.abs(r.top - line);
            if (d < d0) { d0 = d; best = i; }
          });
        }
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

  function horizontal(secSel, railSel, itemSel, onIndex) {
    const sec = $(secSel), rail = $(railSel);
    if (!sec || !rail) return;
    const items = Array.from(rail.querySelectorAll(itemSel));
    const mm = gsap.matchMedia();
    mm.add('(max-width: 1200px)', () => verticalSteps(sec, rail, items, onIndex));
    mm.add('(min-width: 1201px)', () => horizontalScrub(sec, rail, items, onIndex));
  }
  function horizontalScrub(sec, rail, items, onIndex) {
    let last = -1, cached = 0;
    const measure = () => { cached = Math.max(0, rail.scrollWidth - innerWidth + 40); };
    measure();
    const st = ScrollTrigger.create({
      trigger: sec, start: 'top top', end: 'bottom bottom', scrub: .35,
      onRefresh: measure,
      onUpdate: self => {
        const p = self.progress;
        rail.style.transform = `translate3d(${-(cached * p).toFixed(1)}px,0,0)`;
        const idx = clamp(Math.round(p * (items.length - 1)), 0, items.length - 1);
        if (idx !== last) {
          last = idx;
          items.forEach((it, i) => it.classList.toggle('is-on', i === idx));
        }
        if (onIndex) onIndex(idx, p);
      }
    });
    return () => { st.kill(); rail.style.transform = 'none'; };
  }
  horizontal('.cx-conc', '[data-testid="cx-concrete-rail"]', '.cx-stepcard');

  /* ---------------- 06 reinforcement cage (WebGL assembly) ---------------- */
  {
    const sec = $('.cx-cage');
    const canvas = $('#cxCageCanvas');
    if (sec && canvas && gl) {
      const w = scene3(canvas);
      const mat = steelMat();
      const R = .105, W = 1.24, L = 4.0;
      const cage = new THREE.Group();
      w.scene.add(cage);
      const mains = [];
      [[-1, -1], [1, -1], [1, 1], [-1, 1]].forEach(([sx, sz], i) => {
        const b = rebar(L, R, mat);
        b.position.set(sx * W / 2 * .78, 0, sz * W / 2 * .78);
        b.userData.home = b.position.clone();
        cage.add(b);
        mains.push(b);
      });
      const ties = [];
      const tieN = mobile ? 6 : 10;
      for (let i = 0; i < tieN; i++) {
        const s = stirrup(W * .82, W * .82, R * .44, mat);
        s.rotation.x = Math.PI / 2;
        s.position.y = -L / 2 + L * .09 + (i / (tieN - 1)) * L * .82;
        s.userData.home = s.position.y;
        ties.push(s);
        cage.add(s);
      }
      const concreteMat = new THREE.MeshStandardMaterial({ color: 0xb8b3ab, roughness: .92, metalness: .02, transparent: true, opacity: 0 });
      const concrete = new THREE.Mesh(new THREE.BoxGeometry(W * 1.16, L * 1.02, W * 1.16), concreteMat);
      w.scene.add(concrete);
      const edges = new THREE.LineSegments(
        new THREE.EdgesGeometry(new THREE.BoxGeometry(W * 1.16, L * 1.02, W * 1.16)),
        new THREE.LineBasicMaterial({ color: 0xa08a63, transparent: true, opacity: 0 })
      );
      w.scene.add(edges);
      w.cam.position.set(3.0, 2.4, 7.0);
      w.cam.lookAt(0, 0, 0);
      let need = true;
      const draw = () => { if (need) { w.renderer.render(w.scene, w.cam); need = false; } requestAnimationFrame(draw); };
      requestAnimationFrame(draw);
      ScrollTrigger.create({
        trigger: sec, start: 'top top', end: 'bottom bottom', scrub: .5,
        onUpdate: self => {
          const p = self.progress;
          cage.rotation.y = THREE.MathUtils.degToRad(24 + p * 150);
          cage.rotation.x = -0.05;
          mains.forEach((b, i) => {
            const enter = i === 0 ? 1 : seg(p, .14 + i * .045, .3 + i * .045);
            const h = b.userData.home;
            b.position.set(h.x * enter + (1 - enter) * h.x * 3.4, h.y, h.z * enter + (1 - enter) * h.z * 3.4);
            b.visible = enter > .02;
            b.rotation.y = THREE.MathUtils.degToRad(p * 120);
          });
          ties.forEach((s, i) => {
            const a = seg(p, .34 + (i / ties.length) * .16, .5 + (i / ties.length) * .16);
            s.visible = a > .02;
            s.scale.setScalar(.6 + a * .4);
            s.position.y = s.userData.home + (1 - a) * 1.6;
            s.material.opacity = 1;
          });
          const c = seg(p, .72, .93);
          concreteMat.opacity = c * .24;
          edges.material.opacity = c * .8;
          concrete.visible = c > .01;
          w.cam.position.set(3.0 - p * .5, 2.4 - p * 1.1, 7.0 - p * .5);
          w.cam.lookAt(0, 0, 0);
          need = true;
        }
      });
    }
    const cagetrack = copyTracker(sec, '.cx-prin', 'p');
    stateDriver('.cx-cage', '.cx-prin', idx => { if (cagetrack) cagetrack(idx); });
  }

  /* ---------------- 07 execution control (horizontal inspection) ---------------- */
  {
    const sec = $('.cx-insp');
    if (sec) {
      const states = Array.from(sec.querySelectorAll('.cx-insp-state'));
      const stages = Array.from(sec.querySelectorAll('[data-elstate]'));
      /* the element build-up, its label and the active column all come from the
         same rail driver, so nothing can drift out of sync */
      horizontal('.cx-insp', '[data-testid="cx-inspection-rail"]', '.cx-insp-col', (idx, p) => {
        const k = clamp(Math.floor(p * stages.length * 1.02), 0, stages.length - 1);
        states.forEach((s, i) => s.classList.toggle('is-on', i === k));
        stages.forEach((s, i) => { s.style.opacity = i <= k ? 1 : .08; });
      });
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
      const track = copyTracker(sec, '.cx-wp-node', null);
      stateDriver('.cx-wp', '.cx-wp-node', (idx, p) => {
        if (track) track(idx);
        trace.style.strokeDashoffset = (1 - clamp(p * 1.08, 0, 1)).toFixed(4);
        const broken = p > .58 && p < .70;      // unresolved termination, then resolved
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
      const dwg = fin.querySelector('.cx-final-dwg');
      ScrollTrigger.create({
        trigger: fin, start: 'top top', end: 'bottom bottom', scrub: .45,
        onUpdate: self => {
          const p = self.progress;
          const align = seg(p, .06, .58);
          layers.forEach((l, i) => {
            const off = (i - (layers.length - 1) / 2) * 120 * (1 - align);
            l.setAttribute('transform', `translate(${off.toFixed(1)} ${(off * .22).toFixed(1)})`);
            l.style.opacity = (0.25 + align * .75).toFixed(3);
          });
          const dis = seg(p, .62, .93);
          if (photo) photo.style.opacity = dis.toFixed(3);
          if (dwg) dwg.style.opacity = (1 - dis * .96).toFixed(3);
        }
      });
    }
  }

  ScrollTrigger.refresh();
}
