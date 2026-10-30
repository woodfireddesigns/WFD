// Run with: npm test   (node --test, no dependencies)
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

// bodycomp.js is a plain browser script; load its globals into a sandbox.
const ctx = {};
vm.createContext(ctx);
vm.runInContext(readFileSync(new URL('../bodycomp.js', import.meta.url), 'utf8') +
  '\n;Object.assign(globalThis, { navyBodyFat, waistToHeight, whtrZone, siteDeltas, trendWeight, goalProgress });', ctx);
const { navyBodyFat, waistToHeight, whtrZone, siteDeltas, trendWeight, goalProgress } = ctx;

test('Navy body fat, male, matches hand-computed values', () => {
  // 86.010*log10(20) - 70.041*log10(70) + 36.76 = 19.43
  assert.equal(navyBodyFat({ waist: 36, neck: 16, height: 70 }), 19.4);
  // 86.010*log10(24.5) - 70.041*log10(72) + 36.76 = 26.15
  assert.equal(navyBodyFat({ waist: 40, neck: 15.5, height: 72 }), 26.2);
});

test('Navy body fat, female, uses hips', () => {
  // 163.205*log10(56.5) - 97.684*log10(65) - 78.387 = 30.46
  assert.equal(navyBodyFat({ sex: 'female', waist: 30, hips: 40, neck: 13.5, height: 65 }), 30.5);
  assert.equal(navyBodyFat({ sex: 'female', waist: 30, neck: 13.5, height: 65 }), null);
});

test('Navy body fat rejects inputs outside the formula domain', () => {
  assert.equal(navyBodyFat({ waist: 15, neck: 16, height: 70 }), null);   // waist <= neck: log of negative
  assert.equal(navyBodyFat({ waist: 16, neck: 16, height: 70 }), null);   // log10(0)
  assert.equal(navyBodyFat({ waist: 36, neck: 16, height: 0 }), null);
  assert.equal(navyBodyFat({ waist: 36, neck: null, height: 70 }), null);
  assert.equal(navyBodyFat({ waist: 16.5, neck: 16, height: 70 }), null);  // implausible (<2%): tape error
});

test('Waist-to-height ratio', () => {
  assert.equal(waistToHeight(35, 70), 0.5);
  assert.equal(waistToHeight(38, 70), 0.543);
  assert.equal(waistToHeight(null, 70), null);
  assert.equal(waistToHeight(35, 0), null);
});

test('Waist-to-height zones and exact boundaries', () => {
  assert.equal(whtrZone(0.499), 'healthy');
  assert.equal(whtrZone(0.5), 'elevated');
  assert.equal(whtrZone(0.6), 'elevated');
  assert.equal(whtrZone(0.601), 'high');
  assert.equal(whtrZone(null), null);
});

test('Site deltas: since last and since baseline, skipping gaps', () => {
  const entries = [
    { date: '2026-10-04', waist: 38.0, arm: 15.0 },
    { date: '2026-10-11', waist: 37.6, arm: null },
    { date: '2026-10-18', waist: 37.1 },
    { date: '2026-10-25', waist: null, arm: 15.4 },
  ];
  assert.deepEqual(
    { ...siteDeltas(entries, 'waist') },
    { latest: 37.1, date: '2026-10-18', sinceLast: -0.5, sinceBaseline: -0.9, count: 3 });
  const arm = siteDeltas(entries, 'arm');
  assert.equal(arm.latest, 15.4); assert.equal(arm.sinceLast, 0.4); assert.equal(arm.sinceBaseline, 0.4);
});

test('Site deltas: a single entry is its own baseline', () => {
  const d = siteDeltas([{ date: '2026-10-25', waist: 37 }], 'waist');
  assert.equal(d.latest, 37); assert.equal(d.sinceLast, null); assert.equal(d.sinceBaseline, null);
  assert.equal(siteDeltas([], 'waist').latest, null);
});

test('Trend weight averages the last 7 days only', () => {
  const D = 864e5;
  assert.equal(trendWeight([{ t: 0, w: 220 }, { t: 10 * D, w: 210 }, { t: 12 * D, w: 209 }, { t: 14 * D, w: 208 }]), 209);
  assert.equal(trendWeight([]), null);
});

test('Goal progress toward 195 with a 185 stretch', () => {
  const g = goalProgress(205, 195, 185, 215);
  assert.equal(g.toGoal, 10); assert.equal(g.pctGoal, 0.5);
  assert.equal(g.toStretch, 20); assert.equal(g.pctStretch, 1 / 3);
  assert.equal(g.reachedGoal, false);
  assert.equal(goalProgress(194, 195, 185, 215).reachedGoal, true);
  assert.equal(goalProgress(220, 195, 185, 215).pctGoal, 0);   // above start clamps to 0
});
