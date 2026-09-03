/* ==========================================================
   Material register — five materials, five forms.
   Three.js physical materials, drag to turn, scroll-linked
   selection. Runs only while the section is on screen.
   ========================================================== */
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const canvas = document.getElementById('dzMatCanvas');
if (canvas) start();

function start() {
  const gsap = window.gsap;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const stage = canvas.closest('.dz-reg-stage');
  const items = Array.from(document.querySelectorAll('[data-mat-item]'));
  const tabs = Array.from(document.querySelectorAll('[data-mat]'));
  const base = './media/images/design/';

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.92;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(30, 1, 0.1, 100);
  camera.position.set(0, 0, 4.1);

  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.02).texture;
  scene.environmentIntensity = 1;

  /* restrained studio: one key, a cool fill, a warm rim */
  const key = new THREE.DirectionalLight(0xffeeda, 1.15);
  key.position.set(2.4, 2.8, 2.6);
  const fill = new THREE.DirectionalLight(0xdde3ea, 0.34);
  fill.position.set(-2.6, 0.6, -1.4);
  const rim = new THREE.DirectionalLight(0xfff2e2, 0.5);
  rim.position.set(-1.6, 1.8, -3.2);
  scene.add(key, fill, rim, new THREE.AmbientLight(0xffffff, 0.04));

  /* a backdrop the colour of the page, so light transmitted through the glass
     reads correctly instead of resolving to black */
  const backdrop = new THREE.Mesh(
    new THREE.PlaneGeometry(26, 18),
    new THREE.MeshBasicMaterial({ color: 0xf1ebe3, toneMapped: false })
  );
  backdrop.position.z = -7;
  scene.add(backdrop);

  /* a soft contact shadow, sitting on the backdrop behind each sample */
  const shadow = (() => {
    const c = document.createElement('canvas');
    c.width = c.height = 128;
    const x = c.getContext('2d');
    const g = x.createRadialGradient(64, 64, 2, 64, 64, 62);
    g.addColorStop(0, 'rgba(255,255,255,1)');
    g.addColorStop(0.5, 'rgba(255,255,255,.42)');
    g.addColorStop(1, 'rgba(255,255,255,0)');
    x.fillStyle = g; x.fillRect(0, 0, 128, 128);
    const m = new THREE.Mesh(
      new THREE.PlaneGeometry(1.6, 0.34),
      new THREE.MeshBasicMaterial({
        color: 0x4a3d31, alphaMap: new THREE.CanvasTexture(c),
        transparent: true, opacity: 0.1, depthWrite: false, toneMapped: false
      })
    );
    m.position.set(0, -0.62, -0.6);
    return m;
  })();
  scene.add(shadow);

  /* ---------- textures ---------- */
  const loader = new THREE.TextureLoader();
  const anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
  const texCache = new Map();
  const tex = (file, srgb, repeat) => {
    let src = texCache.get(file);
    if (!src) {
      src = loader.load(base + file);
      src.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace;
      src.anisotropy = anisotropy;
      src.wrapS = src.wrapT = THREE.ClampToEdgeWrapping;
      texCache.set(file, src);
    }
    /* the face and edge crops share one download, each with its own UV window */
    const t = src.clone();
    t.needsUpdate = true;
    if (repeat) { t.repeat.set(repeat[0], repeat[1]); t.offset.set(repeat[2], repeat[3]); }
    return t;
  };
  const mapSet = (slug, repeat) => ({
    map: tex(`tex-${slug}.webp`, true, repeat),
    normalMap: tex(`tex-${slug}-n.webp`, false, repeat),
    roughnessMap: tex(`tex-${slug}-r.webp`, false, repeat)
  });

  /* ---------- the five samples: one shared specimen, five materials ----------
     Every material is the same uninterrupted landscape slab, same dimensions,
     same framing; only the surface changes. */
  const pivot = new THREE.Group();
  scene.add(pivot);

  const SLAB = { w: 1.78, h: 1.02, d: 0.115 };
  /* the square scan is cropped to the slab's landscape proportion, never stretched */
  const FACE_UV = [1, SLAB.h / SLAB.w, 0, (1 - SLAB.h / SLAB.w) / 2];
  const EDGE_UV = [0.26, 0.06, 0.37, 0.47];

  const faceMaterial = {
    walnut: () => new THREE.MeshPhysicalMaterial({
      ...mapSet('walnut', FACE_UV),
      roughness: 1, clearcoat: 0.09, clearcoatRoughness: 0.6, envMapIntensity: 0.34
    }),
    pietra: () => new THREE.MeshPhysicalMaterial({
      ...mapSet('pietra', FACE_UV),
      roughness: 1, clearcoat: 0.16, clearcoatRoughness: 0.34, envMapIntensity: 0.55
    }),
    bronze: () => new THREE.MeshPhysicalMaterial({
      ...mapSet('bronze', FACE_UV),
      metalness: 1, roughness: 1, envMapIntensity: 1.1
    }),
    leather: () => new THREE.MeshPhysicalMaterial({
      ...mapSet('leather', FACE_UV),
      roughness: 1, clearcoat: 0.03, clearcoatRoughness: 0.95, envMapIntensity: 0.22,
      sheen: 0.16, sheenRoughness: 0.9, sheenColor: new THREE.Color(0x7d5a40)
    })
  };

  const edgeMaterial = {
    walnut: () => new THREE.MeshPhysicalMaterial({
      ...mapSet('walnut', EDGE_UV), color: 0xc9c2bb,
      roughness: 1, envMapIntensity: 0.2
    }),
    pietra: () => new THREE.MeshPhysicalMaterial({
      ...mapSet('pietra', EDGE_UV), color: 0xb8b6b2,
      roughness: 1, envMapIntensity: 0.3
    }),
    bronze: () => new THREE.MeshPhysicalMaterial({
      ...mapSet('bronze', EDGE_UV), color: 0xd8cfc2,
      metalness: 1, roughness: 1, envMapIntensity: 0.7
    }),
    leather: () => new THREE.MeshPhysicalMaterial({
      ...mapSet('leather', EDGE_UV), color: 0xbfb4ab,
      roughness: 1, envMapIntensity: 0.18
    })
  };

  /* body-tinted smoked float glass: one pane, physically based transmission */
  const glassMaterial = () => new THREE.MeshPhysicalMaterial({
    color: 0xffffff, metalness: 0, roughness: 0.025,
    transmission: 1, thickness: 0.5, ior: 1.51,
    attenuationColor: new THREE.Color(0x7a7a7b), attenuationDistance: 0.9,
    specularIntensity: 1, envMapIntensity: 1.4, transparent: true
  });

  const slab = (slug) => {
    const geo = new THREE.BoxGeometry(SLAB.w, SLAB.h, SLAB.d);
    if (!slug) return new THREE.Mesh(geo, glassMaterial());
    const face = faceMaterial[slug]();
    const edge = edgeMaterial[slug]();
    /* +x, -x, +y, -y, +z, -z */
    return new THREE.Mesh(geo, [edge, edge, edge, edge, face, face]);
  };

  /* two slim studio flags standing behind the glass sample only: seen through
     the pane they shift, darken and pick up the body tint, which is how the
     glass reads as glass rather than as a grey card */
  const studioCard = (() => {
    const g = new THREE.Group();
    const bar = (x, w, hex) => {
      const m = new THREE.Mesh(
        new THREE.BoxGeometry(w, 1.62, 0.02),
        new THREE.MeshStandardMaterial({ color: hex, roughness: 0.9, metalness: 0 })
      );
      m.position.set(x, 0, -0.8);
      return m;
    };
    g.add(bar(-0.5, 0.062, 0xa2988b), bar(0.36, 0.034, 0xc8bfb1));
    g.visible = false;
    return g;
  })();
  scene.add(studioCard);

  const slugs = ['walnut', 'pietra', 'bronze', 'leather', null];
  const objects = slugs.map(() => null);
  const show = (i) => {
    if (!objects[i]) { objects[i] = slab(slugs[i]); pivot.add(objects[i]); }
    objects.forEach((o, n) => { if (o) o.visible = n === i; });
    studioCard.visible = !slugs[i];
    shadow.material.opacity = slugs[i] ? 0.1 : 0.045;
  };


  show(0);
  pivot.rotation.set(-0.1, 0.42, 0);

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
      gsap.to(pivot.rotation, { y: pivot.rotation.y + Math.PI * 2, duration: 1.25, ease: 'power2.inOut' });
      gsap.to(pivot.scale, { x: 0.94, y: 0.94, z: 0.94, duration: 0.5, ease: 'power2.out', yoyo: true, repeat: 1 });
      gsap.delayedCall(0.5, () => show(i));
    } else {
      show(i);
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
    pivot.rotation.y += vy + (dragging || reduce ? 0 : 0.0012);
    pivot.rotation.x = Math.max(-0.6, Math.min(0.6, pivot.rotation.x + vx));
    vx *= 0.9; vy *= 0.9;
    renderer.render(scene, camera);
    raf = requestAnimationFrame(tick);
  }
  if (!raf) tick();
}
