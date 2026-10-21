'use strict';
/* =========================================================================
   KILN — personal strength training app
   Vanilla JS, no build step. All data lives in localStorage on the device.
   ========================================================================= */

/* ---------- constants ---------- */
const STORE_KEY = 'kiln.v1';
const MUSCLES = {
  chest: 'Chest', shoulders: 'Shoulders', triceps: 'Triceps', lats: 'Lats', upperback: 'Upper Back',
  traps: 'Traps', biceps: 'Biceps', forearms: 'Forearms', quads: 'Quads', hamstrings: 'Hamstrings',
  glutes: 'Glutes', calves: 'Calves', abs: 'Abs', lowerback: 'Lower Back',
};
const MUSCLE_ABBR = {
  chest: 'CH', shoulders: 'SH', triceps: 'TR', lats: 'LT', upperback: 'UB', traps: 'TP', biceps: 'BI',
  forearms: 'FA', quads: 'QD', hamstrings: 'HM', glutes: 'GL', calves: 'CV', abs: 'AB', lowerback: 'LB', other: '··',
};
const BIG = new Set(['chest', 'lats', 'upperback', 'quads', 'hamstrings', 'glutes', 'lowerback']);
const recoveryHours = m => (BIG.has(m) ? 72 : 48);
const FATIGUE_SETS = 8; // effective sets that take a muscle to 0% recovered

const EQUIPMENT = [
  ['barbell', 'Barbell + rack'], ['ez', 'EZ bar'], ['trapbar', 'Trap bar'], ['dumbbell', 'Dumbbells'],
  ['kettlebell', 'Kettlebells'], ['cable', 'Cable station'], ['machine', 'Plate / pin machines'],
  ['smith', 'Smith machine'], ['legpress', 'Leg press'], ['pullup', 'Pull-up bar'], ['dip', 'Dip station'],
  ['bench', 'Adjustable bench'], ['band', 'Resistance bands'],
];
const ALL_EQUIP = EQUIPMENT.map(e => e[0]);

const GOALS = {
  strength: { label: 'Strength', sub: 'Heavy compounds, 4–6 reps, long rest' },
  hypertrophy: { label: 'Build Muscle', sub: '6–15 reps, moderate rest' },
  lean: { label: 'Lean & Conditioned', sub: 'Higher reps, short rest, more density' },
};
const SPLITS = {
  auto: { label: 'Auto', sub: 'Push / Pull / Legs, picked by recovery', foci: ['push', 'pull', 'legs'] },
  ppl: { label: 'Push / Pull / Legs', sub: 'Strict rotation', foci: ['push', 'pull', 'legs'], rotate: true },
  ul: { label: 'Upper / Lower', sub: 'Strict rotation', foci: ['upper', 'lower'], rotate: true },
  full: { label: 'Full Body', sub: 'Everything, every session', foci: ['full'] },
};
const FOCUS = { push: 'Push', pull: 'Pull', legs: 'Legs', upper: 'Upper Body', lower: 'Lower Body', full: 'Full Body', custom: 'Custom' };
// [muscle, preference] C = compound, I = isolation, A = any
const TEMPLATES = {
  push: [['chest', 'C'], ['shoulders', 'C'], ['chest', 'A'], ['triceps', 'I'], ['shoulders', 'I'], ['triceps', 'A'], ['chest', 'I'], ['shoulders', 'I']],
  pull: [['lats', 'C'], ['upperback', 'C'], ['biceps', 'I'], ['lats', 'A'], ['upperback', 'I'], ['biceps', 'I'], ['traps', 'I'], ['forearms', 'I']],
  legs: [['quads', 'C'], ['hamstrings', 'C'], ['quads', 'A'], ['hamstrings', 'I'], ['glutes', 'A'], ['calves', 'I'], ['quads', 'I'], ['lowerback', 'I']],
  upper: [['chest', 'C'], ['lats', 'C'], ['shoulders', 'C'], ['upperback', 'C'], ['triceps', 'I'], ['biceps', 'I'], ['shoulders', 'I'], ['chest', 'I']],
  lower: [['quads', 'C'], ['hamstrings', 'C'], ['glutes', 'A'], ['quads', 'A'], ['hamstrings', 'I'], ['calves', 'I'], ['lowerback', 'I'], ['quads', 'I']],
  full: [['quads', 'C'], ['chest', 'C'], ['lats', 'C'], ['hamstrings', 'C'], ['shoulders', 'A'], ['upperback', 'C'], ['biceps', 'I'], ['triceps', 'I']],
};
const DURATION_EXERCISES = { 30: 4, 45: 5, 60: 6, 75: 7, 90: 8 };

/* ---------- state ---------- */
function defaultState() {
  return {
    v: 1,
    onboarded: false,
    settings: {
      unit: 'lb', bodyweight: 185, experience: 'intermediate', goal: 'hypertrophy', split: 'auto',
      duration: 60, core: true, warmups: true, sound: true, wake: true,
      gym: 'gym', incBar: 5, incDb: 5, incMachine: 5,
      health: false, healthWeight: true, healthShortcut: 'Kiln to Health',
    },
    gyms: [
      { id: 'gym', name: 'Commercial Gym', equip: [...ALL_EQUIP] },
      { id: 'home', name: 'Home', equip: ['dumbbell', 'bench', 'pullup', 'band'] },
    ],
    fav: {}, ban: {}, custom: [],
    workouts: [], plan: null, body: [], seed: 1,
    deload: null,
  };
}
function mergeState(data) {
  const def = defaultState();
  const s = { ...def, ...data };
  s.settings = { ...def.settings, ...(data.settings || {}) };
  return s;
}
const S = (() => {
  try {
    const raw = localStorage.getItem(STORE_KEY);
    if (raw) return mergeState(JSON.parse(raw));
  } catch (e) { /* fall through to defaults */ }
  return defaultState();
})();

let saveTimer;
function save() { clearTimeout(saveTimer); saveTimer = setTimeout(saveNow, 300); }
function saveNow() {
  clearTimeout(saveTimer);
  try { localStorage.setItem(STORE_KEY, JSON.stringify(S)); }
  catch (e) { toast('Storage is full. Export a backup in Settings.'); }
}
addEventListener('pagehide', saveNow);
document.addEventListener('visibilitychange', () => { if (document.hidden) saveNow(); });

let dataVersion = 0;
function touch() { dataVersion++; save(); }

/* ---------- helpers ---------- */
const $ = s => document.querySelector(s);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const uid = () => Math.random().toString(36).slice(2, 9) + Date.now().toString(36).slice(-4);
const DAY = 864e5;
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const dayKey = (t = Date.now()) => { const d = new Date(t); return `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()}`; };
const KG = 2.20462;
const U = () => S.settings.unit;
const toDisp = lb => (U() === 'kg' ? lb / KG : lb);
const fromDisp = x => (U() === 'kg' ? x * KG : x);
function fmtNum(x) { if (x == null || x === '' || isNaN(x)) return ''; const r = Math.round(x * 10) / 10; return String(r); }
const fmtW = lb => (lb ? fmtNum(Math.round(toDisp(lb) * 4) / 4) : '0');
const fmtBig = n => (n >= 1e6 ? (n / 1e6).toFixed(1) + 'M' : n >= 1e4 ? Math.round(n / 1e3) + 'k' : n >= 1e3 ? (n / 1e3).toFixed(1) + 'k' : String(Math.round(n)));
function fmtDur(ms) { const m = Math.round(ms / 6e4); return m >= 60 ? `${Math.floor(m / 60)}h ${m % 60}m` : `${m}m`; }
function fmtClock(sec) { sec = Math.max(0, Math.round(sec)); const m = Math.floor(sec / 60), s = sec % 60; return `${m}:${String(s).padStart(2, '0')}`; }
function fmtDate(t, opts = { weekday: 'short', month: 'short', day: 'numeric' }) { return new Date(t).toLocaleDateString(undefined, opts); }
function rng(seed) { let a = seed >>> 0; return () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const dayNum = () => Math.floor((Date.now() - new Date().getTimezoneOffset() * 6e4) / DAY);
function norm(name) {
  return String(name).toLowerCase().replace(/[^a-z0-9 ]/g, ' ').split(/\s+/).filter(Boolean)
    .map(w => (w.length > 3 && w.endsWith('s') && !w.endsWith('ss') ? w.slice(0, -1) : w)).join('');
}

/* ---------- exercises ---------- */
let EX = {};
function rebuildEx() {
  EX = {};
  for (const e of LIBRARY) EX[e.id] = e;
  for (const e of S.custom) EX[e.id] = { ...e, custom: true };
}
rebuildEx();
const exName = id => EX[id]?.name || 'Unknown exercise';
const activeGym = () => S.gyms.find(g => g.id === S.settings.gym) || S.gyms[0];
const isBarbell = e => (e.equip || []).includes('barbell');
const barLb = () => (U() === 'kg' ? 20 * KG : 45);

/* ---------- history ---------- */
let histVersion = -1, HIST = {};
function hist() {
  if (histVersion !== dataVersion) {
    HIST = {};
    const ws = [...S.workouts].sort((a, b) => a.start - b.start);
    for (const w of ws) for (const x of w.exercises) {
      const sets = x.sets.filter(s => s.done && !s.wu);
      if (sets.length) (HIST[x.exId] ||= []).push({ date: w.start, wid: w.id, sets, effort: x.effort || 0, deload: !!w.deload });
    }
    histVersion = dataVersion;
  }
  return HIST;
}
function e1rm(w, r) { if (!w || !r) return 0; return r === 1 ? w : w * (1 + Math.min(r, 15) / 30); }
function metric(e, s) {
  if (!e) return 0;
  if (e.kind === 'w') return e1rm(s.w, s.r);
  if (e.kind === 'bw') return (s.r || 0) + (s.w ? s.w / 10 : 0);
  if (e.kind === 't') return s.s || 0;
  return (s.w || 0) + (s.s || 0) / 1000;
}
function metricLabel(e) { return e.kind === 'w' ? 'Est. 1RM' : e.kind === 'bw' ? 'Best reps' : e.kind === 't' ? 'Best time' : 'Best load'; }
function fmtMetric(e, v) {
  if (e.kind === 'w') return `${fmtW(v)} ${U()}`;
  if (e.kind === 'bw') return `${Math.floor(v)} reps`;
  if (e.kind === 't') return fmtClock(v);
  return `${fmtW(Math.floor(v))} ${U()}`;
}
function sessionBest(e, sets) { return Math.max(0, ...sets.map(s => metric(e, s))); }
function fmtSet(e, s) {
  if (e.kind === 'w') return `${fmtW(s.w)}×${s.r || 0}`;
  if (e.kind === 'bw') return s.w ? `+${fmtW(s.w)}×${s.r || 0}` : `${s.r || 0}`;
  if (e.kind === 't') return fmtClock(s.s || 0);
  return `${fmtW(s.w)} · ${fmtClock(s.s || 0)}`;
}

/* ---------- recovery model ---------- */
// Each working set adds fatigue to its primary muscle (1.0) and secondaries (0.5),
// decaying linearly to zero over 48h (small muscles) or 72h (large muscles).
function recovery(now = Date.now()) {
  const fat = {}, last = {};
  for (const w of S.workouts) {
    const t = w.end || w.start;
    const ageH = (now - t) / 36e5;
    for (const x of w.exercises) {
      const e = EX[x.exId]; if (!e) continue;
      const n = x.sets.filter(s => s.done && !s.wu).length; if (!n) continue;
      const add = (m, k) => {
        if (!MUSCLES[m]) return;
        if (!last[m] || last[m] < t) last[m] = t;
        const d = Math.max(0, 1 - ageH / recoveryHours(m));
        if (d > 0) fat[m] = (fat[m] || 0) + n * k * d;
      };
      add(e.primary, 1);
      (e.secondary || []).forEach(m => add(m, 0.5));
    }
  }
  const r = {};
  for (const m in MUSCLES) r[m] = Math.round(clamp(100 - ((fat[m] || 0) / FATIGUE_SETS) * 100, 0, 100));
  return { r, last };
}
const recColor = p => (p >= 80 ? 'var(--good)' : p >= 50 ? 'var(--warn)' : 'var(--bad)');

/* ---------- programming ---------- */
function scheme(e) {
  const c = e.compound;
  const T = {
    strength: c ? [4, 4, 6, 180] : [3, 8, 12, 90],
    hypertrophy: c ? [3, 6, 10, 120] : [3, 10, 15, 75],
    lean: c ? [3, 8, 12, 75] : [3, 12, 15, 45],
  }[S.settings.goal] || [3, 8, 12, 90];
  const [sets, lo, hi, rest] = T;
  if (e.kind === 't' || e.kind === 'tw') return { sets: 3, lo: 0, hi: 0, rest: Math.min(rest, 75) };
  return { sets, lo, hi, rest };
}
function incFor(e) {
  const q = e.equip || [];
  if (q.some(k => ['barbell', 'ez', 'trapbar', 'smith'].includes(k))) return +S.settings.incBar || 5;
  if (q.some(k => ['dumbbell', 'kettlebell'].includes(k))) return +S.settings.incDb || 5;
  return +S.settings.incMachine || 5;
}
function roundW(lb, e) {
  const inc = incFor(e);
  let x = Math.max(inc, Math.round(toDisp(lb) / inc) * inc);
  let out = fromDisp(x);
  if (isBarbell(e) && out < barLb()) out = barLb();
  return out;
}
// Progression jump in display units. Compound barbell-style lifts move ~2.5% (rounded to real
// increments), everything else moves one increment. An "easy" rating doubles the jump.
function jumpFor(e, lb, effort) {
  const step = incFor(e);
  let j = step;
  if (e.compound && e.kind === 'w') j = Math.max(step, Math.round((toDisp(lb) * 0.025) / step) * step);
  return effort === 1 ? j * 2 : j;
}
const EFFORT = { 1: 'Easy', 2: 'Solid', 3: 'Grind' };
const BW_GRADUATE = 12; // bodyweight reps at which pull-ups/dips graduate to added weight
const canAddLoad = e => e.kind === 'bw' && e.compound && (e.equip || []).some(k => k === 'pullup' || k === 'dip');
function recommend(e, sc) {
  // deload sessions are deliberately light, so they never set the bar for the next session
  const H = (hist()[e.id] || []).filter(h => !h.deload);
  const last = H[H.length - 1], prev = H[H.length - 2];
  const mid = Math.round((sc.lo + sc.hi) / 2) || 8;
  const out = { w: null, r: mid, s: null, note: '', up: false };
  const expMult = { beginner: 0.7, intermediate: 1, advanced: 1.3 }[S.settings.experience] || 1;
  const eff = last?.effort || 2;
  const felt = last?.effort ? ` (${EFFORT[last.effort].toLowerCase()})` : '';

  if (e.kind === 'w') {
    if (last) {
      const top = Math.max(...last.sets.map(s => s.w || 0));
      const topSets = last.sets.filter(s => (s.w || 0) === top);
      const minR = Math.min(...topSets.map(s => s.r || 0));
      const add = j => roundW(fromDisp(toDisp(top) + j), e);
      if (top > 0 && minR >= sc.lo - 2 && minR <= sc.hi + 4) {
        if (minR >= sc.hi && eff === 3) {
          out.w = top; out.r = sc.hi;
          out.note = `Hold ${fmtW(top)}. You hit ${minR}s but it was a grind. Make it solid, then add weight`;
        } else if (minR >= sc.hi) {
          const j = jumpFor(e, top, eff);
          out.w = add(j); out.r = sc.lo; out.up = true;
          out.note = `+${j} ${U()}. You hit ${minR} reps at ${fmtW(top)}${felt}`;
        } else if (minR < sc.lo && prev && stalled(prev, top, sc.lo)) {
          out.w = roundW(top * 0.9, e); out.r = sc.lo + 1;
          out.note = 'Reset 10%. Missed the rep floor two sessions in a row';
        } else if (eff === 1 && minR >= mid) {
          const j = jumpFor(e, top, 2);
          out.w = add(j); out.r = clamp(minR - 2, sc.lo, sc.hi); out.up = true;
          out.note = `+${j} ${U()}. ${fmtW(top)}×${minR} felt easy`;
        } else if (eff === 3) {
          out.w = top; out.r = clamp(minR, sc.lo, sc.hi);
          out.note = `Repeat ${fmtW(top)}×${minR} and make it smoother`;
        } else {
          out.w = top; out.r = clamp(minR + (eff === 1 ? 2 : 1), sc.lo, sc.hi);
          out.note = `Beat last time: ${fmtW(top)}×${minR}${felt}`;
        }
      } else {
        const best = Math.max(...H.slice(-3).map(h => sessionBest(e, h.sets)));
        if (best > 0) { out.w = roundW((best / (1 + mid / 30)) * 0.97, e); out.note = `Based on est. 1RM of ${fmtW(best)}`; }
        else out.note = 'Pick a working weight';
      }
    } else if (e.ratio && S.settings.bodyweight) {
      out.w = roundW(S.settings.bodyweight * e.ratio * expMult, e);
      out.note = `First time. Starting estimate, adjust to a hard ${mid}`;
    } else out.note = 'First time. Find a weight for a hard ' + mid;
  } else if (e.kind === 'bw') {
    if (last) {
      const reps = last.sets.map(s => s.r || 0);
      const minR = Math.min(...reps), maxR = Math.max(...reps);
      const added = Math.max(...last.sets.map(s => s.w || 0));
      const step = +S.settings.incDb || 5;
      if (added > 0) {
        // weighted calisthenics: double progression on the added load
        if (minR >= sc.hi && eff !== 3) {
          out.w = fromDisp(toDisp(added) + step); out.r = sc.lo; out.up = true;
          out.note = `+${step} ${U()}. You hit ${minR} reps with +${fmtW(added)}`;
        } else if (eff === 3) { out.w = added; out.r = clamp(minR, sc.lo, sc.hi); out.note = `Repeat +${fmtW(added)}×${minR} and make it smoother`; }
        else { out.w = added; out.r = clamp(minR + 1, sc.lo, sc.hi); out.note = `Beat last time: +${fmtW(added)}×${minR}${felt}`; }
      } else if (canAddLoad(e) && minR >= BW_GRADUATE && eff !== 3) {
        out.w = fromDisp(step); out.r = sc.lo || 6; out.up = true;
        out.note = `${minR}+ clean reps. Time to add weight: +${step} ${U()} on a belt or a dumbbell between the feet`;
      } else {
        out.r = eff === 3 ? minR : minR >= maxR ? maxR + (eff === 1 ? 2 : 1) : minR + (eff === 1 ? 2 : 1);
        out.note = `Last: ${last.sets.map(s => fmtSet(e, s)).join(', ')}${felt}`;
        if (canAddLoad(e)) out.note += `. Weighted at ${BW_GRADUATE}+`;
      }
    } else { out.r = sc.lo || 8; out.note = 'First time. Log clean reps, stop 1–2 short of failure'; }
  } else if (e.kind === 't') {
    out.r = null;
    out.s = last ? Math.max(...last.sets.map(s => s.s || 0)) + (eff === 3 ? 0 : eff === 1 ? 10 : 5) : 30;
    out.note = last ? (eff === 3 ? 'Match last time' : 'Add time on last session') : 'First time. Hold with good form';
  } else if (e.kind === 'tw') {
    out.r = null;
    if (last) { out.w = Math.max(...last.sets.map(s => s.w || 0)) || null; out.s = Math.max(...last.sets.map(s => s.s || 0)) + 5; out.note = 'Add 5 seconds on last time'; }
    else { out.w = e.ratio ? roundW(S.settings.bodyweight * e.ratio * expMult, e) : null; out.s = 40; out.note = 'First time. Starting estimate'; }
  }
  return out;
}

/* ---------- deloads ---------- */
// A deload week is recommended after 6 training weeks, or sooner when 3+ lifts have stalled.
const DELOAD_WEEKS = 6, DELOAD_DAYS = 7;
function deloadInfo() {
  const now = Date.now();
  if (!S.deload) { S.deload = { anchor: now, until: 0, snooze: 0 }; save(); }
  const d = S.deload;
  if (d.until && now < d.until) return { active: true, daysLeft: Math.ceil((d.until - now) / DAY) };
  if (d.until && now >= d.until) { d.anchor = d.until; d.until = 0; save(); }
  const weeks = new Set(S.workouts.filter(w => w.start >= d.anchor && !w.deload).map(w => startOfWeek(w.start))).size;
  const stalls = stalledLifts();
  const info = { weeks, stalls };
  if (d.snooze && now < d.snooze) return info;
  if (weeks >= DELOAD_WEEKS) info.due = `${weeks} training weeks since your last deload`;
  else if (stalls.length >= 3) info.due = `${stalls.length} lifts have stalled: ${stalls.slice(0, 3).map(exName).join(', ')}`;
  return info;
}
function stalledLifts() {
  const out = [];
  for (const [id, sess] of Object.entries(hist())) {
    const e = EX[id]; if (!e || e.kind !== 'w') continue;
    const H = sess.filter(h => !h.deload);
    const last = H[H.length - 1], prev = H[H.length - 2];
    if (!last || !prev || Date.now() - last.date > 21 * DAY) continue;
    const sc = scheme(e);
    const top = Math.max(...last.sets.map(s => s.w || 0));
    if (top && stalled(last, top, sc.lo) && stalled(prev, top, sc.lo)) out.push(id);
  }
  return out;
}
const deloadActive = () => !!(S.deload?.until && Date.now() < S.deload.until);

function stalled(sess, top, lo) {
  const t = Math.max(...sess.sets.map(s => s.w || 0));
  return t === top && Math.min(...sess.sets.filter(s => s.w === t).map(s => s.r || 0)) < lo;
}
function warmups(e, w) {
  if (!S.settings.warmups || !w || e.kind !== 'w') return [];
  const q = e.equip || [];
  if (q.includes('barbell') || q.includes('trapbar') || q.includes('smith')) {
    const bar = q.includes('barbell') ? barLb() : roundW(w * 0.4, e);
    if (w <= bar * 1.4) return [];
    const out = [{ w: bar, r: 10, wu: true }];
    for (const [p, r] of [[0.5, 8], [0.7, 5], [0.85, 3]]) {
      const x = roundW(w * p, e);
      if (p === 0.85 && toDisp(w) < (U() === 'kg' ? 85 : 185)) continue;
      if (x > out[out.length - 1].w + 1 && x < w - 1) out.push({ w: x, r, wu: true });
    }
    return out;
  }
  const x = roundW(w * 0.6, e);
  return x < w ? [{ w: x, r: 8, wu: true }] : [];
}
function buildEntry(e, first) {
  const sc = scheme(e);
  const rec = recommend(e, sc);
  let n = sc.sets + (first && S.settings.goal === 'hypertrophy' && e.compound ? 1 : 0);
  if (deloadActive()) {
    n = Math.max(2, Math.round(sc.sets / 2));
    if (rec.w && e.kind === 'w') rec.w = roundW(rec.w * 0.9, e);
    if (rec.r && e.kind !== 'w') rec.r = Math.max(1, Math.round(rec.r * 0.7));
    else if (rec.r) rec.r = sc.lo || rec.r;
    rec.up = false;
    rec.note = 'Deload: 90% load, half the sets. Leave 3+ reps in the tank';
  }
  const sets = [];
  if (first) for (const s of warmups(e, rec.w)) sets.push({ ...s, s: null, done: false });
  for (let i = 0; i < n; i++) sets.push({ w: rec.w, r: rec.r, s: rec.s, done: false });
  return { id: uid(), exId: e.id, rest: sc.rest, lo: sc.lo, hi: sc.hi, note: rec.note, up: rec.up, sets };
}
const focusMuscles = f => [...new Set((TEMPLATES[f] || []).slice(0, 5).map(t => t[0]))];
function pickFocus(rec) {
  const sp = SPLITS[S.settings.split] || SPLITS.auto;
  const foci = sp.foci;
  if (foci.length === 1) return foci[0];
  if (sp.rotate) {
    const lw = S.workouts.find(w => foci.includes(w.focus));
    return lw ? foci[(foci.indexOf(lw.focus) + 1) % foci.length] : foci[0];
  }
  const lastFocus = S.workouts[0]?.focus;
  let best = foci[0], bs = -1e9;
  for (const f of foci) {
    const ms = focusMuscles(f);
    const avg = ms.reduce((a, m) => a + rec.r[m], 0) / ms.length;
    const lf = S.workouts.find(w => w.focus === f);
    const hrs = lf ? (Date.now() - lf.start) / 36e5 : 400;
    const score = avg + Math.min(hrs, 200) / 20 - (f === lastFocus ? 25 : 0);
    if (score > bs) { bs = score; best = f; }
  }
  return best;
}
function availableExercises() {
  const eq = new Set(activeGym().equip);
  return Object.values(EX).filter(e => !S.ban[e.id] && MUSCLES[e.primary] && (e.equip || []).every(k => eq.has(k)));
}
function generate(focus) {
  const rec = recovery();
  focus = focus || pickFocus(rec);
  const avail = availableExercises();
  const n = DURATION_EXERCISES[S.settings.duration] || 6;
  const rand = rng(S.seed * 7919 + dayNum());
  const H = hist();
  const recent = new Set();
  for (const w of S.workouts) { if (Date.now() - w.start > 21 * DAY) break; w.exercises.forEach(x => recent.add(x.exId)); }
  const lastSame = new Set((S.workouts.find(w => w.focus === focus)?.exercises || []).map(x => x.exId));
  const richGym = activeGym().equip.length > 5;
  const score = e => (S.fav[e.id] ? 4 : 0) + (H[e.id] ? 2 : 0) + (recent.has(e.id) ? 1.5 : 0)
    - (lastSame.has(e.id) ? 0.75 : 0) + (e.kind === 'w' ? 0.5 : 0)
    - (richGym && (e.equip || []).includes('band') ? 3 : 0) + rand() * 2.5;

  const chosen = [];
  const tpl = TEMPLATES[focus] || TEMPLATES.full;
  for (let pass = 0; pass < 3 && chosen.length < n; pass++) {
    for (const [m, pref] of tpl) {
      if (chosen.length >= n) break;
      if (pass === 0 && rec.r[m] < 30) continue;
      const c = avail.filter(e => e.primary === m && !chosen.includes(e));
      if (!c.length) continue;
      let cp = c.filter(e => (pref === 'C' ? e.compound : pref === 'I' ? !e.compound : true));
      if (!cp.length) cp = c;
      let best = null, bs = -1e9;
      for (const e of cp) { const s = score(e); if (s > bs) { bs = s; best = e; } }
      chosen.push(best);
    }
  }
  if (S.settings.core && rec.r.abs >= 50 && !chosen.some(e => e.primary === 'abs')) {
    const abs = avail.filter(e => e.primary === 'abs');
    if (abs.length) { let best = abs[0], bs = -1e9; for (const e of abs) { const s = score(e); if (s > bs) { bs = s; best = e; } } chosen.push(best); }
  }
  S.plan = {
    id: uid(), focus, gym: activeGym().id, day: dayKey(), created: Date.now(), start: null, deload: deloadActive(),
    exercises: chosen.map((e, i) => buildEntry(e, i === 0)),
  };
  save();
}
function ensurePlan() {
  if (!S.onboarded) return;
  if (!S.plan || (!S.plan.start && S.plan.day !== dayKey())) generate();
}

/* ---------- workout actions ---------- */
function startWorkout() {
  if (!S.plan) return;
  if (!S.plan.start) { S.plan.start = Date.now(); save(); }
  requestWake();
}
function finishWorkout() {
  const p = S.plan; if (!p) return;
  const H = hist();
  const exercises = [];
  const prs = [];
  for (const x of p.exercises) {
    const sets = x.sets.filter(s => s.done).map(s => ({ w: s.w ?? null, r: s.r ?? null, s: s.s ?? null, wu: !!s.wu, done: true }));
    if (!sets.length) continue;
    exercises.push({ exId: x.exId, sets, note: x.userNote || '', effort: x.effort || 0 });
    const e = EX[x.exId];
    const working = sets.filter(s => !s.wu);
    if (!e || !working.length) continue;
    const prevBest = Math.max(0, ...(H[x.exId] || []).map(h => sessionBest(e, h.sets)));
    const nowBest = sessionBest(e, working);
    if (prevBest > 0 && nowBest > prevBest + 0.01) prs.push({ exId: x.exId, value: nowBest, prev: prevBest });
  }
  if (!exercises.length) { toast('No completed sets to save'); return; }
  const w = { id: p.id, focus: p.focus, name: (FOCUS[p.focus] || 'Workout') + (p.deload ? ' · Deload' : ''), start: p.start || Date.now(), end: Date.now(), exercises, prs, deload: !!p.deload };
  S.workouts.unshift(w);
  S.workouts.sort((a, b) => b.start - a.start);
  S.plan = null; S.seed++;
  timer.stop(); releaseWake();
  touch();
  generate();
  saveNow();
  render();
  showSummary(w);
  if (S.settings.health) sendWorkoutToHealth(w);
}
function discardWorkout() {
  if (!confirm('Discard this workout? Logged sets will be lost.')) return;
  timer.stop(); releaseWake();
  S.plan = null; generate(); render(); window.scrollTo(0, 0);
}
function workoutVolume(w) {
  let v = 0, sets = 0;
  for (const x of w.exercises) for (const s of x.sets) if (s.done && !s.wu) { sets++; if (s.w && s.r) v += s.w * s.r; }
  return { v, sets };
}

/* ---------- rest timer ---------- */
const timer = {
  end: 0, total: 0, iv: null, done: false,
  start(sec) {
    this.total = sec; this.end = Date.now() + sec * 1000; this.done = false;
    clearInterval(this.iv); this.iv = setInterval(() => this.tick(), 250); this.tick();
  },
  add(sec) { if (!this.end) return; this.end += sec * 1000; this.total = Math.max(this.total + sec, 1); this.tick(); },
  stop() { clearInterval(this.iv); this.end = 0; const el = $('#timer'); if (el) el.hidden = true; },
  tick() {
    const el = $('#timer'); if (!el) return;
    if (!this.end) { el.hidden = true; return; }
    const left = (this.end - Date.now()) / 1000;
    if (left <= 0 && !this.done) { this.done = true; chime(); }
    if (left < -4) { this.stop(); return; }
    el.hidden = false;
    const pct = clamp(1 - left / this.total, 0, 1);
    el.className = left <= 0 ? 'go' : '';
    el.innerHTML = `
      <div class="t-bar" style="--p:${pct}"></div>
      <span class="t-label">${left <= 0 ? 'Go' : 'Rest'}</span>
      <span class="t-time">${left <= 0 ? 'Next set' : fmtClock(left)}</span>
      <button data-a="t-add" data-v="-15">−15</button>
      <button data-a="t-add" data-v="15">+15</button>
      <button data-a="t-skip" class="t-skip">Skip</button>`;
  },
};
let audioCtx;
function unlockAudio() {
  if (audioCtx) return;
  try { audioCtx = new (window.AudioContext || window.webkitAudioContext)(); } catch (e) { /* no audio */ }
}
function chime() {
  if (navigator.vibrate) navigator.vibrate([200, 100, 200]);
  if (!S.settings.sound || !audioCtx) return;
  try {
    audioCtx.resume();
    const t0 = audioCtx.currentTime;
    [0, 0.18].forEach((d, i) => {
      const o = audioCtx.createOscillator(), g = audioCtx.createGain();
      o.type = 'sine'; o.frequency.value = i ? 1175 : 880;
      g.gain.setValueAtTime(0.0001, t0 + d); g.gain.exponentialRampToValueAtTime(0.4, t0 + d + 0.02);
      g.gain.exponentialRampToValueAtTime(0.0001, t0 + d + 0.35);
      o.connect(g).connect(audioCtx.destination); o.start(t0 + d); o.stop(t0 + d + 0.4);
    });
  } catch (e) { /* ignore */ }
}

/* ---------- wake lock ---------- */
let wakeLock = null;
async function requestWake() {
  if (!S.settings.wake || !('wakeLock' in navigator) || wakeLock) return;
  try { wakeLock = await navigator.wakeLock.request('screen'); wakeLock.addEventListener('release', () => { wakeLock = null; }); } catch (e) { /* denied */ }
}
function releaseWake() { try { wakeLock?.release(); } catch (e) { /* ignore */ } wakeLock = null; }
document.addEventListener('visibilitychange', () => { if (!document.hidden && S.plan?.start) requestWake(); });

/* ---------- icons ---------- */
const I = {
  dumbbell: '<svg viewBox="0 0 24 24"><path d="M6.5 6.5v11M17.5 6.5v11M3.5 9v6M20.5 9v6M6.5 12h11"/></svg>',
  history: '<svg viewBox="0 0 24 24"><path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5M12 7v5l3 2"/></svg>',
  chart: '<svg viewBox="0 0 24 24"><path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/></svg>',
  list: '<svg viewBox="0 0 24 24"><path d="M9 6h12M9 12h12M9 18h12M4 6h.01M4 12h.01M4 18h.01"/></svg>',
  gear: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/></svg>',
  check: '<svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>',
  more: '<svg viewBox="0 0 24 24"><circle cx="5" cy="12" r="1.3"/><circle cx="12" cy="12" r="1.3"/><circle cx="19" cy="12" r="1.3"/></svg>',
  plus: '<svg viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg>',
  minus: '<svg viewBox="0 0 24 24"><path d="M5 12h14"/></svg>',
  refresh: '<svg viewBox="0 0 24 24"><path d="M21 12a9 9 0 1 1-2.6-6.4L21 8"/><path d="M21 3v5h-5"/></svg>',
  swap: '<svg viewBox="0 0 24 24"><path d="M7 4L3 8l4 4M3 8h14M17 20l4-4-4-4M21 16H7"/></svg>',
  star: '<svg viewBox="0 0 24 24"><path d="M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 16.9l-5.2 2.7 1-5.8-4.3-4.1 5.9-.9z"/></svg>',
  search: '<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>',
  chev: '<svg viewBox="0 0 24 24"><path d="M9 6l6 6-6 6"/></svg>',
  down: '<svg viewBox="0 0 24 24"><path d="M6 9l6 6 6-6"/></svg>',
  up: '<svg viewBox="0 0 24 24"><path d="M6 15l6-6 6 6"/></svg>',
  play: '<svg viewBox="0 0 24 24"><path d="M7 4.5v15l12-7.5z"/></svg>',
  trophy: '<svg viewBox="0 0 24 24"><path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0zM17 5h3v2a3 3 0 0 1-3 3M7 5H4v2a3 3 0 0 0 3 3"/></svg>',
  x: '<svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></svg>',
};

/* ---------- view state ---------- */
const V = { tab: 'workout', libQuery: '', libMuscle: 'all', sheet: null };

function render() {
  renderTabs();
  const fn = { workout: viewWorkout, history: viewHistory, progress: viewProgress, library: viewLibrary, settings: viewSettings }[V.tab];
  $('#view').innerHTML = fn();
  if (V.tab === 'workout') tickElapsed();
}
function renderTabs() {
  const tabs = [['workout', 'Workout', I.dumbbell], ['history', 'History', I.history], ['progress', 'Progress', I.chart], ['library', 'Exercises', I.list], ['settings', 'Settings', I.gear]];
  $('#tabs').innerHTML = tabs.map(([k, l, ic]) => `<button data-a="tab" data-v="${k}" class="${V.tab === k ? 'on' : ''}">${ic}<span>${l}</span></button>`).join('');
}

/* ---------- workout view ---------- */
function viewWorkout() {
  if (!S.onboarded) return viewWelcome();
  const p = S.plan;
  if (!p) return '<div class="empty">No plan yet.</div>';
  const started = !!p.start;
  const rec = recovery();
  const doneSets = p.exercises.reduce((a, x) => a + x.sets.filter(s => s.done && !s.wu).length, 0);
  const totalSets = p.exercises.reduce((a, x) => a + x.sets.filter(s => !s.wu).length, 0);
  const muscles = [...new Set(p.exercises.map(x => EX[x.exId]?.primary).filter(m => MUSCLES[m]))];
  const est = Math.round(p.exercises.reduce((a, x) => a + x.sets.length * (40 + x.rest), 0) / 60);

  return `
  <header class="page-head">
    <div class="eyebrow">${started ? `<span class="live"></span>In progress · <span id="elapsed">0:00</span>` : esc(fmtDate(Date.now(), { weekday: 'long', month: 'short', day: 'numeric' }))}</div>
    <div class="title-row">
      <h1>${esc(FOCUS[p.focus] || 'Workout')}</h1>
      ${started ? `<button class="btn-finish" data-a="finish">Finish</button>` : ''}
    </div>
    ${!started ? `
    <div class="chips">
      <button class="chip" data-a="pick-focus">${esc(FOCUS[p.focus])} ${I.down}</button>
      <button class="chip" data-a="pick-gym">${esc(activeGym().name)} ${I.down}</button>
      <button class="chip" data-a="pick-duration">${S.settings.duration} min ${I.down}</button>
    </div>` : `
    <div class="progress-line"><div style="width:${totalSets ? (doneSets / totalSets) * 100 : 0}%"></div></div>
    <div class="meta-line">${doneSets} of ${totalSets} working sets</div>`}
  </header>

  ${deloadBanner(started)}

  ${!started ? `
  <section class="target-strip">
    ${muscles.map(m => `<div class="tm"><div class="ring" style="--p:${rec.r[m]};--c:${recColor(rec.r[m])}"><span>${rec.r[m]}</span></div><label>${MUSCLES[m]}</label></div>`).join('')}
  </section>
  <div class="plan-meta"><span>${p.exercises.length} exercises</span><span>${totalSets} sets</span><span>~${est} min</span><span>${esc(GOALS[S.settings.goal].label)}</span></div>
  ` : ''}

  <section class="ex-list">
    ${p.exercises.map((x, i) => exerciseCard(x, i, started)).join('')}
  </section>

  <div class="add-row">
    <button class="btn ghost" data-a="add-ex">${I.plus} Add exercise</button>
    ${!started ? `<button class="btn ghost" data-a="regen">${I.refresh} Regenerate</button>` : `<button class="btn ghost danger" data-a="discard">Discard</button>`}
  </div>

  ${!started ? `<div class="dock"><button class="btn primary big" data-a="start">${I.play} Start Workout</button></div>` : ''}
  `;
}
function deloadBanner(started) {
  const d = deloadInfo();
  if (d.active) return `<div class="banner calm"><div><b>Deload week</b><span>${d.daysLeft} day${d.daysLeft === 1 ? '' : 's'} left. Lighter on purpose so you come back stronger.</span></div>${started ? '' : '<button class="btn sm" data-a="deload-end">End early</button>'}</div>`;
  if (d.due && !started) return `<div class="banner"><div><b>Deload week recommended</b><span>${esc(d.due)}. One lighter week: 90% load, half the sets.</span></div><div class="banner-actions"><button class="btn sm primary" data-a="deload-start">Start deload</button><button class="btn sm ghost" data-a="deload-snooze">Not now</button></div></div>`;
  return '';
}
function exerciseCard(x, i, started) {
  const e = EX[x.exId] || { name: 'Unknown', primary: 'other', kind: 'w', equip: [] };
  const working = x.sets.filter(s => !s.wu);
  const allDone = x.sets.length && x.sets.every(s => s.done);
  const target = e.kind === 't' ? `${working.length} × ${fmtClock(working[0]?.s || 30)}`
    : e.kind === 'tw' ? `${working.length} × ${fmtClock(working[0]?.s || 40)}`
      : `${working.length} × ${x.lo && x.hi ? `${x.lo}–${x.hi}` : working[0]?.r || ''}`;
  const topW = Math.max(0, ...working.map(s => s.w || 0));
  const plates = isBarbell(e) && topW ? plateText(topW) : '';
  const H = hist()[x.exId];
  const lastTxt = H ? H[H.length - 1].sets.map(s => fmtSet(e, s)).join('  ') : '';
  let k = 0;
  return `
  <article class="card ex ${allDone ? 'complete' : ''}" id="ex-${i}">
    <div class="ex-head">
      <div class="ex-badge m-${e.primary}">${MUSCLE_ABBR[e.primary] || '··'}</div>
      <div class="ex-title" data-a="ex-detail" data-v="${e.id}">
        <h3>${esc(e.name)}${S.fav[e.id] ? ' <i class="fav-dot"></i>' : ''}</h3>
        <p>${target}${e.kind === 'w' && topW ? ` · ${fmtW(topW)} ${U()}` : ''}${e.kind === 'bw' && topW ? ` · +${fmtW(topW)} ${U()}` : ''}</p>
      </div>
      <button class="icon-btn" data-a="ex-menu" data-i="${i}" aria-label="Exercise options">${I.more}</button>
    </div>
    ${x.note ? `<div class="hint ${x.up ? 'up' : ''}">${x.up ? '▲ ' : ''}${esc(x.note)}</div>` : ''}
    ${lastTxt ? `<div class="last">Last: ${esc(lastTxt)}</div>` : ''}
    ${plates ? `<div class="plates">${plates}</div>` : ''}
    <div class="sets kind-${e.kind}">
      <div class="set-h"><span>Set</span>${setHeaders(e)}<span></span></div>
      ${x.sets.map((s, j) => { if (!s.wu) k++; return setRow(e, s, i, j, s.wu ? 'W' : k); }).join('')}
    </div>
    ${started && working.length && working.every(s => s.done) ? `
    <div class="effort"><span>How did that feel?</span>${[1, 2, 3].map(v => `<button data-a="effort" data-i="${i}" data-v="${v}" class="${x.effort === v ? 'on e' + v : ''}">${EFFORT[v]}</button>`).join('')}</div>` : ''}
    <div class="ex-foot">
      <button data-a="add-set" data-i="${i}">${I.plus} Set</button>
      <button data-a="rm-set" data-i="${i}">${I.minus} Set</button>
      <span class="rest-tag" data-a="rest-edit" data-i="${i}">Rest ${fmtClock(x.rest)}</span>
    </div>
  </article>`;
}
function setHeaders(e) {
  if (e.kind === 'w') return `<span>${U()}</span><span>Reps</span>`;
  if (e.kind === 'bw') return `<span>+${U()}</span><span>Reps</span>`;
  if (e.kind === 't') return `<span class="span2">Seconds</span>`;
  return `<span>${U()}</span><span>Sec</span>`;
}
function setRow(e, s, i, j, label) {
  const wv = s.w != null && s.w !== '' ? fmtW(s.w) : '';
  const wIn = `<input inputmode="decimal" data-f="w" data-i="${i}" data-j="${j}" value="${wv}" placeholder="${e.kind === 'bw' ? 'BW' : '—'}" aria-label="Weight">`;
  const rIn = `<input inputmode="numeric" data-f="r" data-i="${i}" data-j="${j}" value="${s.r ?? ''}" placeholder="—" aria-label="Reps">`;
  const sIn = cls => `<input inputmode="numeric" class="${cls}" data-f="s" data-i="${i}" data-j="${j}" value="${s.s ?? ''}" placeholder="sec" aria-label="Seconds">`;
  const inputs = e.kind === 't' ? sIn('span2') : e.kind === 'tw' ? wIn + sIn('') : wIn + rIn;
  return `<div class="set ${s.done ? 'done' : ''} ${s.wu ? 'wu' : ''}">
    <span class="n" data-a="toggle-wu" data-i="${i}" data-j="${j}">${label}</span>${inputs}
    <button class="chk" data-a="toggle" data-i="${i}" data-j="${j}" aria-label="Complete set">${I.check}</button>
  </div>`;
}
function plateText(lb) {
  const unit = U();
  const total = toDisp(lb);
  const bar = unit === 'kg' ? 20 : 45;
  const plates = unit === 'kg' ? [25, 20, 15, 10, 5, 2.5, 1.25] : [45, 35, 25, 10, 5, 2.5];
  let side = (total - bar) / 2;
  if (side <= 0) return `Empty bar (${bar})`;
  const out = [];
  for (const p of plates) while (side >= p - 0.001) { out.push(p); side -= p; }
  return `<b>Per side</b> ${out.join(' · ')}${side > 0.01 ? ` <em>(+${fmtNum(side)})</em>` : ''}`;
}
let elapsedIv;
function tickElapsed() {
  clearInterval(elapsedIv);
  if (!S.plan?.start) return;
  const upd = () => { const el = $('#elapsed'); if (!el) { clearInterval(elapsedIv); return; } el.textContent = fmtClock((Date.now() - S.plan.start) / 1000); };
  upd(); elapsedIv = setInterval(upd, 1000);
}

/* ---------- welcome / onboarding ---------- */
const OB = { step: 0 };
function viewWelcome() {
  const st = S.settings;
  const steps = [
    () => `
      <div class="ob-hero">
        <div class="logo-mark"></div>
        <h1>Kiln</h1>
        <p>Your training, forged on recovery and progressive overload. Built for one lifter.</p>
      </div>
      <button class="btn primary big" data-a="ob-next">Set up</button>
      <button class="btn ghost big" data-a="ob-import">Import Fitbod history first</button>
      <p class="fine">Fitbod: Settings → Export Workout Data → save the CSV, then import here.</p>`,
    () => `
      <h2 class="ob-h">About you</h2>
      <div class="field"><label>Units</label>${seg('unit', [['lb', 'lb'], ['kg', 'kg']], st.unit)}</div>
      <div class="field"><label>Bodyweight (${U()})</label><input class="txt" inputmode="decimal" data-setting="bodyweight" value="${fmtW(st.bodyweight)}"></div>
      <div class="field"><label>Lifting experience</label>${seg('experience', [['beginner', 'New'], ['intermediate', 'Intermediate'], ['advanced', 'Advanced']], st.experience)}</div>
      <button class="btn primary big" data-a="ob-next">Continue</button>`,
    () => `
      <h2 class="ob-h">Goal</h2>
      ${optionList('goal', Object.entries(GOALS).map(([k, g]) => [k, g.label, g.sub]), st.goal)}
      <h2 class="ob-h">Split</h2>
      ${optionList('split', Object.entries(SPLITS).map(([k, g]) => [k, g.label, g.sub]), st.split)}
      <button class="btn primary big" data-a="ob-next">Continue</button>`,
    () => `
      <h2 class="ob-h">Where do you train?</h2>
      ${optionList('gym', S.gyms.map(g => [g.id, g.name, `${g.equip.length} equipment types`]), st.gym)}
      <p class="fine">Edit equipment anytime in Settings → Gyms.</p>
      <div class="field"><label>Session length</label>${seg('duration', [[30, '30'], [45, '45'], [60, '60'], [75, '75'], [90, '90']], st.duration)}</div>
      <button class="btn primary big" data-a="ob-done">Build my first workout</button>`,
  ];
  return `<div class="onboard">${OB.step > 0 ? `<div class="ob-dots">${[1, 2, 3].map(n => `<i class="${n <= OB.step ? 'on' : ''}"></i>`).join('')}</div>` : ''}${steps[OB.step]()}</div>`;
}
function seg(key, opts, cur) {
  return `<div class="seg">${opts.map(([v, l]) => `<button data-a="set" data-k="${key}" data-v="${v}" class="${String(cur) === String(v) ? 'on' : ''}">${l}</button>`).join('')}</div>`;
}
function optionList(key, opts, cur) {
  return `<div class="opts">${opts.map(([v, l, sub]) => `<button class="opt ${String(cur) === String(v) ? 'on' : ''}" data-a="set" data-k="${key}" data-v="${v}"><span><b>${esc(l)}</b><small>${esc(sub)}</small></span><i></i></button>`).join('')}</div>`;
}

/* ---------- history view ---------- */
function viewHistory() {
  const ws = S.workouts;
  if (!ws.length) return `<header class="page-head"><h1>History</h1></header><div class="empty">${I.history}<p>No workouts yet.</p><small>Finish a workout or import your Fitbod history in Settings.</small></div>`;
  let html = '<header class="page-head"><h1>History</h1></header>';
  let month = '';
  for (const w of ws.slice(0, 400)) {
    const m = fmtDate(w.start, { month: 'long', year: 'numeric' });
    if (m !== month) { month = m; html += `<h4 class="group-h">${m}</h4>`; }
    const { v, sets } = workoutVolume(w);
    const dur = w.end && w.end - w.start > 6e4 ? fmtDur(w.end - w.start) : '';
    html += `
    <button class="card row-card" data-a="workout-detail" data-v="${w.id}">
      <div class="date-badge"><b>${new Date(w.start).getDate()}</b><span>${fmtDate(w.start, { weekday: 'short' })}</span></div>
      <div class="rc-main">
        <h3>${esc(w.name)}${w.prs?.length ? ` <span class="pr-tag">${I.trophy}${w.prs.length}</span>` : ''}</h3>
        <p>${w.exercises.map(x => esc(exName(x.exId))).slice(0, 3).join(', ')}${w.exercises.length > 3 ? ` +${w.exercises.length - 3}` : ''}</p>
        <div class="rc-stats"><span>${sets} sets</span>${v ? `<span>${fmtBig(toDisp(v))} ${U()}</span>` : ''}${dur ? `<span>${dur}</span>` : ''}</div>
      </div>
      ${I.chev}
    </button>`;
  }
  if (ws.length > 400) html += `<p class="fine center">Showing latest 400 of ${ws.length}</p>`;
  return html;
}
function workoutDetail(id) {
  const w = S.workouts.find(x => x.id === id); if (!w) return;
  const { v, sets } = workoutVolume(w);
  openSheet(`
    <div class="sheet-head"><div><div class="eyebrow">${esc(fmtDate(w.start, { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' }))}</div><h2>${esc(w.name)}</h2></div></div>
    <div class="stat-row">
      <div><b>${sets}</b><span>Sets</span></div>
      <div><b>${fmtBig(toDisp(v))}</b><span>Volume ${U()}</span></div>
      <div><b>${w.end && w.end - w.start > 6e4 ? fmtDur(w.end - w.start) : '—'}</b><span>Duration</span></div>
    </div>
    ${w.exercises.map(x => {
      const e = EX[x.exId] || { kind: 'w', name: 'Unknown' };
      const pr = w.prs?.find(p => p.exId === x.exId);
      return `<div class="detail-ex"><h4 data-a="ex-detail" data-v="${x.exId}">${esc(e.name)} ${pr ? `<span class="pr-tag">${I.trophy}PR</span>` : ''}</h4>
        <div class="set-pills">${x.sets.map(s => `<span class="${s.wu ? 'wu' : ''}">${fmtSet(e, s)}</span>`).join('')}</div></div>`;
    }).join('')}
    <div class="sheet-actions">
      <button class="btn" data-a="repeat-workout" data-v="${w.id}">${I.refresh} Repeat this workout</button>
      <button class="btn" data-a="health-send" data-v="${w.id}">${w.healthSent ? 'Sent to Apple Health · send again' : 'Send to Apple Health'}</button>
      <button class="btn ghost danger" data-a="delete-workout" data-v="${w.id}">Delete</button>
    </div>`);
}
function showSummary(w) {
  const { v, sets } = workoutVolume(w);
  openSheet(`
    <div class="summary">
      <div class="logo-mark sm"></div>
      <h2>Workout complete</h2>
      <p>${esc(w.name)} · ${fmtDur(w.end - w.start)}</p>
      <div class="stat-row">
        <div><b>${sets}</b><span>Sets</span></div>
        <div><b>${fmtBig(toDisp(v))}</b><span>Volume ${U()}</span></div>
        <div><b>${w.prs.length}</b><span>PRs</span></div>
      </div>
      ${w.prs.length ? `<div class="pr-list">${w.prs.map(p => { const e = EX[p.exId]; return `<div>${I.trophy}<span>${esc(e.name)}</span><b>${fmtMetric(e, p.value)}</b></div>`; }).join('')}</div>` : ''}
      <div class="sheet-actions">
        <button class="btn" data-a="health-send" data-v="${w.id}">${S.settings.health ? 'Send to Apple Health again' : 'Send to Apple Health'}</button>
        <button class="btn primary big" data-a="close-sheet">Done</button>
      </div>
    </div>`);
}

/* ---------- progress view ---------- */
function viewProgress() {
  const now = Date.now();
  const rec = recovery();
  const weekStart = startOfWeek(now);
  const thisWeek = S.workouts.filter(w => w.start >= weekStart);
  const weeks = [];
  for (let i = 11; i >= 0; i--) {
    const ws = weekStart - i * 7 * DAY, we = ws + 7 * DAY;
    weeks.push({ ws, n: S.workouts.filter(w => w.start >= ws && w.start < we).length });
  }
  let streak = 0;
  for (let i = weeks.length - 1; i >= 0; i--) { if (weeks[i].n > 0) streak++; else if (i === weeks.length - 1) continue; else break; }
  const weekVol = thisWeek.reduce((a, w) => a + workoutVolume(w).v, 0);

  // weekly sets per muscle (rolling 7 days)
  const setsBy = {};
  for (const w of S.workouts) {
    if (now - w.start > 7 * DAY) break;
    for (const x of w.exercises) {
      const e = EX[x.exId]; if (!e || !MUSCLES[e.primary]) continue;
      const n = x.sets.filter(s => s.done && !s.wu).length;
      setsBy[e.primary] = (setsBy[e.primary] || 0) + n;
      (e.secondary || []).forEach(m => { if (MUSCLES[m]) setsBy[m] = (setsBy[m] || 0) + n * 0.5; });
    }
  }
  const maxSets = Math.max(20, ...Object.values(setsBy));

  // top lifts
  const H = hist();
  const top = Object.entries(H).filter(([id]) => EX[id])
    .sort((a, b) => b[1].length - a[1].length).slice(0, 6);

  return `
  <header class="page-head"><h1>Progress</h1></header>
  <div class="stat-row big">
    <div><b>${thisWeek.length}</b><span>This week</span></div>
    <div><b>${streak}</b><span>Week streak</span></div>
    <div><b>${fmtBig(toDisp(weekVol))}</b><span>${U()} this week</span></div>
  </div>

  <section class="card pad">
    <div class="card-h"><h3>Workouts per week</h3><span>12 weeks</span></div>
    ${barChart(weeks.map(w => ({ label: fmtDate(w.ws, { month: 'numeric', day: 'numeric' }), v: w.n })))}
  </section>

  <section class="card pad">
    <div class="card-h"><h3>Muscle recovery</h3><span>Now</span></div>
    <div class="rec-grid">
      ${Object.keys(MUSCLES).map(m => `<div class="rec-cell"><div class="ring" style="--p:${rec.r[m]};--c:${recColor(rec.r[m])}"><span>${rec.r[m]}</span></div><label>${MUSCLES[m]}</label><small>${rec.last[m] ? agoText(rec.last[m]) : '—'}</small></div>`).join('')}
    </div>
  </section>

  <section class="card pad">
    <div class="card-h"><h3>Weekly sets by muscle</h3><span>Last 7 days</span></div>
    <div class="vol-bars">
      ${Object.keys(MUSCLES).map(m => { const v = setsBy[m] || 0; return `<div class="vb"><label>${MUSCLES[m]}</label><div class="vb-track"><i class="zone" style="left:${(10 / maxSets) * 100}%;width:${(10 / maxSets) * 100}%"></i><div class="vb-fill" style="width:${(v / maxSets) * 100}%"></div></div><b>${fmtNum(v)}</b></div>`; }).join('')}
    </div>
    <p class="fine">Shaded zone is 10–20 weekly sets, the productive range for most lifters. Secondary muscles count as half a set.</p>
  </section>

  <section class="card pad">
    <div class="card-h"><h3>Bodyweight</h3><span>${S.body.length ? `${fmtW(S.body[S.body.length - 1].w)} ${U()}` : ''}</span></div>
    ${S.body.length > 1 ? lineChart(S.body.slice(-60).map(b => ({ x: b.t, y: toDisp(b.w) }))) : '<p class="fine">Log your weight a few times to see the trend.</p>'}
    <div class="inline-form"><input class="txt" id="bw-input" inputmode="decimal" placeholder="Today's weight (${U()})"><button class="btn primary" data-a="log-bw">Log</button></div>
  </section>

  ${top.length ? `
  <section class="card pad">
    <div class="card-h"><h3>Top lifts</h3><span>Most trained</span></div>
    ${top.map(([id, sess]) => {
      const e = EX[id];
      const pts = sess.slice(-20).map(h => ({ x: h.date, y: sessionBest(e, h.sets) }));
      const best = Math.max(...sess.map(h => sessionBest(e, h.sets)));
      return `<button class="lift-row" data-a="ex-detail" data-v="${id}"><div><b>${esc(e.name)}</b><small>${metricLabel(e)} · ${fmtMetric(e, best)}</small></div>${sparkline(pts)}</button>`;
    }).join('')}
  </section>` : ''}
  `;
}
function startOfWeek(t) { const d = new Date(t); d.setHours(0, 0, 0, 0); const day = (d.getDay() + 6) % 7; return d.getTime() - day * DAY; }
function agoText(t) { const h = (Date.now() - t) / 36e5; if (h < 1) return 'just now'; if (h < 24) return `${Math.round(h)}h ago`; const d = Math.round(h / 24); return d > 60 ? '60d+' : `${d}d ago`; }

/* ---------- charts ---------- */
function lineChart(pts, h = 150) {
  if (pts.length < 2) return '';
  const W = 340, H = h, pad = 22;
  const xs = pts.map(p => p.x), ys = pts.map(p => p.y);
  const x0 = Math.min(...xs), x1 = Math.max(...xs) || x0 + 1;
  let y0 = Math.min(...ys), y1 = Math.max(...ys);
  if (y1 - y0 < 1) { y0 -= 1; y1 += 1; }
  const yp = (y1 - y0) * 0.15; y0 -= yp; y1 += yp;
  const X = x => pad / 2 + ((x - x0) / (x1 - x0 || 1)) * (W - pad);
  const Y = y => H - pad - ((y - y0) / (y1 - y0)) * (H - pad * 1.6);
  const d = pts.map((p, i) => `${i ? 'L' : 'M'}${X(p.x).toFixed(1)},${Y(p.y).toFixed(1)}`).join('');
  const last = pts[pts.length - 1];
  return `<svg class="chart" viewBox="0 0 ${W} ${H}">
    <defs><linearGradient id="lg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="var(--accent)" stop-opacity=".35"/><stop offset="1" stop-color="var(--accent)" stop-opacity="0"/></linearGradient></defs>
    <path d="${d}L${X(last.x)},${H - pad}L${X(pts[0].x)},${H - pad}Z" fill="url(#lg)" stroke="none"/>
    <path d="${d}" fill="none" stroke="var(--accent)" stroke-width="2.25" stroke-linejoin="round" stroke-linecap="round"/>
    <circle cx="${X(last.x)}" cy="${Y(last.y)}" r="4" fill="var(--accent)" stroke="none"/>
    <text x="4" y="12" class="ct">${fmtNum(Math.max(...ys))}</text>
    <text x="4" y="${H - 6}" class="ct">${fmtNum(Math.min(...ys))}</text>
    <text x="${W - 4}" y="${H - 6}" class="ct" text-anchor="end">${fmtDate(last.x, { month: 'short', day: 'numeric' })}</text>
  </svg>`;
}
function sparkline(pts) {
  if (pts.length < 2) return '<svg class="spark"></svg>';
  const W = 90, H = 32;
  const ys = pts.map(p => p.y); const y0 = Math.min(...ys), y1 = Math.max(...ys) || 1;
  const d = pts.map((p, i) => `${i ? 'L' : 'M'}${((i / (pts.length - 1)) * (W - 4) + 2).toFixed(1)},${(H - 3 - ((p.y - y0) / (y1 - y0 || 1)) * (H - 6)).toFixed(1)}`).join('');
  return `<svg class="spark" viewBox="0 0 ${W} ${H}"><path d="${d}" fill="none" stroke="var(--accent)" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
}
function barChart(items) {
  const max = Math.max(1, ...items.map(i => i.v));
  return `<div class="bars">${items.map((it, k) => `<div class="bar ${k === items.length - 1 ? 'now' : ''}"><b>${it.v || ''}</b><i style="height:${(it.v / max) * 100}%"></i><span>${k % 2 === items.length % 2 ? '' : it.label}</span></div>`).join('')}</div>`;
}

/* ---------- library view ---------- */
function viewLibrary() {
  const q = norm(V.libQuery);
  const eq = new Set(activeGym().equip);
  let list = Object.values(EX).filter(e => (V.libMuscle === 'all' || (V.libMuscle === 'fav' ? S.fav[e.id] : e.primary === V.libMuscle)) && (!q || norm(e.name).includes(q)));
  list.sort((a, b) => (S.fav[b.id] ? 1 : 0) - (S.fav[a.id] ? 1 : 0) || a.name.localeCompare(b.name));
  const H = hist();
  return `
  <header class="page-head"><div class="title-row"><h1>Exercises</h1><button class="btn sm" data-a="custom-ex">${I.plus} Custom</button></div></header>
  <div class="search">${I.search}<input id="lib-q" type="search" placeholder="Search ${Object.keys(EX).length} exercises" value="${esc(V.libQuery)}"></div>
  <div class="chips scroll">
    ${[['all', 'All'], ['fav', '★ Favorites'], ...Object.entries(MUSCLES)].map(([k, l]) => `<button class="chip ${V.libMuscle === k ? 'on' : ''}" data-a="lib-muscle" data-v="${k}">${l}</button>`).join('')}
  </div>
  <div class="lib-list">
    ${list.map(e => `
      <button class="lib-item ${(e.equip || []).every(k => eq.has(k)) ? '' : 'na'} ${S.ban[e.id] ? 'banned' : ''}" data-a="ex-detail" data-v="${e.id}">
        <div class="ex-badge m-${e.primary}">${MUSCLE_ABBR[e.primary] || '··'}</div>
        <div><b>${esc(e.name)}${S.fav[e.id] ? ' <i class="fav-dot"></i>' : ''}</b><small>${MUSCLES[e.primary] || 'Other'}${(e.equip || []).length ? ' · ' + e.equip.map(k => EQUIPMENT.find(q => q[0] === k)?.[1].split(' ')[0] || k).join(', ') : ' · Bodyweight'}${H[e.id] ? ` · ${H[e.id].length}×` : ''}${S.ban[e.id] ? ' · Hidden' : ''}</small></div>
        ${I.chev}
      </button>`).join('') || '<div class="empty"><p>No matches.</p></div>'}
  </div>`;
}
function exerciseDetail(id, opts = {}) {
  const e = EX[id]; if (!e) return;
  const H = hist()[id] || [];
  const best = H.length ? Math.max(...H.map(h => sessionBest(e, h.sets))) : 0;
  let bestSet = null;
  for (const h of H) for (const s of h.sets) if (!bestSet || metric(e, s) > metric(e, bestSet)) bestSet = s;
  const pts = H.slice(-40).map(h => ({ x: h.date, y: sessionBest(e, h.sets) }));
  const rec = recommend(e, scheme(e));
  openSheet(`
    <div class="sheet-head">
      <div><div class="eyebrow">${MUSCLES[e.primary] || 'Other'}${e.custom ? ' · Custom' : ''}</div><h2>${esc(e.name)}</h2></div>
      <button class="icon-btn ${S.fav[id] ? 'starred' : ''}" data-a="fav" data-v="${id}" aria-label="Favorite">${I.star}</button>
    </div>
    <div class="tags">
      ${(e.secondary || []).map(m => `<span>${MUSCLES[m] || m}</span>`).join('')}
      ${(e.equip || []).map(k => `<span class="eq">${EQUIPMENT.find(q => q[0] === k)?.[1] || k}</span>`).join('') || '<span class="eq">Bodyweight</span>'}
      <span class="eq">${e.compound ? 'Compound' : 'Isolation'}</span>
    </div>
    <div class="stat-row">
      <div><b>${best ? fmtMetric(e, best) : '—'}</b><span>${metricLabel(e)}</span></div>
      <div><b>${bestSet ? fmtSet(e, bestSet) : '—'}</b><span>Best set</span></div>
      <div><b>${H.length}</b><span>Sessions</span></div>
    </div>
    ${pts.length > 1 ? `<div class="card-h"><h3>${metricLabel(e)} trend</h3></div>${lineChart(pts)}` : ''}
    <div class="next-up"><span>Next time</span><b>${e.kind === 'w' || e.kind === 'tw' ? (rec.w ? fmtW(rec.w) + ' ' + U() : 'Find weight') + ' · ' : ''}${rec.r ? rec.r + ' reps' : fmtClock(rec.s || 30)}</b><small>${esc(rec.note)}</small></div>
    ${H.length ? `<div class="card-h"><h3>Recent sessions</h3></div>
      ${H.slice(-8).reverse().map(h => `<div class="sess"><span>${fmtDate(h.date, { month: 'short', day: 'numeric', year: '2-digit' })}</span><div class="set-pills">${h.sets.map(s => `<span>${fmtSet(e, s)}</span>`).join('')}</div></div>`).join('')}` : ''}
    <div class="sheet-actions">
      ${opts.pick ? '' : `<button class="btn primary" data-a="add-this" data-v="${id}">${I.plus} Add to workout</button>`}
      <a class="btn" href="https://www.youtube.com/results?search_query=${encodeURIComponent(e.name + ' proper form')}" target="_blank" rel="noopener">${I.play} Form video</a>
      <button class="btn ghost ${S.ban[id] ? '' : 'danger'}" data-a="ban" data-v="${id}">${S.ban[id] ? 'Allow in workouts' : 'Never recommend'}</button>
      ${e.custom ? `<button class="btn ghost danger" data-a="del-custom" data-v="${id}">Delete custom exercise</button>` : ''}
    </div>`);
}

/* ---------- settings view ---------- */
function viewSettings() {
  const st = S.settings;
  const g = activeGym();
  return `
  <header class="page-head"><h1>Settings</h1></header>

  <h4 class="group-h">Training</h4>
  <section class="card pad form">
    <div class="field"><label>Goal</label>${optionList('goal', Object.entries(GOALS).map(([k, x]) => [k, x.label, x.sub]), st.goal)}</div>
    <div class="field"><label>Split</label>${optionList('split', Object.entries(SPLITS).map(([k, x]) => [k, x.label, x.sub]), st.split)}</div>
    <div class="field"><label>Session length (min)</label>${seg('duration', [[30, '30'], [45, '45'], [60, '60'], [75, '75'], [90, '90']], st.duration)}</div>
    <div class="field"><label>Experience</label>${seg('experience', [['beginner', 'New'], ['intermediate', 'Intermediate'], ['advanced', 'Advanced']], st.experience)}</div>
    ${toggle('core', 'Add a core finisher', st.core)}
    ${toggle('warmups', 'Warm-up sets on first lift', st.warmups)}
    <div class="toggle-row static"><span>Deload</span><small>${deloadActive() ? 'Active now' : `${deloadInfo().weeks || 0} of ${DELOAD_WEEKS} training weeks`}</small></div>
    ${deloadActive() ? '<button class="btn block" data-a="deload-end">End deload week</button>' : '<button class="btn block" data-a="deload-start">Start a deload week now</button>'}
  </section>

  <h4 class="group-h">Gyms</h4>
  <section class="card pad form">
    ${optionList('gym', S.gyms.map(x => [x.id, x.name, `${x.equip.length} equipment types`]), st.gym)}
    <div class="field"><label>Equipment at ${esc(g.name)}</label>
      <div class="equip-grid">${EQUIPMENT.map(([k, l]) => `<button class="eq-tog ${g.equip.includes(k) ? 'on' : ''}" data-a="equip" data-v="${k}">${l}</button>`).join('')}</div>
    </div>
    <div class="btn-row"><button class="btn sm" data-a="gym-rename">Rename</button><button class="btn sm" data-a="gym-add">${I.plus} New gym</button>${S.gyms.length > 1 ? `<button class="btn sm ghost danger" data-a="gym-del">Delete</button>` : ''}</div>
  </section>

  <h4 class="group-h">Body & units</h4>
  <section class="card pad form">
    <div class="field"><label>Units</label>${seg('unit', [['lb', 'lb'], ['kg', 'kg']], st.unit)}</div>
    <div class="field"><label>Bodyweight (${U()})</label><input class="txt" inputmode="decimal" data-setting="bodyweight" value="${fmtW(st.bodyweight)}"></div>
    <div class="field three">
      <div><label>Barbell jump</label><input class="txt" inputmode="decimal" data-setting="incBar" value="${st.incBar}"></div>
      <div><label>Dumbbell jump</label><input class="txt" inputmode="decimal" data-setting="incDb" value="${st.incDb}"></div>
      <div><label>Machine jump</label><input class="txt" inputmode="decimal" data-setting="incMachine" value="${st.incMachine}"></div>
    </div>
  </section>

  <h4 class="group-h">During workouts</h4>
  <section class="card pad form">
    ${toggle('sound', 'Rest timer chime', st.sound)}
    ${toggle('wake', 'Keep screen awake', st.wake)}
  </section>

  <h4 class="group-h">Apple Health</h4>
  <section class="card pad form">
    ${toggle('health', 'Send finished workouts to Health', st.health)}
    ${toggle('healthWeight', 'Send logged bodyweight too', st.healthWeight)}
    <div class="field"><label>Shortcut name</label><input class="txt" data-setting-str="healthShortcut" value="${esc(st.healthShortcut)}"></div>
    <button class="btn block" data-a="health-guide">Set up the shortcut (2 min)</button>
  </section>

  <h4 class="group-h">Data</h4>
  <section class="card pad form">
    <p class="fine">${S.workouts.length} workouts · ${S.custom.length} custom exercises · stored on this device only.</p>
    <button class="btn block" data-a="import-file" data-v="csv">Import Fitbod / Strong / Hevy CSV</button>
    <button class="btn block" data-a="export-json">Export full backup (.json)</button>
    <button class="btn block" data-a="import-file" data-v="json">Restore from backup</button>
    <button class="btn block" data-a="export-csv">Export workouts (.csv)</button>
    <button class="btn block ghost danger" data-a="reset">Erase everything</button>
  </section>
  <p class="fine center">Kiln v1 · Back up monthly. iOS can clear web app data if storage gets tight.</p>
  <input type="file" id="file-in" accept=".csv,.json,text/csv,application/json" hidden>
  `;
}
function toggle(key, label, on) {
  return `<button class="toggle-row" data-a="toggle-setting" data-k="${key}"><span>${label}</span><i class="sw ${on ? 'on' : ''}"></i></button>`;
}

/* ---------- sheets ---------- */
function openSheet(html) {
  const sh = $('#sheet'), sc = $('#scrim');
  sh.innerHTML = `<div class="grab"></div><button class="sheet-x" data-a="close-sheet" aria-label="Close">${I.x}</button><div class="sheet-body">${html}</div>`;
  sh.hidden = false; sc.hidden = false;
  requestAnimationFrame(() => { sh.classList.add('open'); sc.classList.add('open'); });
  document.body.classList.add('locked');
}
function closeSheet() {
  const sh = $('#sheet'), sc = $('#scrim');
  sh.classList.remove('open'); sc.classList.remove('open');
  document.body.classList.remove('locked');
  setTimeout(() => { if (!sh.classList.contains('open')) { sh.hidden = true; sc.hidden = true; sh.innerHTML = ''; } }, 260);
  V.sheet = null;
}
function exMenu(i) {
  const x = S.plan.exercises[i]; const e = EX[x.exId];
  openSheet(`
    <div class="sheet-head"><div><div class="eyebrow">${MUSCLES[e.primary] || ''}</div><h2>${esc(e.name)}</h2></div></div>
    <div class="menu">
      <button data-a="swap" data-i="${i}">${I.swap}<span>Swap exercise</span></button>
      <button data-a="ex-detail" data-v="${e.id}">${I.chart}<span>History & details</span></button>
      <button data-a="move" data-i="${i}" data-v="-1" ${i === 0 ? 'disabled' : ''}>${I.up}<span>Move up</span></button>
      <button data-a="move" data-i="${i}" data-v="1" ${i === S.plan.exercises.length - 1 ? 'disabled' : ''}>${I.down}<span>Move down</span></button>
      <button data-a="fav" data-v="${e.id}">${I.star}<span>${S.fav[e.id] ? 'Remove from favorites' : 'Favorite (recommend more)'}</span></button>
      <button data-a="ban-swap" data-i="${i}">${I.x}<span>Never recommend, swap now</span></button>
      <button data-a="remove-ex" data-i="${i}" class="danger">${I.minus}<span>Remove from workout</span></button>
    </div>`);
}
function swapSheet(i, query = '') {
  const x = S.plan.exercises[i]; const cur = EX[x.exId];
  const inPlan = new Set(S.plan.exercises.map(y => y.exId));
  const avail = availableExercises().filter(e => !inPlan.has(e.id));
  const H = hist();
  const same = avail.filter(e => e.primary === cur.primary)
    .sort((a, b) => (S.fav[b.id] ? 2 : 0) + (H[b.id] ? 1 : 0) + (b.compound === cur.compound ? 1 : 0) - ((S.fav[a.id] ? 2 : 0) + (H[a.id] ? 1 : 0) + (a.compound === cur.compound ? 1 : 0)));
  V.sheet = { type: 'swap', i };
  openSheet(`
    <div class="sheet-head"><div><div class="eyebrow">Swap</div><h2>${esc(cur.name)}</h2></div></div>
    <div class="search">${I.search}<input id="pick-q" type="search" placeholder="Search all exercises" value="${esc(query)}"></div>
    <div id="pick-list" class="lib-list">${pickList(query ? avail : same, query)}</div>`);
}
function addSheet(query = '') {
  V.sheet = { type: 'add' };
  openSheet(`
    <div class="sheet-head"><div><div class="eyebrow">Add to workout</div><h2>Choose exercise</h2></div></div>
    <div class="search">${I.search}<input id="pick-q" type="search" placeholder="Search" value="${esc(query)}"></div>
    <div id="pick-list" class="lib-list">${pickList(availableExercises(), query)}</div>`);
}
function pickList(list, query) {
  const q = norm(query);
  const H = hist();
  const out = list.filter(e => !q || norm(e.name).includes(q))
    .sort((a, b) => (q ? 0 : ((S.fav[b.id] ? 2 : 0) + (H[b.id] ? 1 : 0)) - ((S.fav[a.id] ? 2 : 0) + (H[a.id] ? 1 : 0))) || a.name.localeCompare(b.name))
    .slice(0, 80);
  return out.map(e => `<button class="lib-item" data-a="pick" data-v="${e.id}"><div class="ex-badge m-${e.primary}">${MUSCLE_ABBR[e.primary] || '··'}</div><div><b>${esc(e.name)}${S.fav[e.id] ? ' <i class="fav-dot"></i>' : ''}</b><small>${MUSCLES[e.primary] || ''}${H[e.id] ? ` · done ${H[e.id].length}×` : ''}</small></div>${I.plus}</button>`).join('') || '<div class="empty"><p>Nothing matches with this gym\'s equipment.</p></div>';
}
function pickExercise(id) {
  const e = EX[id]; if (!e || !S.plan) return;
  if (V.sheet?.type === 'swap') {
    const old = S.plan.exercises[V.sheet.i];
    const entry = buildEntry(e, V.sheet.i === 0 && !old.sets.some(s => s.done));
    const n = old.sets.filter(s => !s.wu).length;
    const working = entry.sets.filter(s => !s.wu);
    while (working.length < n) working.push({ ...working[0] });
    entry.sets = [...entry.sets.filter(s => s.wu), ...working.slice(0, Math.max(n, 1))];
    S.plan.exercises[V.sheet.i] = entry;
    toast(`Swapped in ${e.name}`);
  } else {
    S.plan.exercises.push(buildEntry(e, false));
    toast(`Added ${e.name}`);
  }
  save(); closeSheet(); render();
}
function customExerciseSheet() {
  openSheet(`
    <div class="sheet-head"><div><div class="eyebrow">New</div><h2>Custom exercise</h2></div></div>
    <div class="form">
      <div class="field"><label>Name</label><input class="txt" id="cx-name" placeholder="e.g. Landmine Press"></div>
      <div class="field"><label>Primary muscle</label><select class="txt" id="cx-muscle">${Object.entries(MUSCLES).map(([k, l]) => `<option value="${k}">${l}</option>`).join('')}</select></div>
      <div class="field"><label>Tracking</label><select class="txt" id="cx-kind"><option value="w">Weight × reps</option><option value="bw">Bodyweight reps</option><option value="t">Time</option><option value="tw">Weight × time</option></select></div>
      <div class="field"><label>Equipment needed</label><div class="equip-grid">${EQUIPMENT.map(([k, l]) => `<button class="eq-tog" data-a="cx-eq" data-v="${k}">${l}</button>`).join('')}</div></div>
      ${toggle('cx-compound', 'Compound (multi-joint) movement', false).replace('toggle-setting', 'cx-compound')}
      <button class="btn primary big" data-a="cx-save">Save exercise</button>
    </div>`);
}

/* ---------- import / export ---------- */
function parseCSV(text) {
  const rows = []; let row = [], f = '', q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) {
      if (c === '"') { if (text[i + 1] === '"') { f += '"'; i++; } else q = false; }
      else f += c;
    } else if (c === '"') q = true;
    else if (c === ',') { row.push(f); f = ''; }
    else if (c === '\n' || c === '\r') { if (c === '\r' && text[i + 1] === '\n') i++; row.push(f); rows.push(row); row = []; f = ''; }
    else f += c;
  }
  if (f || row.length) { row.push(f); rows.push(row); }
  return rows.filter(r => r.some(x => x.trim() !== ''));
}
function parseDate(s) {
  s = String(s).trim();
  let t = Date.parse(s.replace(' ', 'T').replace(/ ?([+-]\d{2}):?(\d{2})$/, '$1:$2'));
  if (isNaN(t)) t = Date.parse(s);
  if (isNaN(t)) t = Date.parse(s.replace(/ [A-Z]{2,4}$/, ''));
  return t;
}
function guessMuscle(name) {
  const n = ' ' + name.toLowerCase() + ' ';
  const R = [
    [/calf|calves/, 'calves'], [/leg curl|hamstring|nordic/, 'hamstrings'], [/leg extension/, 'quads'],
    [/tricep|skull|pushdown|kickback| dip/, 'triceps'], [/shrug/, 'traps'], [/rear delt|reverse fly|face pull|pull apart/, 'upperback'],
    [/lateral raise|shoulder|overhead press|military|arnold|delt|front raise|upright/, 'shoulders'],
    [/bench|chest|fly|flye|push ?up|pec|crossover/, 'chest'], [/pulldown|pull ?up|chin ?up|lat /, 'lats'],
    [/row/, 'upperback'], [/curl/, 'biceps'], [/hip thrust|glute|bridge|abduct|kickback|swing/, 'glutes'],
    [/deadlift|rdl|good morning/, 'hamstrings'], [/squat|lunge|leg press|step ?up|split/, 'quads'],
    [/crunch|plank|sit ?up| ab|leg raise|twist|rotation|core|knee raise|woodchop|pallof/, 'abs'],
    [/back extension|hyperextension|superman/, 'lowerback'], [/wrist|farmer|grip|hang/, 'forearms'],
  ];
  for (const [re, m] of R) if (re.test(n)) return m;
  return 'other';
}
function guessEquip(name) {
  const n = name.toLowerCase(); const out = [];
  if (/barbell|bench press|deadlift|squat/.test(n) && !/dumbbell|smith|goblet|machine|bodyweight/.test(n)) out.push('barbell');
  if (/dumbbell|db /.test(n)) out.push('dumbbell');
  if (/cable|rope|pulldown/.test(n)) out.push('cable');
  if (/machine/.test(n)) out.push('machine');
  if (/kettlebell/.test(n)) out.push('kettlebell');
  if (/smith/.test(n)) out.push('smith');
  if (/ez/.test(n)) out.push('ez');
  return out;
}
function matchExercise(name, sample) {
  const key = norm(name);
  for (const e of Object.values(EX)) if (norm(e.name) === key) return e.id;
  for (const [alias, id] of Object.entries(ALIASES)) if (norm(alias) === key) return id;
  const kind = sample.s && !sample.r ? (sample.w ? 'tw' : 't') : sample.w ? 'w' : 'bw';
  const muscle = guessMuscle(name);
  const ex = { id: 'c_' + uid(), name: String(name).trim(), primary: muscle, secondary: [], equip: guessEquip(name), kind, compound: /press|squat|deadlift|row|pull ?up|chin|lunge|dip/.test(name.toLowerCase()), ratio: 0 };
  S.custom.push(ex); EX[ex.id] = { ...ex, custom: true };
  return ex.id;
}
function importCSV(text) {
  const rows = parseCSV(text);
  if (rows.length < 2) throw new Error('File is empty');
  const hdr = rows[0].map(h => h.trim().toLowerCase().replace(/^﻿/, ''));
  const col = (...res) => { for (const re of res) { const i = hdr.findIndex(h => re.test(h)); if (i >= 0) return i; } return -1; };
  const cDate = col(/^date$/, /^start_time$/, /date/, /start/);
  const cEx = col(/^exercise$/, /exercise_title/, /exercise name/, /exercise/);
  const cReps = col(/^reps$/, /reps/);
  const cW = col(/^weight\(kg\)$/, /weight_kg/, /weight_lbs/, /^weight/, /weight/);
  const cDur = col(/duration\(s\)/, /duration_seconds/, /^seconds$/);
  const cWarm = col(/warm/, /set_type/);
  const cName = col(/workout name/, /^title$/);
  if (cDate < 0 || cEx < 0) throw new Error('Could not find Date and Exercise columns');
  const wKg = cW >= 0 && /kg/.test(hdr[cW]);
  const parsed = [];
  for (let i = 1; i < rows.length; i++) {
    const r = rows[i];
    const t = parseDate(r[cDate]); const name = (r[cEx] || '').trim();
    if (isNaN(t) || !name) continue;
    let w = cW >= 0 ? parseFloat(r[cW]) || 0 : 0;
    if (w && wKg) w = Math.round(w * KG * 2) / 2;
    else if (w && !wKg && U() === 'kg') w = w * KG;
    const reps = cReps >= 0 ? parseInt(r[cReps], 10) || 0 : 0;
    const sec = cDur >= 0 ? parseFloat(r[cDur]) || 0 : 0;
    const wu = cWarm >= 0 && /true|1|warm/i.test(r[cWarm] || '');
    parsed.push({ t, i, name, w, r: reps, s: sec, wu, wname: cName >= 0 ? r[cName] : '' });
  }
  if (!parsed.length) throw new Error('No rows with a valid date and exercise');
  parsed.sort((a, b) => a.t - b.t || a.i - b.i);
  // group rows into workouts: new workout when the gap exceeds 3h
  const groups = []; let g = null;
  for (const p of parsed) {
    if (!g || p.t - g.last > 3 * 36e5) { g = { start: p.t, last: p.t, rows: [] }; groups.push(g); }
    g.last = p.t; g.rows.push(p);
  }
  const existing = new Set(S.workouts.map(w => w.importKey).filter(Boolean));
  let added = 0, sets = 0;
  const idCache = {};
  for (const gr of groups) {
    const key = 'imp:' + gr.start;
    if (existing.has(key)) continue;
    const exMap = new Map();
    for (const p of gr.rows) {
      const id = idCache[p.name] || (idCache[p.name] = matchExercise(p.name, p));
      if (!exMap.has(id)) exMap.set(id, []);
      exMap.get(id).push({ w: p.w || null, r: p.r || null, s: p.s || null, wu: p.wu, done: true });
      sets++;
    }
    const exercises = [...exMap].map(([exId, s]) => ({ exId, sets: s, note: '' }));
    const name = gr.rows[0].wname || inferName(exercises);
    S.workouts.push({ id: uid(), importKey: key, name, focus: inferFocus(exercises), start: gr.start, end: gr.last > gr.start ? gr.last : gr.start, exercises, prs: [] });
    added++;
  }
  S.workouts.sort((a, b) => b.start - a.start);
  touch(); saveNow();
  return { added, sets, skipped: groups.length - added };
}
function inferFocus(exs) {
  const cnt = { push: 0, pull: 0, legs: 0 };
  for (const x of exs) {
    const m = EX[x.exId]?.primary;
    if (['chest', 'shoulders', 'triceps'].includes(m)) cnt.push++;
    else if (['lats', 'upperback', 'biceps', 'traps', 'forearms'].includes(m)) cnt.pull++;
    else if (['quads', 'hamstrings', 'glutes', 'calves'].includes(m)) cnt.legs++;
  }
  const tot = cnt.push + cnt.pull + cnt.legs || 1;
  const top = Object.entries(cnt).sort((a, b) => b[1] - a[1])[0];
  if (top[1] / tot >= 0.6) return top[0];
  if ((cnt.push + cnt.pull) / tot >= 0.8) return 'upper';
  return 'full';
}
const inferName = exs => FOCUS[inferFocus(exs)];
function download(name, text, type) {
  const file = new File([text], name, { type });
  if (navigator.canShare && navigator.canShare({ files: [file] }) && /iPhone|iPad|Android/i.test(navigator.userAgent)) {
    navigator.share({ files: [file], title: name }).catch(() => {});
    return;
  }
  const a = document.createElement('a');
  a.href = URL.createObjectURL(file); a.download = name;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 2000);
}
function exportCSV() {
  const lines = ['Date,Workout,Exercise,Set,Weight(' + U() + '),Reps,Seconds,Warmup'];
  const q = s => `"${String(s).replace(/"/g, '""')}"`;
  for (const w of [...S.workouts].reverse()) {
    const d = new Date(w.start).toISOString();
    for (const x of w.exercises) x.sets.forEach((s, i) => lines.push([d, q(w.name), q(exName(x.exId)), i + 1, s.w ? fmtW(s.w) : '', s.r ?? '', s.s ?? '', s.wu ? 'true' : 'false'].join(',')));
  }
  download(`kiln-workouts-${dayKey()}.csv`, lines.join('\n'), 'text/csv');
}

/* ---------- Apple Health (via the Shortcuts app) ---------- */
// Web apps can't write to HealthKit, so Kiln hands a JSON payload to a user-built shortcut.
function shortcutURL(payload) {
  return `shortcuts://run-shortcut?name=${encodeURIComponent(S.settings.healthShortcut || 'Kiln to Health')}&input=text&text=${encodeURIComponent(JSON.stringify(payload))}`;
}
const pad2 = n => String(n).padStart(2, '0');
function localStamp(t) { const d = new Date(t); return `${d.getFullYear()}-${pad2(d.getMonth() + 1)}-${pad2(d.getDate())} ${pad2(d.getHours())}:${pad2(d.getMinutes())}`; }
function workoutCalories(w) {
  // MET estimate: ~5 for working sets with rest, ~3.5 for a deload session
  const hrs = Math.max(0.1, (w.end - w.start) / 36e5);
  return Math.round((w.deload ? 3.5 : 5) * ((S.settings.bodyweight || 180) / KG) * hrs);
}
function sendWorkoutToHealth(w) {
  const minutes = Math.max(1, Math.round((w.end - w.start) / 6e4));
  w.healthSent = true; saveNow();
  location.href = shortcutURL({ type: 'workout', name: w.name, start: localStamp(w.start), end: localStamp(w.end), minutes, calories: workoutCalories(w) });
}
function sendWeightToHealth(lb) {
  location.href = shortcutURL({ type: 'weight', lb: Math.round(lb * 10) / 10, kg: Math.round((lb / KG) * 10) / 10 });
}
function healthGuide() {
  const name = esc(S.settings.healthShortcut || 'Kiln to Health');
  openSheet(`
    <div class="sheet-head"><div><div class="eyebrow">Apple Health</div><h2>Build the shortcut</h2></div></div>
    <p class="fine">One-time setup in the Shortcuts app. Kiln sends each finished workout to it, and the shortcut logs it to Health.</p>
    <ol class="steps">
      <li>Open <b>Shortcuts</b>, tap <b>+</b>, and name it exactly <b>${name}</b>.</li>
      <li>Add <b>Get Dictionary from Input</b> (input: Shortcut Input).</li>
      <li>Add <b>Get Dictionary Value</b>: key <code>type</code>.</li>
      <li>Add <b>If</b>: Dictionary Value <b>is</b> <code>workout</code>.</li>
      <li>Inside the If, add <b>Get Dictionary Value</b> for <code>start</code>, then <b>Get Dates from Input</b>. Add two more Get Dictionary Value actions for <code>minutes</code> and <code>calories</code>.</li>
      <li>Add <b>Log Workout</b>: type <b>Traditional Strength Training</b>, start date = Dates, duration = <code>minutes</code> minutes, energy = <code>calories</code> kcal.</li>
      <li>In the <b>Otherwise</b> branch, add <b>Get Dictionary Value</b> <code>lb</code>, then <b>Log Health Sample</b>: Weight, value = Dictionary Value, unit lb.</li>
      <li>Tap the shortcut's settings (ⓘ) and make sure it receives <b>Text</b>. Run it once from Kiln and allow Health access when asked.</li>
    </ol>
    <p class="fine">After it runs, tap ◀ Kiln in the top-left corner to come back. If nothing shows up in Health, check Health → Sharing → Apps → Shortcuts and turn on write access for Workouts and Weight.</p>
    <div class="sheet-actions">
      <button class="btn primary" data-a="health-test">Send a test workout</button>
    </div>`);
}

/* ---------- toast ---------- */
let toastT;
function toast(msg) {
  const el = $('#toast'); el.textContent = msg; el.classList.add('show');
  clearTimeout(toastT); toastT = setTimeout(() => el.classList.remove('show'), 2400);
}

/* ---------- events ---------- */
const A = {
  tab(b) { V.tab = b.dataset.v; render(); window.scrollTo(0, 0); },
  set(b) {
    const k = b.dataset.k; let v = b.dataset.v;
    if (k === 'duration') v = +v;
    if (k === 'gym') { S.settings.gym = v; } else S.settings[k] = v;
    if (['goal', 'split', 'duration', 'gym', 'experience'].includes(k) && S.onboarded && S.plan && !S.plan.start) generate();
    if (b.closest('#sheet')) closeSheet();
    save(); render();
  },
  'toggle-setting'(b) {
    const k = b.dataset.k; S.settings[k] = !S.settings[k];
    if (k === 'core' && S.plan && !S.plan.start) generate();
    save(); render();
    if (k === 'health' && S.settings.health) healthGuide();
  },
  'ob-next'() { OB.step++; render(); window.scrollTo(0, 0); },
  'ob-done'() { S.onboarded = true; generate(); render(); window.scrollTo(0, 0); },
  'ob-import'() { pickFile('csv'); },
  start() { startWorkout(); render(); },
  finish() {
    const p = S.plan; const undone = p.exercises.reduce((a, x) => a + x.sets.filter(s => !s.done && !s.wu).length, 0);
    if (undone && !confirm(`${undone} sets not checked off. Finish anyway? Unchecked sets won't be saved.`)) return;
    finishWorkout();
  },
  discard() { discardWorkout(); },
  regen() { S.seed++; generate(S.plan?.focus); render(); toast('New workout generated'); },
  toggle(b) {
    const { i, j } = b.dataset; const x = S.plan.exercises[+i]; const s = x.sets[+j];
    const e = EX[x.exId];
    s.done = !s.done;
    if (s.done) {
      if (!S.plan.start) startWorkout();
      if (e.kind === 'w' && (s.w == null || s.w === '')) { s.done = false; toast('Enter a weight first'); return; }
      if (!s.wu) timer.start(x.rest);
      else timer.start(Math.min(60, x.rest));
      if (navigator.vibrate) navigator.vibrate(15);
    }
    save(); render();
  },
  'toggle-wu'(b) { const s = S.plan.exercises[+b.dataset.i].sets[+b.dataset.j]; s.wu = !s.wu; save(); render(); },
  'add-set'(b) {
    const x = S.plan.exercises[+b.dataset.i];
    const last = [...x.sets].reverse().find(s => !s.wu) || x.sets[x.sets.length - 1] || { w: null, r: 8, s: null };
    x.sets.push({ w: last.w, r: last.r, s: last.s, done: false }); save(); render();
  },
  'rm-set'(b) {
    const x = S.plan.exercises[+b.dataset.i];
    const idx = x.sets.map(s => !s.done).lastIndexOf(true);
    if (idx >= 0) x.sets.splice(idx, 1); else x.sets.pop();
    save(); render();
  },
  'rest-edit'(b) {
    const x = S.plan.exercises[+b.dataset.i];
    const opts = [30, 45, 60, 75, 90, 120, 150, 180, 240];
    x.rest = opts[(opts.indexOf(x.rest) + 1) % opts.length] || 90; save(); render();
  },
  'ex-menu'(b) { exMenu(+b.dataset.i); },
  'ex-detail'(b) { exerciseDetail(b.dataset.v); },
  swap(b) { swapSheet(+b.dataset.i); },
  'ban-swap'(b) { const i = +b.dataset.i; S.ban[S.plan.exercises[i].exId] = true; save(); swapSheet(i); },
  move(b) {
    const i = +b.dataset.i, d = +b.dataset.v, arr = S.plan.exercises;
    if (i + d < 0 || i + d >= arr.length) return;
    [arr[i], arr[i + d]] = [arr[i + d], arr[i]]; save(); closeSheet(); render();
  },
  'remove-ex'(b) { S.plan.exercises.splice(+b.dataset.i, 1); save(); closeSheet(); render(); },
  'add-ex'() { addSheet(); },
  'add-this'(b) {
    if (!S.plan) generate();
    S.plan.exercises.push(buildEntry(EX[b.dataset.v], false)); save(); closeSheet();
    V.tab = 'workout'; render(); toast(`Added ${exName(b.dataset.v)}`);
    setTimeout(() => $(`#ex-${S.plan.exercises.length - 1}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' }), 50);
  },
  pick(b) { pickExercise(b.dataset.v); },
  fav(b) { const id = b.dataset.v; if (S.fav[id]) delete S.fav[id]; else S.fav[id] = true; save(); b.classList.toggle('starred', !!S.fav[id]); render(); toast(S.fav[id] ? 'Favorited. Kiln will program it more' : 'Removed from favorites'); },
  ban(b) { const id = b.dataset.v; if (S.ban[id]) delete S.ban[id]; else S.ban[id] = true; save(); closeSheet(); render(); toast(S.ban[id] ? 'Hidden from generated workouts' : 'Allowed again'); },
  'del-custom'(b) {
    const id = b.dataset.v;
    if (hist()[id] && !confirm('This exercise has logged history. Delete anyway? History entries will show as Unknown.')) return;
    S.custom = S.custom.filter(e => e.id !== id); rebuildEx(); touch(); closeSheet(); render();
  },
  'pick-focus'() {
    const rec = recovery();
    openSheet(`<div class="sheet-head"><div><div class="eyebrow">Today's focus</div><h2>What are we training?</h2></div></div>
      <div class="opts">${Object.keys(TEMPLATES).map(f => { const ms = focusMuscles(f); const avg = Math.round(ms.reduce((a, m) => a + rec.r[m], 0) / ms.length); return `<button class="opt ${S.plan.focus === f ? 'on' : ''}" data-a="focus" data-v="${f}"><span><b>${FOCUS[f]}</b><small>${ms.map(m => MUSCLES[m]).join(', ')}</small></span><em style="color:${recColor(avg)}">${avg}%</em></button>`; }).join('')}</div>`);
  },
  focus(b) { generate(b.dataset.v); closeSheet(); render(); },
  'pick-gym'() {
    openSheet(`<div class="sheet-head"><div><div class="eyebrow">Equipment</div><h2>Where are you training?</h2></div></div>${optionList('gym', S.gyms.map(g => [g.id, g.name, `${g.equip.length} equipment types`]), S.settings.gym)}<p class="fine">Edit equipment in Settings → Gyms.</p>`);
  },
  'pick-duration'() {
    openSheet(`<div class="sheet-head"><div><div class="eyebrow">Session length</div><h2>How much time?</h2></div></div>${optionList('duration', Object.entries(DURATION_EXERCISES).map(([m, n]) => [m, `${m} minutes`, `${n} exercises`]), S.settings.duration)}`);
  },
  'close-sheet'() { closeSheet(); },
  'workout-detail'(b) { workoutDetail(b.dataset.v); },
  'delete-workout'(b) {
    if (!confirm('Delete this workout permanently?')) return;
    S.workouts = S.workouts.filter(w => w.id !== b.dataset.v); touch(); closeSheet(); render();
  },
  'repeat-workout'(b) {
    const w = S.workouts.find(x => x.id === b.dataset.v); if (!w) return;
    if (S.plan?.start && !confirm('Replace the workout in progress?')) return;
    S.plan = { id: uid(), focus: w.focus || 'custom', gym: activeGym().id, day: dayKey(), created: Date.now(), start: null,
      exercises: w.exercises.filter(x => EX[x.exId]).map((x, i) => {
        const ent = buildEntry(EX[x.exId], i === 0);
        const n = x.sets.filter(s => !s.wu).length || 3;
        const wk = ent.sets.filter(s => !s.wu);
        while (wk.length < n) wk.push({ ...wk[0] });
        ent.sets = [...ent.sets.filter(s => s.wu), ...wk.slice(0, n)];
        return ent;
      }) };
    save(); closeSheet(); V.tab = 'workout'; render(); window.scrollTo(0, 0); toast('Loaded with fresh targets');
  },
  'lib-muscle'(b) { V.libMuscle = b.dataset.v; render(); },
  'custom-ex'() { customExerciseSheet(); },
  'cx-eq'(b) { b.classList.toggle('on'); },
  'cx-compound'(b) { b.querySelector('.sw').classList.toggle('on'); },
  'cx-save'() {
    const name = $('#cx-name').value.trim(); if (!name) { toast('Name it first'); return; }
    const ex = { id: 'c_' + uid(), name, primary: $('#cx-muscle').value, secondary: [], kind: $('#cx-kind').value,
      equip: [...document.querySelectorAll('#sheet .eq-tog.on')].map(x => x.dataset.v),
      compound: !!$('#sheet .toggle-row .sw.on'), ratio: 0 };
    S.custom.push(ex); rebuildEx(); save(); closeSheet(); render(); toast(`Created ${name}`);
  },
  equip(b) {
    const g = activeGym(); const k = b.dataset.v;
    g.equip = g.equip.includes(k) ? g.equip.filter(x => x !== k) : [...g.equip, k];
    if (S.plan && !S.plan.start) generate();
    save(); render();
  },
  'gym-add'() {
    const name = prompt('Gym name', 'Hotel Gym'); if (!name) return;
    const g = { id: uid(), name, equip: ['dumbbell', 'bench'] }; S.gyms.push(g); S.settings.gym = g.id;
    if (S.plan && !S.plan.start) generate(); save(); render();
  },
  'gym-rename'() { const g = activeGym(); const n = prompt('Rename gym', g.name); if (n) { g.name = n; save(); render(); } },
  'gym-del'() {
    const g = activeGym(); if (!confirm(`Delete ${g.name}?`)) return;
    S.gyms = S.gyms.filter(x => x !== g); S.settings.gym = S.gyms[0].id;
    if (S.plan && !S.plan.start) generate(); save(); render();
  },
  'log-bw'() {
    const v = parseFloat($('#bw-input').value); if (!v) return;
    const lb = fromDisp(v); const today = dayKey();
    S.body = S.body.filter(b => dayKey(b.t) !== today); S.body.push({ t: Date.now(), w: lb });
    S.body.sort((a, b) => a.t - b.t); S.settings.bodyweight = lb; save(); render(); toast('Logged');
    if (S.settings.health && S.settings.healthWeight) sendWeightToHealth(lb);
  },
  'import-file'(b) { pickFile(b.dataset.v); },
  'export-json'() { saveNow(); download(`kiln-backup-${dayKey()}.json`, JSON.stringify(S), 'application/json'); },
  'export-csv'() { exportCSV(); },
  reset() {
    if (!confirm('Erase all workouts, settings and custom exercises on this device?')) return;
    if (!confirm('Really erase everything? Export a backup first if unsure.')) return;
    localStorage.removeItem(STORE_KEY); location.reload();
  },
  effort(b) {
    const x = S.plan.exercises[+b.dataset.i]; const v = +b.dataset.v;
    x.effort = x.effort === v ? 0 : v; save(); render();
  },
  'deload-start'() {
    if (!S.deload) deloadInfo();
    S.deload.until = Date.now() + DELOAD_DAYS * DAY; S.deload.snooze = 0;
    if (S.plan && !S.plan.start) generate(S.plan.focus);
    save(); render(); toast('Deload week started');
  },
  'deload-snooze'() { S.deload.snooze = Date.now() + 7 * DAY; save(); render(); toast('Reminder snoozed for a week'); },
  'deload-end'() {
    S.deload.anchor = Date.now(); S.deload.until = 0;
    if (S.plan && !S.plan.start) generate(S.plan.focus);
    save(); render(); toast('Back to normal training');
  },
  'health-guide'() { healthGuide(); },
  'health-send'(b) {
    if (!S.settings.health) { S.settings.health = true; save(); render(); }
    const w = S.workouts.find(x => x.id === b.dataset.v); if (w) sendWorkoutToHealth(w);
  },
  'health-test'() {
    const end = Date.now();
    sendWorkoutToHealth({ name: 'Kiln test', start: end - 10 * 6e4, end, deload: true });
  },
  't-add'(b) { timer.add(+b.dataset.v); },
  't-skip'() { timer.stop(); },
};

let filePurpose = 'csv';
function pickFile(kind) {
  filePurpose = kind;
  let inp = $('#file-in');
  if (!inp) { inp = document.createElement('input'); inp.type = 'file'; inp.id = 'file-in'; inp.hidden = true; document.body.appendChild(inp); }
  inp.accept = kind === 'json' ? '.json,application/json' : '.csv,text/csv,text/comma-separated-values';
  inp.value = ''; inp.click();
}
document.addEventListener('change', async ev => {
  const t = ev.target;
  if (t.id === 'file-in' && t.files[0]) {
    const text = await t.files[0].text();
    try {
      if (filePurpose === 'json' || /^\s*\{/.test(text)) {
        const data = JSON.parse(text);
        if (!data || !Array.isArray(data.workouts)) throw new Error('Not a Kiln backup');
        if (!confirm(`Restore backup with ${data.workouts.length} workouts? This replaces everything on this device.`)) return;
        const fresh = mergeState(data);
        Object.keys(S).forEach(k => delete S[k]); Object.assign(S, fresh);
        rebuildEx(); touch(); saveNow(); ensurePlan(); render(); toast('Backup restored');
      } else {
        const res = importCSV(text);
        if (!S.onboarded) { OB.step = 1; }
        if (S.plan && !S.plan.start) generate();
        render();
        alert(`Imported ${res.added} workouts (${res.sets} sets).${res.skipped ? ` Skipped ${res.skipped} already imported.` : ''}\n\nUnrecognized exercise names were added as custom exercises. Check Exercises → filter by muscle to fix any mislabeled ones.`);
      }
    } catch (err) { alert('Import failed: ' + err.message); }
    return;
  }
  if (t.dataset.f && S.plan) {
    // propagate a changed weight/reps to the following unchecked sets that still had the old value
    const i = +t.dataset.i, j = +t.dataset.j, f = t.dataset.f;
    const x = S.plan.exercises[i]; if (!x) return;
    const prevVal = t.dataset.prev;
    const newVal = x.sets[j][f];
    for (let k = j + 1; k < x.sets.length; k++) {
      const s = x.sets[k];
      if (s.done || s.wu !== x.sets[j].wu) continue;
      if (String(s[f] ?? '') === String(prevVal ?? '')) s[f] = newVal;
    }
    save(); render();
  }
  if (t.dataset.settingStr) { S.settings[t.dataset.settingStr] = t.value.trim() || 'Kiln to Health'; save(); }
  if (t.dataset.setting) {
    const k = t.dataset.setting; const v = parseFloat(t.value);
    if (isNaN(v) || v <= 0) return;
    S.settings[k] = k === 'bodyweight' ? fromDisp(v) : v;
    save();
  }
});
document.addEventListener('focusin', ev => {
  const t = ev.target;
  if (t.dataset?.f && S.plan) {
    const x = S.plan.exercises[+t.dataset.i]; const v = x?.sets[+t.dataset.j]?.[t.dataset.f];
    t.dataset.prev = v ?? '';
    setTimeout(() => t.select?.(), 0);
  }
});
document.addEventListener('input', ev => {
  const t = ev.target;
  if (t.dataset.f && S.plan) {
    const s = S.plan.exercises[+t.dataset.i]?.sets[+t.dataset.j]; if (!s) return;
    const raw = t.value.replace(',', '.').trim();
    if (raw === '') { s[t.dataset.f] = null; save(); return; }
    const v = parseFloat(raw); if (isNaN(v)) return;
    s[t.dataset.f] = t.dataset.f === 'w' ? fromDisp(v) : Math.round(v);
    save();
    return;
  }
  if (t.id === 'lib-q') {
    V.libQuery = t.value;
    const pos = t.selectionStart; render();
    const n = $('#lib-q'); n.focus(); n.setSelectionRange(pos, pos);
  }
  if (t.id === 'pick-q') {
    const list = V.sheet?.type === 'swap'
      ? availableExercises().filter(e => !S.plan.exercises.some(y => y.exId === e.id))
      : availableExercises();
    $('#pick-list').innerHTML = pickList(list, t.value);
  }
});
document.addEventListener('click', ev => {
  unlockAudio();
  const b = ev.target.closest('[data-a]');
  if (!b || b.disabled) return;
  const fn = A[b.dataset.a];
  if (fn) { ev.preventDefault(); fn(b, ev); }
});
$('#scrim').addEventListener('click', closeSheet);
document.addEventListener('keydown', ev => {
  if (ev.key === 'Enter' && ev.target.matches('.set input')) {
    // jump to next input in the card for fast entry
    const inputs = [...document.querySelectorAll('.set input')];
    const k = inputs.indexOf(ev.target);
    if (inputs[k + 1]) inputs[k + 1].focus(); else ev.target.blur();
  }
  if (ev.key === 'Escape') closeSheet();
});
// swipe-down to close sheets
(() => {
  let y0 = null, sh;
  document.addEventListener('touchstart', e => { sh = $('#sheet'); if (!sh.classList.contains('open') || !e.target.closest('#sheet')) return; if (sh.scrollTop > 0) return; y0 = e.touches[0].clientY; }, { passive: true });
  document.addEventListener('touchmove', e => { if (y0 == null) return; const dy = e.touches[0].clientY - y0; if (dy > 0) sh.style.transform = `translateY(${dy}px)`; }, { passive: true });
  document.addEventListener('touchend', e => { if (y0 == null) return; const dy = e.changedTouches[0].clientY - y0; sh.style.transform = ''; y0 = null; if (dy > 110) closeSheet(); });
})();

/* ---------- boot ---------- */
ensurePlan();
render();
if (S.plan?.start) requestWake();
if (navigator.storage?.persist) navigator.storage.persist().catch(() => {});
if ('serviceWorker' in navigator && location.protocol === 'https:') navigator.serviceWorker.register('sw.js').catch(() => {});
