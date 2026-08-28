/* global gsap, ScrollTrigger, THREE */
/* ==========================================================
   LEED / Sustainability — scroll-directed architectural film
   Three.js (procedural architecture) + GSAP ScrollTrigger
   ========================================================== */
import * as THREE from 'three';

/* GSAP and ScrollTrigger are loaded from the CDN in the page head */
const { gsap, ScrollTrigger } = window;

const body = document.body;
const film = document.getElementById('lxFilm');
const stage = document.getElementById('lxStage');
const canvas = document.getElementById('lxCanvas');
const skyEl = document.getElementById('lxSky');
const leadersSvg = document.getElementById('lxLeaders');
const labelsWrap = document.getElementById('lxLabels');
const siteplan = document.getElementById('lxSiteplan');
const railFill = document.getElementById('lxRailFill');
const railItems = Array.from(document.querySelectorAll('.lx-rail-item'));

const clamp = (v, a, b) => v < a ? a : (v > b ? b : v);
const smooth = t => t * t * (3 - 2 * t);
const lerp = (a, b, t) => a + (b - a) * t;

/* ---------- keyframe helpers ---------- */
function keyed(arr, p) {
  if (p <= arr[0][0]) return arr[0][1];
  for (let i = 1; i < arr.length; i++) {
    if (p <= arr[i][0]) {
      const [p0, v0] = arr[i - 1], [p1, v1] = arr[i];
      return lerp(v0, v1, smooth((p - p0) / (p1 - p0)));
    }
  }
  return arr[arr.length - 1][1];
}

/* =========================================================
   Scroll-driven opacity for every [data-lx] element
   ========================================================= */
const fades = Array.from(document.querySelectorAll('[data-lx]')).map(el => {
  const v = el.dataset.lx.trim().split(/[\s,]+/).map(Number);
  return { el, a: v[0], b: v[1], c: v[2], d: v[3], last: -1, hot: el.classList.contains('lx-hot') };
});

function applyFades(p) {
  for (const f of fades) {
    let a = 0;
    if (p > f.a && p < f.d) {
      if (p < f.b) a = (p - f.a) / (f.b - f.a);
      else if (p <= f.c) a = 1;
      else a = 1 - (p - f.c) / (f.d - f.c);
    }
    a = smooth(clamp(a, 0, 1));
    if (Math.abs(a - f.last) < 0.004) continue;
    f.last = a;
    const el = f.el;
    if (a <= 0.002) {
      el.style.opacity = '0';
      el.style.visibility = 'hidden';
    } else {
      el.style.visibility = 'visible';
      el.style.opacity = a.toFixed(3);
      const dir = p < f.c ? 1 : -1;
      el.style.transform = a > 0.995 ? 'none' : `translate3d(0,${((1 - a) * 13 * dir).toFixed(2)}px,0)`;
    }
  }
}

/* =========================================================
   Always-on interactions (film + static fallback)
   ========================================================= */
function initInteractions() {
  /* material hotspots — click/tap to inspect */
  const hots = Array.from(document.querySelectorAll('.lx-hot'));
  hots.forEach(h => {
    h.addEventListener('click', () => {
      const open = h.classList.contains('is-open');
      hots.forEach(o => { o.classList.remove('is-open'); o.setAttribute('aria-expanded', 'false'); });
      if (!open) { h.classList.add('is-open'); h.setAttribute('aria-expanded', 'true'); }
    });
  });

  /* LEED impact areas */
  const items = Array.from(document.querySelectorAll('.lx-leed-item'));
  const copies = Array.from(document.querySelectorAll('[data-leed-copy]'));
  const setLeed = key => {
    items.forEach(i => i.classList.toggle('is-active', i.dataset.leed === key));
    copies.forEach(c => c.classList.toggle('is-active', c.dataset.leedCopy === key));
  };
  items.forEach(i => {
    i.addEventListener('mouseenter', () => setLeed(i.dataset.leed));
    i.addEventListener('focus', () => setLeed(i.dataset.leed));
    i.addEventListener('click', () => setLeed(i.dataset.leed));
  });

  /* dust motes in the interior chapter */
  const motes = document.getElementById('lxMotes');
  if (motes && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const n = window.matchMedia('(max-width: 760px)').matches ? 8 : 16;
    for (let i = 0; i < n; i++) {
      const s = document.createElement('i');
      s.style.left = (8 + Math.random() * 84) + '%';
      s.style.top = (30 + Math.random() * 62) + '%';
      s.style.animationDuration = (11 + Math.random() * 12).toFixed(1) + 's';
      s.style.animationDelay = (-Math.random() * 16).toFixed(1) + 's';
      s.style.opacity = (0.35 + Math.random() * 0.5).toFixed(2);
      motes.appendChild(s);
    }
  }
}

/* =========================================================
   Capability gate
   ========================================================= */
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
function webglOK() {
  try {
    const c = document.createElement('canvas');
    return !!(window.WebGLRenderingContext && (c.getContext('webgl2') || c.getContext('webgl')));
  } catch (e) { return false; }
}

initInteractions();

if (reduceMotion || !webglOK() || !window.gsap || !window.ScrollTrigger) {
  body.classList.add('lx-static');
  const ch2 = document.querySelector('.lx-ch2');
  if (ch2 && labelsWrap) ch2.appendChild(labelsWrap);
  if (siteplan) {
    siteplan.style.opacity = '1';
    siteplan.style.visibility = 'visible';
    siteplan.querySelectorAll('[pathLength]').forEach(p => p.style.strokeDashoffset = '0');
  }
} else {
  initFilm();
}

/* =========================================================
   THE FILM
   ========================================================= */
function initFilm() {
  gsap.registerPlugin(ScrollTrigger);

  const isMobile = window.matchMedia('(max-width: 900px)').matches;

  /* ---------------------------------------------------------------
     Scroll-time warp — the narrative timeline is not linear with the
     scrollbar. Reading passages get 2-3x the physical scroll distance
     of the purely cinematic transitions, so each statement holds still
     long enough to be read: movement -> pause -> information.
     [narrative start, narrative end, scroll weight]
  --------------------------------------------------------------- */
  const SEG = [
    [0.00, 0.10, 1.2],  // 01 approach (hold on the hero)
    [0.10, 0.13, 1.6],  //    -> systems
    [0.13, 0.27, 3.6],  // 02 systems — 7 annotations + 5 statements (reading)
    [0.27, 0.30, 1.6],  //    -> dusk
    [0.30, 0.39, 3.4],  // 03 decarbonization (reading)
    [0.39, 0.42, 1.6],
    [0.42, 0.51, 3.2],  // 04 water (reading)
    [0.51, 0.54, 1.6],
    [0.54, 0.63, 3.2],  // 05 material — inspection points (reading + interaction)
    [0.63, 0.66, 1.6],
    [0.66, 0.75, 3.4],  // 06 quality of life (reading)
    [0.75, 0.79, 1.6],  //    -> site plan
    [0.79, 0.86, 2.6],  // 07 ecology (reading + plan draw)
    [0.86, 0.89, 1.6],
    [0.89, 0.95, 2.8],  // 08 LEED framework (reading)
    [0.95, 0.97, 2.0],
    [0.97, 1.00, 3.5]   // 09 final statement (long hold)
  ];
  const WARP = [];
  {
    let acc = 0;
    SEG.forEach(([a, b, w]) => { const len = (b - a) * w; WARP.push({ r0: acc, r1: acc + len, p0: a, p1: b }); acc += len; });
    WARP.forEach(w => { w.r0 /= acc; w.r1 /= acc; });
  }
  function warp(r) {
    if (r <= 0) return 0;
    for (const w of WARP) if (r <= w.r1) return w.p0 + (w.p1 - w.p0) * ((r - w.r0) / (w.r1 - w.r0));
    return 1;
  }
  function unwarp(p) {
    if (p <= 0) return 0;
    for (const w of WARP) if (p <= w.p1) return w.r0 + (w.r1 - w.r0) * ((p - w.p0) / (w.p1 - w.p0));
    return 1;
  }
  const LOW = isMobile || (navigator.hardwareConcurrency || 4) <= 4;

  /* ---------- renderer ---------- */
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: !LOW, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, LOW ? 1.5 : 2));
  renderer.setSize(stage.clientWidth, stage.clientHeight, false);
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  renderer.shadowMap.enabled = !LOW;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  const scene = new THREE.Scene();
  const DAY_SKY = new THREE.Color(0xb9c3c6);
  const NIGHT_SKY = new THREE.Color(0x0b1219);
  const GRAPHITE = new THREE.Color(0x1e2226);
  scene.background = DAY_SKY.clone();
  scene.fog = new THREE.FogExp2(DAY_SKY.getHex(), 0.0055);

  const camera = new THREE.PerspectiveCamera(38, stage.clientWidth / stage.clientHeight, 0.1, 600);
  camera.position.set(16, 10, 34);

  /* ---------- lights ---------- */
  const hemi = new THREE.HemisphereLight(0xcfe0e6, 0x5f584c, 1.0);
  scene.add(hemi);
  const sun = new THREE.DirectionalLight(0xfff2dd, 3.0);
  sun.position.set(26, 34, 20);
  if (!LOW) {
    sun.castShadow = true;
    sun.shadow.mapSize.set(1024, 1024);
    const s = sun.shadow.camera;
    s.left = -32; s.right = 32; s.top = 40; s.bottom = -12; s.near = 1; s.far = 140;
    sun.shadow.bias = -0.0009;
  }
  scene.add(sun);
  const fill = new THREE.DirectionalLight(0x9fb6c4, 0.35);
  fill.position.set(-22, 12, -18);
  scene.add(fill);

  /* ---------- dimensions ---------- */
  const FLOORS = LOW ? 9 : 13;
  const FH = 2.0, W = 10, D = 8;
  const H = FLOORS * FH;

  const M = {
    concrete: new THREE.MeshStandardMaterial({ color: 0x9a958d, roughness: 0.88, metalness: 0.02 }),
    slab: new THREE.MeshStandardMaterial({ color: 0xb4aea4, roughness: 0.8, metalness: 0.02 }),
    glass: new THREE.MeshPhysicalMaterial({
      color: 0x8fa8b2, roughness: 0.06, metalness: 0.0, transparent: true, opacity: 0.3,
      clearcoat: 1, clearcoatRoughness: 0.05, side: THREE.DoubleSide
    }),
    mullion: new THREE.MeshStandardMaterial({ color: 0x33383b, roughness: 0.35, metalness: 0.85 }),
    insul: new THREE.MeshStandardMaterial({ color: 0xd9d0bd, roughness: 0.96, metalness: 0, transparent: true, opacity: 0.6 }),
    metal: new THREE.MeshStandardMaterial({ color: 0x74797c, roughness: 0.45, metalness: 0.8 }),
    ground: new THREE.MeshStandardMaterial({ color: 0x24272a, roughness: 0.95, metalness: 0 }),
    podium: new THREE.MeshStandardMaterial({ color: 0x817d75, roughness: 0.9, metalness: 0 }),
    plant: new THREE.MeshStandardMaterial({ color: 0x3d4b3f, roughness: 0.9, metalness: 0 }),
    trunk: new THREE.MeshStandardMaterial({ color: 0x4a443c, roughness: 0.9 }),
    water: new THREE.MeshPhysicalMaterial({ color: 0x7f9fab, roughness: 0.08, transparent: true, opacity: 0.34, metalness: 0 })
  };

  const box = (w, h, d, mat, x, y, z, cast) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
    m.position.set(x, y, z);
    if (!LOW && cast !== false) { m.castShadow = true; m.receiveShadow = true; }
    return m;
  };

  /* ---------- ground ---------- */
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), M.ground);
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -0.42;
  if (!LOW) ground.receiveShadow = true;
  scene.add(ground);

  /* ---------- building ---------- */
  const building = new THREE.Group();
  scene.add(building);

  const SYS = {};
  const mkSys = (key, dir, dist, anchor) => {
    const g = new THREE.Group();
    building.add(g);
    SYS[key] = { g, dir: new THREE.Vector3(...dir).normalize(), dist, anchor: new THREE.Vector3(...anchor) };
    return g;
  };

  /* structure — the datum, stays in place */
  const gStruct = mkSys('structure', [0, 0, 0], 0, [1.9, H * 0.82, 1.2]);
  gStruct.add(box(3.4, H, 2.6, M.concrete, 0, H / 2, 0));
  for (let i = 1; i <= FLOORS; i++) gStruct.add(box(W + 0.5, 0.18, D + 0.5, M.slab, 0, i * FH, 0));
  gStruct.add(box(W + 1.2, 0.3, D + 1.2, M.slab, 0, 0.05, 0));
  [[-(W / 2 - 0.6), -(D / 2 - 0.6)], [(W / 2 - 0.6), -(D / 2 - 0.6)], [-(W / 2 - 0.6), (D / 2 - 0.6)], [(W / 2 - 0.6), (D / 2 - 0.6)], [0, -(D / 2 - 0.6)], [0, (D / 2 - 0.6)]]
    .forEach(([x, z]) => gStruct.add(box(0.42, H, 0.42, M.concrete, x, H / 2, z)));

  /* envelope / insulation */
  const gEnv = mkSys('envelope', [1.0, 0.08, -1.0], 5.2, [4.4, H * 0.42, -3.4]);
  gEnv.add(box(W - 0.7, H - 0.6, 0.14, M.insul, 0, H / 2, -(D / 2 - 0.3), false));
  gEnv.add(box(W - 0.7, H - 0.6, 0.14, M.insul, 0, H / 2, (D / 2 - 0.3), false));
  gEnv.add(box(0.14, H - 0.6, D - 0.7, M.insul, -(W / 2 - 0.3), H / 2, 0, false));
  gEnv.add(box(0.14, H - 0.6, D - 0.7, M.insul, (W / 2 - 0.3), H / 2, 0, false));

  /* glazing — mullion grid (single instanced draw call) */
  const gGlaze = mkSys('glazing', [-1.0, 0.06, 0.85], 5.4, [-5.2, H * 0.6, 1.4]);
  {
    const bays = 8;
    const items = [];
    [-1, 1].forEach(sz => {
      for (let i = 0; i <= bays; i++) {
        const x = -W / 2 + (W / bays) * i;
        items.push([x, H / 2, sz * (D / 2 + 0.06), 0.07, H, 0.07]);
      }
      for (let i = 0; i <= FLOORS; i++) items.push([0, i * FH, sz * (D / 2 + 0.06), W, 0.07, 0.07]);
    });
    [-1, 1].forEach(sx => {
      for (let i = 1; i <= 5; i++) {
        const z = -D / 2 + (D / 6) * i;
        items.push([sx * (W / 2 + 0.06), H / 2, z, 0.07, H, 0.07]);
      }
    });
    const inst = new THREE.InstancedMesh(new THREE.BoxGeometry(1, 1, 1), M.mullion, items.length);
    const mtx = new THREE.Matrix4();
    items.forEach((it, i) => {
      mtx.makeScale(it[3], it[4], it[5]);
      mtx.setPosition(it[0], it[1], it[2]);
      inst.setMatrixAt(i, mtx);
    });
    inst.instanceMatrix.needsUpdate = true;
    gGlaze.add(inst);
  }

  /* façade — glass skin + horizontal shading */
  const gFacade = mkSys('facade', [1.0, 0.12, 0.9], 6.6, [5.4, H * 0.72, 3.4]);
  gFacade.add(box(W, H - 0.2, 0.07, M.glass, 0, H / 2, D / 2, false));
  gFacade.add(box(W, H - 0.2, 0.07, M.glass, 0, H / 2, -D / 2, false));
  gFacade.add(box(0.07, H - 0.2, D, M.glass, W / 2, H / 2, 0, false));
  gFacade.add(box(0.07, H - 0.2, D, M.glass, -W / 2, H / 2, 0, false));
  for (let i = 1; i <= FLOORS; i++) {
    gFacade.add(box(W + 0.9, 0.08, 0.62, M.slab, 0, i * FH + 0.16, D / 2 + 0.24));
    gFacade.add(box(W + 0.9, 0.08, 0.62, M.slab, 0, i * FH + 0.16, -(D / 2 + 0.24)));
  }

  /* mechanical */
  const gMech = mkSys('mech', [0.05, 1.0, -0.75], 4.5, [0.4, H + 1.3, -2.2]);
  gMech.add(box(3.2, 1.5, 2.2, M.metal, -1.6, H + 1.05, -1.2));
  gMech.add(box(2.2, 1.1, 1.8, M.metal, 2.2, H + 0.85, 1.0));
  gMech.add(box(1.4, 0.9, 1.4, M.metal, 2.6, H + 0.75, -2.0));
  gMech.add(box(0.75, H, 0.75, M.metal, 1.4, H / 2, -0.9, false));
  gMech.add(box(0.75, H, 0.75, M.metal, -1.4, H / 2, 0.9, false));

  /* water systems */
  const gWater = mkSys('water', [-0.95, 0.7, -0.6], 6.2, [-2.6, H + 1.1, -1.4]);
  {
    const tank = new THREE.CylinderGeometry(0.62, 0.62, 1.5, 18);
    const t1 = new THREE.Mesh(tank, M.water); t1.position.set(-2.6, H + 1.05, -2.2);
    const t2 = new THREE.Mesh(tank, M.water); t2.position.set(-2.6, H + 1.05, -0.4);
    gWater.add(t1, t2);
    const riser = new THREE.CylinderGeometry(0.13, 0.13, H, 10);
    const r1 = new THREE.Mesh(riser, M.metal); r1.position.set(-2.6, H / 2, -1.3);
    gWater.add(r1);
  }

  /* landscape */
  const gLand = mkSys('landscape', [0.15, -0.85, 1.0], 4.6, [7.6, 0.9, 6.2]);
  gLand.add(box(26, 0.5, 22, M.podium, 0, -0.2, 2, false));
  const plantSpots = [[-9, 7], [-6.5, -6], [8.5, 6.5], [10, -5], [-11, 0], [11, 1.5], [0, 9.5], [-3, -8], [4, 10], [6, -8]];
  const nTrees = LOW ? 5 : plantSpots.length;
  for (let i = 0; i < nTrees; i++) {
    const [x, z] = plantSpots[i];
    gLand.add(box(3.6, 0.24, 3.6, M.plant, x, 0.13, z + 2, false));
    const cy = new THREE.Mesh(new THREE.ConeGeometry(0.6, 3.4, 7), M.plant);
    cy.position.set(x, 1.95, z + 2);
    cy.rotation.y = Math.random() * 1.5;
    if (!LOW) cy.castShadow = true;
    const hedge = box(2.6, 0.5, 0.7, M.plant, x, 0.42, z + 3.2, false);
    gLand.add(cy, hedge);
  }

  /* ---------- night window light ---------- */
  const winMat = new THREE.MeshBasicMaterial({ color: 0xffdca8, transparent: true, opacity: 0 });
  let windows;
  {
    const cols = 7, per = FLOORS * cols * 2;
    windows = new THREE.InstancedMesh(new THREE.PlaneGeometry(0.82, 0.72), winMat, per);
    const mtx = new THREE.Matrix4(), col = new THREE.Color();
    let k = 0;
    for (let s = 0; s < 2; s++) {
      const sz = s === 0 ? 1 : -1;
      for (let f = 1; f <= FLOORS; f++) {
        for (let c = 0; c < cols; c++) {
          const x = -W / 2 + (W / (cols + 1)) * (c + 1);
          mtx.makeRotationY(sz === 1 ? 0 : Math.PI);
          mtx.setPosition(x, f * FH - 0.72, sz * (D / 2 + 0.02));
          windows.setMatrixAt(k, mtx);
          const on = Math.random();
          col.setRGB(1, 0.86, 0.66).multiplyScalar(on > 0.45 ? 0.55 + Math.random() * 0.65 : 0.06);
          windows.setColorAt(k, col);
          k++;
        }
      }
    }
    windows.instanceMatrix.needsUpdate = true;
    if (windows.instanceColor) windows.instanceColor.needsUpdate = true;
    gFacade.add(windows);
  }

  /* ---------- flow shaders (energy / water) ---------- */
  function flowMat(hex, speed, rep, width) {
    return new THREE.ShaderMaterial({
      uniforms: {
        uTime: { value: 0 }, uI: { value: 0 },
        uColor: { value: new THREE.Color(hex) },
        uSpeed: { value: speed }, uRep: { value: rep }, uWidth: { value: width }
      },
      vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
      fragmentShader: `
        uniform float uTime, uI, uSpeed, uRep, uWidth;
        uniform vec3 uColor;
        varying vec2 vUv;
        void main(){
          float f = fract(vUv.x * uRep - uTime * uSpeed);
          float head = smoothstep(0.0, uWidth * 0.35, f) * (1.0 - smoothstep(uWidth * 0.35, uWidth * 2.6, f));
          float a = (0.045 + head * 0.95) * uI;
          if (a < 0.004) discard;
          gl_FragColor = vec4(uColor * (0.3 + head * 1.1), a);
        }`,
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending
    });
  }

  const V = (x, y, z) => new THREE.Vector3(x, y, z);
  const tube = (pts, mat, r) => {
    const c = new THREE.CatmullRomCurve3(pts);
    return new THREE.Mesh(new THREE.TubeGeometry(c, LOW ? 34 : 64, r, LOW ? 5 : 7, false), mat);
  };

  const energyMat = flowMat(0xffd9a0, 0.34, 2.2, 0.2);
  const gEnergy = new THREE.Group();
  building.add(gEnergy);
  gEnergy.add(tube([V(-1.4, H + 1.4, 0.9), V(-1.4, H * 0.78, 0.9), V(-1.4, H * 0.45, 0.9), V(-1.4, H * 0.16, 0.9), V(-1.4, 0.6, 0.9)], energyMat, 0.055));
  gEnergy.add(tube([V(1.4, H + 1.4, -0.9), V(1.4, H * 0.72, -0.9), V(1.4, H * 0.38, -0.9), V(1.4, 0.6, -0.9)], energyMat, 0.055));
  gEnergy.add(tube([V(1.4, H * 0.66, -0.9), V(2.6, H * 0.66 + 0.1, 0.4), V(3.6, H * 0.66, 2.2), V(W / 2 - 0.5, H * 0.66, 3.2)], energyMat, 0.045));
  gEnergy.add(tube([V(-1.4, H * 0.32, 0.9), V(-2.8, H * 0.32 + 0.1, 0.2), V(-3.8, H * 0.32, -1.8), V(-(W / 2 - 0.5), H * 0.32, -3.0)], energyMat, 0.045));
  if (!LOW) gEnergy.add(tube([V(-1.4, H * 0.52, 0.9), V(0.4, H * 0.52, 2.6), V(2.4, H * 0.52, 3.4)], energyMat, 0.04));

  const waterMat = flowMat(0x9fd0e6, 0.2, 1.7, 0.3);
  const gFlowWater = new THREE.Group();
  building.add(gFlowWater);
  gFlowWater.add(tube([V(-2.6, H + 1.1, -1.3), V(-2.6, H * 0.6, -1.3), V(-2.6, 1.6, -1.3), V(-5.0, 0.35, 1.4), V(-8.6, 0.28, 4.6), V(-11.5, 0.25, 6.4)], waterMat, 0.07));
  gFlowWater.add(tube([V(2.4, H + 0.42, -3.2), V(2.4, H + 0.36, 1.2), V(3.6, H + 0.3, 3.4), V(5.4, 1.2, 5.2), V(8.4, 0.3, 7.4)], waterMat, 0.06));
  gFlowWater.add(tube([V(-11.5, 0.25, 6.4), V(-6, 0.22, 9.2), V(1, 0.2, 10.4), V(8.4, 0.3, 7.4)], waterMat, 0.05));

  /* =========================================================
     Keyframed direction
     ========================================================= */
  const SC = H / 26;
  const CAM = [
    { p: 0.000, pos: [22, 17, 54], tgt: [0, 13, 0] },
    { p: 0.100, pos: [16, 13, 38], tgt: [0, 13.5, 0] },
    { p: 0.190, pos: [-10, 23, 55], tgt: [0, 14.5, 0] },
    { p: 0.265, pos: [-36, 26, 49], tgt: [0, 15, 0] },
    { p: 0.390, pos: [-21, 13, 42], tgt: [0, 12, 0] },
    { p: 0.470, pos: [9, 40, 31], tgt: [0, 9, 1] },
    { p: 0.520, pos: [13, 22, 24], tgt: [1, 12, 0] },
    { p: 0.610, pos: [9, 15, 15], tgt: [0, 12, 0] },
    { p: 0.700, pos: [5, 11, 10], tgt: [0, 11, 0] },
    { p: 0.780, pos: [0.8, 62, 24], tgt: [0, 0, 2] },
    { p: 0.860, pos: [2, 44, 34], tgt: [0, 2, 2] },
    { p: 0.920, pos: [-20, 17, 44], tgt: [0, 13, 0] },
    { p: 1.000, pos: [22, 17, 54], tgt: [0, 13, 0] }
  ].map(k => ({ p: k.p, pos: [k.pos[0] * SC, k.pos[1] * SC, k.pos[2] * SC], tgt: [k.tgt[0], k.tgt[1] * SC, k.tgt[2]] }));
  const camPos = new THREE.Vector3(), camTgt = new THREE.Vector3();
  function camAt(p) {
    let i = 1;
    while (i < CAM.length - 1 && p > CAM[i].p) i++;
    const A = CAM[i - 1], B = CAM[i];
    const t = smooth(clamp((p - A.p) / (B.p - A.p), 0, 1));
    camPos.set(lerp(A.pos[0], B.pos[0], t), lerp(A.pos[1], B.pos[1], t), lerp(A.pos[2], B.pos[2], t));
    camTgt.set(lerp(A.tgt[0], B.tgt[0], t), lerp(A.tgt[1], B.tgt[1], t), lerp(A.tgt[2], B.tgt[2], t));
  }

  const K = {
    explode: [[0, 0], [0.105, 0], [0.26, 1], [0.288, 1], [0.345, 0.12], [0.50, 0.12], [0.60, 0.24], [0.78, 0.2], [0.90, 0.62], [0.985, 0], [1, 0]],
    night: [[0, 0], [0.255, 0], [0.40, 1], [0.435, 0.96], [0.50, 0.55], [0.575, 0.5], [0.66, 0.12], [0.755, 0.25], [0.80, 0.35], [0.90, 0.45], [1, 0.28]],
    energy: [[0, 0], [0.285, 0], [0.335, 1], [0.375, 1], [0.425, 0], [1, 0]],
    water: [[0, 0], [0.425, 0], [0.462, 1], [0.50, 1], [0.545, 0], [1, 0]],
    /* the environment darkens to a graphite studio as the technical
       information appears, so off-white typography always has contrast */
    studio: [[0, 0], [0.108, 0], [0.152, 1], [1, 1]],
    yaw: [[0, -0.44], [0.26, -0.06], [0.5, 0.26], [0.78, 0.62], [1, 0.96]],
    siteplanDraw: [[0.770, 0], [0.816, 1]],
    siteplanAlpha: [[0.768, 0], [0.786, 1], [0.822, 1], [0.848, 0]]
  };

  /* =========================================================
     Leader lines + system legend
     ========================================================= */
  const labels = Array.from(document.querySelectorAll('.lx-label')).map((el, i) => ({
    el, key: el.dataset.sys, i,
    a: 0.126 + i * 0.0145, b: 0.126 + i * 0.0145 + 0.005, c: 0.244, d: 0.262,
    slot: 0.155 + i * 0.107,
    line1: null, line2: null, dot: null, last: -1
  }));
  const NS = 'http://www.w3.org/2000/svg';
  labels.forEach(L => {
    L.line1 = document.createElementNS(NS, 'line');
    L.line2 = document.createElementNS(NS, 'line');
    L.dot = document.createElementNS(NS, 'circle');
    L.dot.setAttribute('r', '2');
    leadersSvg.append(L.line1, L.line2, L.dot);
  });

  const proj = new THREE.Vector3();
  let sw = stage.clientWidth, sh = stage.clientHeight;

  function updateLabels(p) {
    const labX = sw * 0.755;
    const seg = clamp((p - 0.126) / (0.248 - 0.126), 0, 1);
    const focus = Math.min(labels.length - 1, Math.floor(seg * labels.length));
    for (const L of labels) {
      let a = 0;
      if (p > L.a && p < L.d) {
        if (p < L.b) a = (p - L.a) / (L.b - L.a);
        else if (p <= L.c) a = 1;
        else a = 1 - (p - L.c) / (L.d - L.c);
      }
      a = smooth(clamp(a, 0, 1));
      const vis = a > 0.004;
      if (Math.abs(a - L.last) > 0.004) {
        L.last = a;
        L.el.style.opacity = a.toFixed(3);
        L.el.style.visibility = vis ? 'visible' : 'hidden';
      }
      const isFocus = L.i === focus;
      L.el.classList.toggle('is-focus', isFocus && vis);
      if (isMobile) { L.line1.style.opacity = '0'; L.line2.style.opacity = '0'; L.dot.style.opacity = '0'; continue; }
      if (!vis || !isFocus) {
        L.line1.style.opacity = '0'; L.line2.style.opacity = '0'; L.dot.style.opacity = '0';
        continue;
      }
      const labY = sh * L.slot;
      L.el.style.transform = `translate3d(${labX.toFixed(1)}px,${labY.toFixed(1)}px,0)`;

      const sys = SYS[L.key];
      proj.copy(sys.anchor);
      sys.g.localToWorld(proj);
      proj.project(camera);
      const behind = proj.z > 1;
      const ax = (proj.x * 0.5 + 0.5) * sw;
      const ay = (-proj.y * 0.5 + 0.5) * sh;
      const inView = !behind && ax > -200 && ax < sw + 200 && ay > -200 && ay < sh + 200;
      const o = inView ? (a * 0.8).toFixed(3) : '0';
      const elbowX = Math.min(ax + 26, labX - 26);
      L.line1.setAttribute('x1', ax.toFixed(1)); L.line1.setAttribute('y1', ay.toFixed(1));
      L.line1.setAttribute('x2', elbowX.toFixed(1)); L.line1.setAttribute('y2', ay.toFixed(1));
      L.line2.setAttribute('x1', elbowX.toFixed(1)); L.line2.setAttribute('y1', ay.toFixed(1));
      L.line2.setAttribute('x2', (labX - 3).toFixed(1)); L.line2.setAttribute('y2', (labY + 9).toFixed(1));
      L.dot.setAttribute('cx', ax.toFixed(1)); L.dot.setAttribute('cy', ay.toFixed(1));
      L.line1.style.opacity = o; L.line2.style.opacity = o; L.dot.style.opacity = o;
    }
    /* non-focused labels still need their column position */
    if (!isMobile) {
      for (const L of labels) {
        if (L.i === focus) continue;
        L.el.style.transform = `translate3d(${labX.toFixed(1)}px,${(sh * L.slot).toFixed(1)}px,0)`;
      }
    }
  }

  /* ---------- site plan draw ---------- */
  const spPaths = Array.from(siteplan.querySelectorAll('[pathLength]'));
  let lastDraw = -1, lastSpA = -1;
  function updateSiteplan(p) {
    const a = keyed(K.siteplanAlpha, p);
    if (Math.abs(a - lastSpA) > 0.004) {
      lastSpA = a;
      siteplan.style.opacity = a.toFixed(3);
      siteplan.style.visibility = a > 0.004 ? 'visible' : 'hidden';
    }
    if (a <= 0.004) return;
    const d = keyed(K.siteplanDraw, p);
    if (Math.abs(d - lastDraw) < 0.004) return;
    lastDraw = d;
    const off = (1 - d).toFixed(4);
    for (let i = 0; i < spPaths.length; i++) spPaths[i].style.strokeDashoffset = off;
  }

  /* =========================================================
     Scene update
     ========================================================= */
  const tmp = new THREE.Vector3();
  const skyCol = new THREE.Color();
  let flowActive = false;

  function updateScene(p, t) {
    camAt(p);
    /* portrait viewports need more distance to hold the full composition */
    const k = clamp(1.05 / camera.aspect, 1, 1.9);
    if (k > 1.001) camPos.sub(camTgt).multiplyScalar(k).add(camTgt);
    camera.position.copy(camPos);
    camera.lookAt(camTgt);

    building.rotation.y = keyed(K.yaw, p);

    const ex = keyed(K.explode, p);
    for (const k in SYS) {
      const s = SYS[k];
      tmp.copy(s.dir).multiplyScalar(s.dist * ex);
      s.g.position.copy(tmp);
    }

    const st = keyed(K.studio, p);
    const n = keyed(K.night, p);
    skyCol.copy(DAY_SKY).lerp(GRAPHITE, st).lerp(NIGHT_SKY, n);
    scene.background.copy(skyCol);
    scene.fog.color.copy(skyCol);
    scene.fog.density = lerp(lerp(0.0055, 0.0072, st), 0.0085, n);

    sun.intensity = lerp(3.0, 0.16, n) * (1 + 0.28 * st * (1 - n));
    sun.color.setRGB(lerp(1, 0.42, n), lerp(0.95, 0.5, n), lerp(0.87, 0.72, n));
    sun.position.set(lerp(26, -20, n), lerp(34, 16, n), lerp(20, -22, n));
    hemi.intensity = lerp(1.0, 0.14, n) * (1 - 0.38 * st);
    hemi.color.setRGB(lerp(0.81, 0.09, n), lerp(0.88, 0.13, n), lerp(0.9, 0.2, n));
    fill.intensity = lerp(0.35, 0.24, n);
    renderer.toneMappingExposure = lerp(1.05, 0.92, n) * (1 - 0.06 * st);
    winMat.opacity = Math.pow(n, 1.4) * 0.95;

    const e = keyed(K.energy, p);
    const w = keyed(K.water, p);
    energyMat.uniforms.uI.value = e;
    energyMat.uniforms.uTime.value = t;
    waterMat.uniforms.uI.value = w;
    waterMat.uniforms.uTime.value = t;
    gEnergy.visible = e > 0.01;
    gFlowWater.visible = w > 0.01;
    flowActive = e > 0.01 || w > 0.01;

    building.updateMatrixWorld();
  }

  /* =========================================================
     Scroll wiring
     ========================================================= */
  let target = 0, cur = 0, raw = 0, time = 0, first = true;
  ScrollTrigger.create({
    trigger: film,
    start: 'top top',
    end: 'bottom bottom',
    onUpdate: self => { raw = self.progress; target = warp(raw); }
  });

  /* pre-scroll nudge — only if the visitor has not moved yet */
  const cueEl = document.getElementById('lxCue');
  if (cueEl) {
    const nudge = setTimeout(() => { if ((window.scrollY || 0) < 14) cueEl.classList.add('is-nudge'); }, 2600);
    const clear = () => { clearTimeout(nudge); cueEl.classList.remove('is-nudge'); };
    window.addEventListener('scroll', clear, { once: true, passive: true });
    window.addEventListener('wheel', clear, { once: true, passive: true });
    window.addEventListener('touchstart', clear, { once: true, passive: true });
  }

  /* the first inspection point demonstrates itself when the chapter opens */
  const firstHot = document.querySelector('[data-testid="leed-hotspot-durability"]');
  let demoed = false;
  function maybeDemoHotspot(p) {
    if (demoed || !firstHot) return;
    if (p < 0.568 || p > 0.606) return;
    demoed = true;
    if (!document.querySelector('.lx-hot.is-open')) {
      firstHot.classList.add('is-open');
      firstHot.setAttribute('aria-expanded', 'true');
    }
  }

  /* rail */
  const railEl = document.getElementById('lxRail');
  const moFill = document.getElementById('lxMobarFill');
  const moChap = document.getElementById('lxMoChap');
  const moN = moChap ? moChap.querySelector('.lx-mochap-n') : null;
  const moT = moChap ? moChap.querySelector('.lx-mochap-t') : null;
  const RAIL_AT = [0.02, 0.19, 0.34, 0.46, 0.58, 0.70, 0.81, 0.91, 0.985];
  let lastRail = -1;
  function updateRail(p) {
    const rp = unwarp(p);
    railFill.style.height = (rp * 100).toFixed(2) + '%';
    if (moFill) moFill.style.width = (rp * 100).toFixed(2) + '%';
    let idx = 0;
    for (let i = 0; i < RAIL_AT.length; i++) if (p >= RAIL_AT[i] - 0.055) idx = i;
    if (idx !== lastRail) {
      lastRail = idx;
      railItems.forEach((b, i) => b.classList.toggle('is-active', i === idx));
      if (moN && moT) {
        moN.textContent = String(idx + 1).padStart(2, '0');
        moT.textContent = railItems[idx].querySelector('.lx-rail-t').textContent;
      }
    }
  }
  ScrollTrigger.create({
    trigger: '.lx-closing', start: 'top 88%', end: 'bottom top',
    onToggle: self => {
      railEl.classList.toggle('is-off', self.isActive);
      if (moChap) moChap.classList.toggle('is-off', self.isActive);
    }
  });
  railItems.forEach(b => b.addEventListener('click', () => {
    const goal = parseFloat(b.dataset.goto);
    const top = film.offsetTop + unwarp(goal) * (film.offsetHeight - window.innerHeight);
    window.scrollTo({ top, behavior: 'smooth' });
  }));

  /* =========================================================
     Loop — only while the stage is on screen
     ========================================================= */
  let raf = 0, running = false, prevT = performance.now();

  function tick(now) {
    raf = requestAnimationFrame(tick);
    const dt = Math.min(0.3, (now - prevT) / 1000);
    prevT = now;

    const before = cur;
    cur += (target - cur) * (1 - Math.exp(-dt * 9));
    if (Math.abs(target - cur) < 0.00006) cur = target;
    const moved = Math.abs(cur - before) > 0.000012;

    if (moved || first) {
      applyFades(cur);
      updateSiteplan(cur);
      updateRail(cur);
      maybeDemoHotspot(cur);
    }
    if (moved || first || flowActive) {
      time += dt;
      updateScene(cur, time);
      updateLabels(cur);
      renderer.render(scene, camera);
      first = false;
    }
  }

  function start() { if (!running) { running = true; prevT = performance.now(); raf = requestAnimationFrame(tick); } }
  function stop() { if (running) { running = false; cancelAnimationFrame(raf); } }

  new IntersectionObserver(entries => {
    entries[0].isIntersecting ? start() : stop();
  }, { rootMargin: '10% 0px' }).observe(stage);

  document.addEventListener('visibilitychange', () => { document.hidden ? stop() : start(); });

  /* ---------- resize ---------- */
  let rt = 0;
  function resize() {
    sw = stage.clientWidth; sh = stage.clientHeight;
    camera.aspect = sw / sh;
    camera.updateProjectionMatrix();
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, LOW ? 1.5 : 2));
    renderer.setSize(sw, sh, false);
    leadersSvg.setAttribute('viewBox', `0 0 ${sw} ${sh}`);
    labels.forEach(L => L.last = -1);
    first = true;
  }
  window.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(resize, 140); });
  resize();

  skyEl.style.background = '#b9c3c6';
  start();
  ScrollTrigger.refresh();
}
