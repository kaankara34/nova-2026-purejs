import io, re, sys

P = '/app/frontend/js/construction.js'
src = io.open(P, encoding='utf-8').read()
lines = src.split('\n')

# ---- sanity: line anchors (1-based) ----
def at(n):
    return lines[n - 1]

assert at(167).strip().startswith('function stirrup('), at(167)
assert at(212).strip() == '}', at(212)
assert at(526).strip().startswith('/* ---------------- 05 reinforcement cage'), at(526)
assert at(670).strip() == '});', at(670)
assert at(671).strip().startswith('} else if (marks.length)'), at(671)

PRIMS = r'''  /* --- reinforcement primitives -------------------------------------------
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
      const n = clamp(Math.floor(len / (r * 2.5)), 4, 90);
      const trg = new THREE.TorusGeometry(r * 1.04, r * .17, 4, 9);
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
    const hl = Math.min(hx, hz) * .52;
    const dir = new THREE.Vector3(-sx, 0, -sz).normalize();
    [-1, 1].forEach(side => {
      const p0 = new THREE.Vector3(sx * (hx - cr * .4), side * r * 1.9, sz * (hz - cr * .4));
      const p1 = p0.clone().addScaledVector(dir, hl * .34).add(new THREE.Vector3(0, side * r * 1.2, 0));
      const p2 = p0.clone().addScaledVector(dir, hl).add(new THREE.Vector3(0, side * r * 3.1, 0));
      g.add(bentBar([p0, p1, p2], r, mat, false, ribbed));
    });
    return g;
  }
  /* single-leg cross-tie: one continuous bar across the short direction of the
     confined core, hooked at both ends around the longitudinal bar it restrains
     and engaging the perimeter hoop leg at the same level */
  function crossTie(zEnd, r, mat, flip, ribbed) {
    const hl = zEnd * .46, k = .707, y = flip * r * .6;
    const pts = [
      new THREE.Vector3(0, y - flip * hl * k, -zEnd + hl * k),
      new THREE.Vector3(0, y - flip * r * 1.7, -zEnd - r * .45),
      new THREE.Vector3(0, y, -zEnd + r * 1.1),
      new THREE.Vector3(0, y, zEnd - r * 1.1),
      new THREE.Vector3(0, y - flip * r * 1.7, zEnd + r * .45),
      new THREE.Vector3(0, y - flip * hl * k, zEnd - hl * k)
    ];
    return bentBar(pts, r, mat, false, ribbed);
  }
  function setMat(obj, m) {
    obj.traverse(o => { if (o.isMesh || o.isInstancedMesh) o.material = m; });
  }'''

CAGE = r'''  /* ---------------- 05 reinforcement cage (WebGL assembly) ----------------
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
    if (sec && canvas && gl) {
      const w = scene3(canvas);
      const mat = steelMat();
      const conf = new THREE.MeshStandardMaterial({ color: 0x9fbf86, roughness: .42, metalness: .72, emissive: 0x2c3d22, emissiveIntensity: .5 });
      const ribbed = !mobile;

      /* 1 — horizontal section topology (solved before any extrusion)
         column boundary -> cover zone -> closed hoop -> longitudinal bars ->
         cross-tie positions. Every value below is a proportion, not a dimension. */
      const BX = 1.58, BZ = 1.06, L = 3.44, FD = .6;
      const COV = .085;
      const RH = .028, RL = .054, RT = .026;
      const hx = BX / 2 - COV - RH, hz = BZ / 2 - COV - RH;   // hoop centreline
      const ix = hx - RH - RL, iz = hz - RH - RL;             // longitudinal bar centres
      const XS = [-ix, -ix / 2, 0, ix / 2, ix];               // symmetric perimeter arrangement
      const TIE_X = [-ix / 2, 0, ix / 2];                     // intermediate bars need restraint

      /* transverse levels: dense in both special confinement regions, wider in
         the mid-region — the differentiation is the point of the model */
      const zoneT = L * .2;
      const pd = L * (mobile ? .05 : .039), pm = L * (mobile ? .14 : .11);
      const y0 = -L / 2 + L * .02, y1 = L / 2 - L * .02;
      const levels = [];
      for (let y = y0; y <= y0 + zoneT + 1e-6; y += pd) levels.push({ y, c: true });
      for (let y = y0 + zoneT + pm; y < y1 - zoneT - 1e-6; y += pm) levels.push({ y, c: false });
      for (let y = y1 - zoneT; y <= y1 + 1e-6; y += pd) levels.push({ y, c: true });

      const cage = new THREE.Group();
      w.scene.add(cage);
      const mains = [], dowels = [], hoops = [], ties = [];

      /* 2 — longitudinal reinforcement (ribbed bars, perimeter only) */
      XS.forEach(x => [-iz, iz].forEach(z => {
        const b = rebar(L, RL, mat);
        b.position.set(x, 0, z);
        b.userData.home = b.position.clone();
        cage.add(b); mains.push(b);
        /* 5 — continuity into the foundation: straight continuation only, the
           anchorage configuration itself is project specific */
        const d = rebar(FD * .8, RL, mat);
        d.position.set(x, -L / 2 - FD * .33, z);
        d.visible = false;
        cage.add(d); dowels.push(d);
      }));

      /* 3 + 4 — closed hoops and cross-ties at every level */
      levels.forEach((lv, i) => {
        const corner = [[1, 1], [-1, 1], [-1, -1], [1, -1]][i % 4];
        const h = perimeterHoop(hx, hz, RH, mat, corner, ribbed);
        h.position.y = lv.y;
        h.userData.home = lv.y;
        h.userData.conf = lv.c;
        cage.add(h); hoops.push(h);
        TIE_X.forEach((x, k) => {
          const t = crossTie(iz, RT, mat, (i + k) % 2 ? 1 : -1, ribbed);
          t.position.set(x, lv.y, 0);
          t.userData.conf = lv.c;
          cage.add(t); ties.push(t);
        });
      });

      /* subordinate foundation block */
      const fndMat = new THREE.MeshStandardMaterial({ color: 0xb8b3ab, roughness: .95, metalness: .02, transparent: true, opacity: 0 });
      const fndGeo = new THREE.BoxGeometry(BX * 2.05, FD, BZ * 2.5);
      const fnd = new THREE.Mesh(fndGeo, fndMat);
      fnd.position.y = -L / 2 - FD / 2 + FD * .1;
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

      w.cam.position.set(3.2, 1.5, 8.6);
      w.cam.lookAt(0, -.1, 0);
      let need = true;
      const draw = () => { if (need) { w.renderer.render(w.scene, w.cam); need = false; } requestAnimationFrame(draw); };
      requestAnimationFrame(draw);
      const phase = p => p < .14 ? 0 : p < .34 ? 1 : p < .5 ? 2 : p < .66 ? 3 : p < .82 ? 4 : 5;
      if (marks[0]) marks[0].classList.add('is-on');
      let matState = -1;
      const cageUpdate = p => {
        cage.rotation.y = THREE.MathUtils.degToRad(22 + p * 44);
        cage.rotation.x = -.05;
        /* 01 — longitudinal reinforcement moves into its section position */
        mains.forEach((b, i) => {
          const enter = seg(p, .002 + i * .006, .045 + i * .006);
          const h = b.userData.home;
          const out = 1 + (1 - enter) * 1.6;
          b.position.set(h.x * out, h.y, h.z * out);
        });
        /* 02 — closed transverse reinforcement, bottom to top */
        const hn = hoops.length;
        hoops.forEach((s, i) => {
          const t = i / hn;
          const a = seg(p, .14 + t * .16, .21 + t * .16);
          s.visible = a > .02;
          s.position.y = s.userData.home + (1 - a) * .42;
        });
        /* 03 — cross-ties */
        const tn = ties.length;
        ties.forEach((t, i) => {
          const a = seg(p, .34 + (i / tn) * .12, .4 + (i / tn) * .12);
          t.visible = a > .02;
          t.scale.set(1, 1, .35 + a * .65);
        });
        /* 04 — special confinement regions read against the mid-region */
        const st = p >= .5 ? 1 : 0;
        if (st !== matState) {
          matState = st;
          hoops.forEach(s => setMat(s, st && s.userData.conf ? conf : mat));
          ties.forEach(t => setMat(t, st && t.userData.conf ? conf : mat));
        }
        /* 05 — foundation continuity */
        const f = seg(p, .66, .8);
        dowels.forEach(d => { d.visible = f > .02; d.scale.setScalar(1); });
        fndMat.opacity = f * .26;
        fndEdges.material.opacity = f * .7;
        fnd.visible = fndEdges.visible = f > .01;
        /* 06 — concrete cover boundary */
        const c = seg(p, .82, .97);
        concreteMat.opacity = c * .16;
        edges.material.opacity = c * .85;
        concrete.visible = c > .01;
        const ph = phase(p);
        marks.forEach(m => m.classList.toggle('is-on', +m.dataset.mark === ph + 1));
        w.cam.position.set(3.2 - p * .35, 1.5 - p * .5, 8.6 + p * 1.2);
        w.cam.lookAt(0, -.1 - p * .22, 0);
        need = true;
      };
      cageUpdate(0);
      /* validation hook: 4 mandatory views (top / front / side / perspective) */
      window.cxCageView = (v, p) => {
        cageUpdate(typeof p === 'number' ? p : 1);
        cage.rotation.set(0, 0, 0);
        const d = 8.6;
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
      });'''

new = lines[:525] + CAGE.split('\n') + lines[670:]
# primitives replacement (indices before 525 stay valid because we splice after)
new2 = new[:166] + PRIMS.split('\n') + new[212:]
io.open(P, 'w', encoding='utf-8').write('\n'.join(new2))
print('cage rebuilt')
