'use strict';
// Body composition math for the Body module. Pure functions, no DOM: tested in tests/bodycomp.test.js.
// Every number here is an estimate or a screening ratio, never a measurement of body fat.

const BODY_SITES = ['waist', 'neck', 'chest', 'hips', 'thigh', 'arm'];
const round1 = x => Math.round(x * 10) / 10;
const num = x => (typeof x === 'number' && isFinite(x) ? x : null);

// US Navy circumference method. Inches in, body fat % out (one decimal), or null when inputs are unusable.
function navyBodyFat({ sex = 'male', waist, neck, hips, height }) {
  waist = num(waist); neck = num(neck); hips = num(hips); height = num(height);
  if (!waist || !neck || !height || height <= 0) return null;
  let bf;
  if (sex === 'female') {
    if (!hips) return null;
    const girth = waist + hips - neck;
    if (girth <= 0) return null;
    bf = 163.205 * Math.log10(girth) - 97.684 * Math.log10(height) - 78.387;
  } else {
    if (waist - neck <= 0) return null;
    bf = 86.010 * Math.log10(waist - neck) - 70.041 * Math.log10(height) + 36.76;
  }
  if (!isFinite(bf) || bf < 2 || bf > 70) return null;   // outside any plausible range: bad tape reading
  return round1(bf);
}

function waistToHeight(waist, height) {
  waist = num(waist); height = num(height);
  if (!waist || !height || height <= 0) return null;
  return Math.round((waist / height) * 1000) / 1000;
}

// Zones: under 0.5 healthy, 0.5 to 0.6 elevated, over 0.6 high.
function whtrZone(r) {
  if (r == null) return null;
  if (r < 0.5) return 'healthy';
  if (r <= 0.6) return 'elevated';
  return 'high';
}

// entries: sorted oldest first. Returns latest value plus change since the previous entry and since the first.
function siteDeltas(entries, site) {
  const vals = entries.filter(e => num(e[site]) != null).map(e => ({ date: e.date, v: e[site] }));
  if (!vals.length) return { latest: null, sinceLast: null, sinceBaseline: null, count: 0 };
  const latest = vals[vals.length - 1];
  return {
    latest: latest.v,
    date: latest.date,
    sinceLast: vals.length > 1 ? round1(latest.v - vals[vals.length - 2].v) : null,
    sinceBaseline: vals.length > 1 ? round1(latest.v - vals[0].v) : null,
    count: vals.length,
  };
}

// Average of weigh-ins in the 7 days ending at the latest one: smooths out water swings.
function trendWeight(body) {
  if (!body || !body.length) return null;
  const last = body[body.length - 1].t;
  const win = body.filter(b => last - b.t < 7 * 864e5);
  return round1(win.reduce((a, b) => a + b.w, 0) / win.length);
}

// Progress from a starting weight toward a goal (works for cutting or gaining).
function goalProgress(current, goal, stretch, start) {
  current = num(current); goal = num(goal); start = num(start); stretch = num(stretch);
  if (current == null || goal == null) return null;
  const pct = (from, to) => (from == null || from === to ? (current === to ? 1 : 0)
    : Math.max(0, Math.min(1, (from - current) / (from - to))));
  return {
    toGoal: round1(Math.abs(current - goal)),
    reachedGoal: start != null && start >= goal ? current <= goal : current >= goal,
    pctGoal: pct(start, goal),
    toStretch: stretch == null ? null : round1(Math.abs(current - stretch)),
    pctStretch: stretch == null ? null : pct(start, stretch),
  };
}
