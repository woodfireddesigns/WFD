'use strict';
// Recovery body map. Each view is a Blender render of the Z-Anatomy model (CC BY-SA 4.0)
// plus an ID map whose grey value (group index + 1) * 16 says which muscle group a pixel is.
// The canvas blends ember glow into each muscle by fatigue while keeping the sculpted shading.
const BODY_GROUPS = ['chest', 'shoulders', 'triceps', 'lats', 'upperback', 'traps', 'biceps', 'forearms', 'quads', 'hamstrings', 'glutes', 'calves', 'abs', 'lowerback'];
// The female figure is the same model reshaped in Blender (tools/blender/render.py, "fem").
const BODY_SRC = {
  front: { base: 'img/body-front.webp', id: 'img/body-front-id.png', ratio: '426 / 1045' },
  back: { base: 'img/body-back.webp', id: 'img/body-back-id.png', ratio: '426 / 1045' },
  'front-f': { base: 'img/body-front-f.webp', id: 'img/body-front-f-id.png', ratio: '400 / 983' },
  'back-f': { base: 'img/body-back-f.webp', id: 'img/body-back-f-id.png', ratio: '400 / 983' },
};
const bodyKey = view => (typeof S !== 'undefined' && S.settings.sex === 'female' ? view + '-f' : view);
const bodyData = {};

function loadImage(src) {
  return new Promise((ok, fail) => { const im = new Image(); im.onload = () => ok(im); im.onerror = fail; im.src = src; });
}
function loadBody(view) {
  if (bodyData[view]) return bodyData[view].ready;
  const d = bodyData[view] = {};
  d.ready = Promise.all([loadImage(BODY_SRC[view].base), loadImage(BODY_SRC[view].id)]).then(([base, id]) => {
    const w = base.naturalWidth, h = base.naturalHeight;
    const c = document.createElement('canvas'); c.width = w; c.height = h;
    const x = c.getContext('2d', { willReadFrequently: true });
    x.drawImage(base, 0, 0); d.base = x.getImageData(0, 0, w, h);
    x.clearRect(0, 0, w, h); x.drawImage(id, 0, 0, w, h);
    const raw = x.getImageData(0, 0, w, h).data;
    d.ids = new Uint8Array(w * h);
    for (let i = 0; i < w * h; i++) d.ids[i] = Math.min(14, Math.round(raw[i * 4] / 16));
    d.w = w; d.h = h;
    return d;
  });
  return d.ready;
}

// Paint every .body-cv canvas on the page for the given recovery map.
function paintBodies(rec, selected) {
  document.querySelectorAll('canvas.body-cv').forEach(cv => {
    const view = bodyKey(cv.dataset.view);
    cv.style.aspectRatio = BODY_SRC[view].ratio;
    loadBody(view).then(d => {
      if (!cv.isConnected) return;
      cv.width = d.w; cv.height = d.h;
      // per-group glow strength 0..1 (fatigue), with a floor so any fatigue is visible
      const amt = new Float32Array(15), sel = new Uint8Array(15);
      BODY_GROUPS.forEach((m, i) => {
        const p = rec[m] ?? 100;
        // 95%+ reads as fresh; below that glow ramps up so 40% clearly out-burns 85%
        const f = (100 - p) / 100;
        amt[i + 1] = p >= 95 ? 0 : Math.min(1, 0.1 + 1.25 * Math.pow(f, 1.1));
        sel[i + 1] = selected === m ? 1 : 0;
      });
      const src = d.base.data, out = new ImageData(d.w, d.h), o = out.data, ids = d.ids;
      for (let i = 0, n = d.w * d.h; i < n; i++) {
        const k = i * 4;
        let r = src[k], g = src[k + 1], b = src[k + 2];
        const id = ids[i];
        if (id) {
          const a = amt[id];
          if (a > 0) {
            // ember glow modulated by the sculpt's own lighting so form stays readable
            const lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
            const s = 0.38 + lum * 2.2;
            r += (Math.min(255, 255 * s) - r) * a;
            g += (Math.min(255, 92 * s) - g) * a;
            b += (Math.min(255, 30 * s) - b) * a;
          }
          if (sel[id]) { r = r + (255 - r) * 0.12; g = g + (236 - g) * 0.12; b = b + (220 - b) * 0.12; }
        }
        o[k] = r; o[k + 1] = g; o[k + 2] = b; o[k + 3] = src[k + 3];
      }
      cv.getContext('2d').putImageData(out, 0, 0);
    }).catch(() => { /* image failed to load: canvas stays blank */ });
  });
}

// Muscle group under a tap on a body canvas, or null.
function bodyHit(cv, ev) {
  const d = bodyData[bodyKey(cv.dataset.view)]; if (!d || !d.ids) return null;
  const r = cv.getBoundingClientRect();
  const x = Math.floor((ev.clientX - r.left) / r.width * d.w), y = Math.floor((ev.clientY - r.top) / r.height * d.h);
  // search a small radius so near-misses on thin muscles still register
  for (let rad = 0; rad <= 10; rad += 2) {
    for (let dy = -rad; dy <= rad; dy += 2) for (let dx = -rad; dx <= rad; dx += 2) {
      const xx = x + dx, yy = y + dy;
      if (xx < 0 || yy < 0 || xx >= d.w || yy >= d.h) continue;
      const id = d.ids[yy * d.w + xx];
      if (id) return BODY_GROUPS[id - 1];
    }
  }
  return null;
}
