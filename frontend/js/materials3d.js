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
    {
      slug: 'walnut', depth: 1,
      props: {
        roughness: 1, metalness: 0, clearcoat: 0.07, clearcoatRoughness: 0.62,
        nScale: 0.45, envMapIntensity: 0.3
      }
    },
    {
      slug: 'stone', depth: 1.35,
      props: {
        roughness: 1, metalness: 0, clearcoat: 0.34, clearcoatRoughness: 0.14,
        nScale: 0.35, envMapIntensity: 0.9
      }
    },
    {
      slug: 'bronze', depth: 0.8,
      props: {
        roughness: 1, metalness: 1, clearcoat: 0, nScale: 0.55, envMapIntensity: 0.75
      }
    },
    {
      slug: 'leather', depth: 0.92,
      props: {
        roughness: 1, metalness: 0, clearcoat: 0.04, clearcoatRoughness: 0.9,
        nScale: 0.7, envMapIntensity: 0.28, sheen: 0.35, sheenRoughness: 0.85, sheenColor: 0x9c7250
      }
    },
    {
      slug: null, depth: 1.7,
      props: {
        roughness: 0.02, metalness: 0, transmission: 1, thickness: 0.5, ior: 1.52,
        color: 0xffffff, attenuationColor: 0x8d938e, attenuationDistance: 1.4,
        specularIntensity: 1, clearcoat: 0, envMapIntensity: 1.15
      }
    }
  ];

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.86;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(30, 1, 0.1, 100);
  camera.position.set(0, 0, 4.1);

  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.02).texture;
  scene.environmentIntensity = 1;

  const key = new THREE.DirectionalLight(0xffe9d2, 0.85);
  key.position.set(2.2, 2.6, 2.4);
  const fill = new THREE.DirectionalLight(0xdde3ea, 0.3);
  fill.position.set(-2.4, 0.8, -1.6);
  const rim = new THREE.DirectionalLight(0xfff4e6, 0.45);
  rim.position.set(-1.4, 1.6, -3.2);
  scene.add(key, fill, rim, new THREE.AmbientLight(0xffffff, 0.03));

  const loader = new THREE.TextureLoader();
  const anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
  const sets = defs.map(() => null);
  const loadSet = (i) => {
    if (sets[i] || !defs[i].slug) return sets[i];
    const slug = defs[i].slug;
    const tex = (file, srgb) => {
      const t = loader.load(base + file);
      t.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace;
      t.anisotropy = anisotropy;
      /* the plate is wider than it is tall — the square scan is cropped rather
         than stretched, except the bookmatched slab whose seam must stay centred */
      if (slug !== 'stone') {
        t.repeat.set(1, 0.63);
        t.offset.set(0, 0.185);
      }
      return t;
    };
    sets[i] = {
      map: tex(`tex-${slug}.webp`, true),
      normalMap: tex(`tex-${slug}-n.webp`, false),
      roughnessMap: tex(`tex-${slug}-r.webp`, false)
    };
    return sets[i];
  };

  /* a backdrop the colour of the page, so transmitted light through the glass
     sample reads correctly instead of resolving to black */
  const backdrop = new THREE.Mesh(
    new THREE.PlaneGeometry(24, 16),
    new THREE.MeshBasicMaterial({ color: 0xf1ebe3, toneMapped: false })
  );
  backdrop.position.z = -6;
  scene.add(backdrop);

  const material = new THREE.MeshPhysicalMaterial({ color: 0xffffff });
  const mesh = new THREE.Mesh(new RoundedBoxGeometry(1.9, 1.2, 0.15, 4, 0.025), material);
  mesh.rotation.set(-0.2, -0.42, 0.02);
  scene.add(mesh);

  /* a backing card, seen only through the glass sample, so the body tint,
     transmission and refraction are readable */
  const cardTex = (() => {
    const c = document.createElement('canvas');
    c.width = c.height = 256;
    const x = c.getContext('2d');
    const g = x.createLinearGradient(0, 0, 256, 256);
    g.addColorStop(0, '#FBF7F1'); g.addColorStop(0.55, '#EFE8DE'); g.addColorStop(1, '#D8CEC1');
    x.fillStyle = g; x.fillRect(0, 0, 256, 256);
    x.strokeStyle = 'rgba(51,41,31,.42)'; x.lineWidth = 2;
    x.beginPath(); x.moveTo(0, 98); x.lineTo(256, 86); x.moveTo(0, 174); x.lineTo(256, 188); x.stroke();
    const t = new THREE.CanvasTexture(c);
    t.colorSpace = THREE.SRGBColorSpace;
    return t;
  })();
  const card = new THREE.Mesh(
    new THREE.PlaneGeometry(1.66, 1.02),
    new THREE.MeshBasicMaterial({ map: cardTex, toneMapped: false })
  );
  card.position.z = -0.4;
  card.visible = false;
  mesh.add(card);

  const applyMaterial = (i) => {
    const d = defs[i];
    const set = loadSet(i);
    card.visible = !d.slug;
    material.setValues({
      map: set ? set.map : null,
      normalMap: set ? set.normalMap : null,
      roughnessMap: set ? set.roughnessMap : null,
      bumpMap: null, bumpScale: 0,
      color: 0xffffff, transmission: 0, thickness: 0, clearcoat: 0, clearcoatRoughness: 0,
      sheen: 0, metalness: 0, roughness: 1, ior: 1.5, attenuationDistance: Infinity,
      envMapIntensity: 1, specularIntensity: 1,
      transparent: !!d.props.transmission,
      ...d.props
    });
    material.normalScale.set(d.props.nScale || 1, d.props.nScale || 1);
    mesh.scale.z = d.depth;
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
