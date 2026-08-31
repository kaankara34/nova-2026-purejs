/* ==========================================================
   Material register — one lit sample plate, five surfaces.
   Three.js physical materials, drag to turn, scroll-linked
   selection. Runs only while the section is on screen.
   ========================================================== */
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

const canvas = document.getElementById('dzMatCanvas');
if (canvas) start();

function start() {
  const gsap = window.gsap;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const stage = canvas.closest('.dz-reg-stage');
  const items = Array.from(document.querySelectorAll('[data-mat-item]'));
  const tabs = Array.from(document.querySelectorAll('[data-mat]'));
  const base = './media/images/design/';

  const defs = [
    { map: 'tex-walnut.webp', bump: 0.055, props: { roughness: 0.44, metalness: 0, clearcoat: 0.22, clearcoatRoughness: 0.38 } },
    { map: 'tex-stone.webp', bump: 0.02, props: { roughness: 0.2, metalness: 0, clearcoat: 0.4, clearcoatRoughness: 0.16 } },
    { map: 'tex-bronze.webp', bump: 0.035, props: { roughness: 0.33, metalness: 0.92, clearcoat: 0.1 } },
    { map: 'tex-leather.webp', bump: 0.08, props: { roughness: 0.72, metalness: 0, sheen: 0.4, sheenRoughness: 0.6 } },
    { map: null, props: { roughness: 0.06, metalness: 0, transmission: 0.9, thickness: 0.55, ior: 1.5, color: 0x63615b } }
  ];

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.06;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(30, 1, 0.1, 100);
  camera.position.set(0, 0, 4.1);

  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

  const key = new THREE.DirectionalLight(0xffe3c2, 1.7);
  key.position.set(2.2, 2.6, 2.4);
  const fill = new THREE.DirectionalLight(0xdde3ea, 0.5);
  fill.position.set(-2.4, 0.8, -1.6);
  scene.add(key, fill, new THREE.AmbientLight(0xffffff, 0.16));

  const loader = new THREE.TextureLoader();
  const maps = defs.map(d => {
    if (!d.map) return null;
    const t = loader.load(base + d.map);
    t.colorSpace = THREE.SRGBColorSpace;
    t.anisotropy = 4;
    return t;
  });

  const material = new THREE.MeshPhysicalMaterial({ color: 0xffffff });
  const mesh = new THREE.Mesh(new RoundedBoxGeometry(1.9, 1.2, 0.15, 4, 0.025), material);
  mesh.rotation.set(-0.2, -0.42, 0.02);
  scene.add(mesh);

  const applyMaterial = (i) => {
    const d = defs[i];
    material.setValues({
      map: maps[i] || null,
      bumpMap: maps[i] || null,
      bumpScale: d.bump || 0,
      color: 0xffffff, transmission: 0, thickness: 0, clearcoat: 0,
      sheen: 0, metalness: 0, transparent: !!d.props.transmission,
      ...d.props
    });
    material.needsUpdate = true;
  };
  applyMaterial(0);

  /* ---------- selection ---------- */
  const counter = document.querySelector('[data-mat-count]');
  const nameOut = document.querySelector('[data-mat-name]');
  const prev = document.querySelector('[data-mat-prev]');
  const next = document.querySelector('[data-mat-next]');
  let active = 0;
  const setActive = (i) => {
    if (i === active) return;
    active = i;
    tabs.forEach((t, n) => t.classList.toggle('is-on', n === i));
    tabs.forEach((t, n) => t.setAttribute('aria-selected', n === i ? 'true' : 'false'));
    items.forEach((el, n) => el.classList.toggle('is-on', n === i));
    if (counter) counter.textContent = '0' + (i + 1);
    if (nameOut) nameOut.textContent = items[i].querySelector('.dz-reg-name').textContent;
    if (prev) prev.disabled = i === 0;
    if (next) next.disabled = i === items.length - 1;
    if (gsap && !reduce) {
      gsap.to(mesh.rotation, { y: mesh.rotation.y + Math.PI, duration: 1.05, ease: 'power2.inOut' });
      gsap.to(mesh.scale, { x: 0.94, y: 0.94, z: 0.94, duration: 0.5, ease: 'power2.out', yoyo: true, repeat: 1 });
      gsap.delayedCall(0.5, () => applyMaterial(i));
    } else {
      applyMaterial(i);
    }
  };
  tabs.forEach((tab, i) => {
    tab.addEventListener('click', () => {
      setActive(i);
      const head = document.querySelector('.site-header');
      const bar = document.querySelector('.utility-bar');
      const off = (head ? head.offsetHeight : 110) + (bar ? bar.offsetHeight : 0) + 24;
      const y = items[i].getBoundingClientRect().top + scrollY - off;
      scrollTo({ top: y, behavior: reduce ? 'auto' : 'smooth' });
    });
  });
  if (prev) prev.addEventListener('click', () => setActive(Math.max(0, active - 1)));
  if (next) next.addEventListener('click', () => setActive(Math.min(items.length - 1, active + 1)));
  if (prev) prev.disabled = true;
  const spy = new IntersectionObserver((entries) => {
    if (innerWidth <= 1100) return;
    entries.forEach(e => { if (e.isIntersecting) setActive(items.indexOf(e.target)); });
  }, { rootMargin: '-45% 0px -45% 0px' });
  items.forEach(el => spy.observe(el));

  /* ---------- drag to turn ---------- */
  const badge = document.querySelector('[data-mat-badge]');
  let dragging = false, px = 0, py = 0, vx = 0, vy = 0;
  const start2 = (e) => {
    dragging = true; px = e.clientX; py = e.clientY;
    canvas.classList.add('is-drag');
    if (badge) badge.classList.add('is-done');
  };
  const move = (e) => {
    if (!dragging) return;
    vy += (e.clientX - px) * 0.006;
    vx += (e.clientY - py) * 0.004;
    px = e.clientX; py = e.clientY;
  };
  const end = () => { dragging = false; canvas.classList.remove('is-drag'); };
  canvas.addEventListener('pointerdown', start2);
  addEventListener('pointermove', move, { passive: true });
  addEventListener('pointerup', end);
  addEventListener('pointercancel', end);

  /* ---------- the sample follows the reading column ---------- */
  const grid = document.querySelector('.dz-reg-grid');
  const headerOffset = () => {
    const head = document.querySelector('.site-header');
    const bar = document.querySelector('.utility-bar');
    return (head ? head.offsetHeight : 110) + (bar ? bar.offsetHeight : 0) + (innerWidth > 1100 ? 40 : 14);
  };
  const follow = () => {
    if (!grid) return;
    /* only on wide screens: on a phone a floating sample would cross the copy */
    if (innerWidth <= 1100) { stage.style.transform = ''; return; }
    const g = grid.getBoundingClientRect();
    const room = g.height - stage.offsetHeight;
    if (room <= 0) { stage.style.transform = ''; return; }
    const t = Math.max(0, Math.min(headerOffset() - g.top, room));
    stage.style.transform = 'translateY(' + t.toFixed(1) + 'px)';
  };
  addEventListener('scroll', follow, { passive: true });
  addEventListener('resize', follow);
  follow();

  /* ---------- size + loop ---------- */
  const resize = () => {
    const r = canvas.getBoundingClientRect();
    if (!r.width) return;
    renderer.setSize(r.width, r.height, false);
    camera.aspect = r.width / r.height;
    camera.updateProjectionMatrix();
  };
  resize();
  addEventListener('resize', resize);

  let visible = false;
  new IntersectionObserver(([e]) => {
    visible = e.isIntersecting;
    if (visible) { resize(); tick(); }
  }, { rootMargin: '200px' }).observe(stage);

  let raf = 0;
  function tick() {
    if (!visible) { raf = 0; return; }
    mesh.rotation.y += vy + (dragging || reduce ? 0 : 0.0012);
    mesh.rotation.x = Math.max(-0.6, Math.min(0.6, mesh.rotation.x + vx));
    vx *= 0.9; vy *= 0.9;
    renderer.render(scene, camera);
    raf = requestAnimationFrame(tick);
  }
  if (!raf) tick();
}
