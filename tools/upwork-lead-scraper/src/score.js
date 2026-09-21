/**
 * Scoring in three passes:
 *   1. gates()          - hard disqualifiers. Serious budgets only.
 *   2. fitScore()       - how well the work matches what WFD sells.
 *   3. retainerScore()  - how likely this turns into ongoing monthly work.
 *
 * Fit and retainer stay separate on purpose. A $12k one-and-done rebrand and a
 * $3k store-management gig that runs all year are both good, for different
 * reasons, and you want to see which is which before you spend connects.
 */

import { gates, scoring, retainer } from '../config.js';

/**
 * Country aliases. Upwork prints the client's country in a few forms, and the
 * digest should not drop a real US job because the card said "USA".
 * Deliberately excludes bare "CA" - that reads as California far more often
 * than Canada.
 */
const COUNTRY_ALIASES = {
  'United States': ['united states', 'united states of america', 'usa', 'u.s.a', 'u.s.', ' us ', 'america'],
  'United Kingdom': ['united kingdom', 'uk', 'u.k.', 'great britain', 'britain', 'england', 'scotland', 'wales', 'northern ireland'],
  Canada: ['canada', 'canadian'],
};

/** Resolve a raw country string to a canonical name, or null if unrecognized. */
export function canonicalCountry(raw) {
  if (!raw) return null;
  const s = ` ${String(raw).toLowerCase().trim()} `;
  for (const [canonical, aliases] of Object.entries(COUNTRY_ALIASES)) {
    if (aliases.some((a) => s.includes(a))) return canonical;
  }
  return null;
}

function band(bands, value, key = 'min') {
  if (value == null) return null;
  for (const b of bands) {
    if (key === 'min' && value >= b.min) return b;
    if (key === 'max' && value <= b.max) return b;
    if (key === 'minMonths' && value >= b.minMonths) return b;
  }
  return null;
}

/** Effective budget figure used by gates and bands. */
function budgetOf(job) {
  if (job.contractType === 'hourly') return { type: 'hourly', value: job.hourlyMax ?? job.hourlyMin };
  if (job.fixedBudget != null) return { type: 'fixed', value: job.fixedBudget };
  if (job.hourlyMax || job.hourlyMin) return { type: 'hourly', value: job.hourlyMax ?? job.hourlyMin };
  return { type: 'unknown', value: null };
}

/** Returns null if the job passes, or a string reason if it's disqualified. */
export function checkGates(job) {
  if (gates.requirePaymentVerified && job.paymentVerified === false) return 'payment not verified';

  // Country whitelist. US, UK, Canada only.
  // A MISSING country is "unknown" and governed by allowUnknownCountry.
  // A country that is present but not on the list is always a drop - an
  // unrecognized name means it isn't US, UK, or Canada, not that it's a mystery.
  if (gates.allowedCountries?.length) {
    const raw = (job.clientCountry || '').trim();
    if (!raw) {
      if (!gates.allowUnknownCountry) return 'client country not listed';
    } else {
      const country = canonicalCountry(raw);
      if (!country || !gates.allowedCountries.includes(country)) {
        return `client in ${raw}, outside ${gates.allowedCountries.join('/')}`;
      }
    }
  }

  const budget = budgetOf(job);
  if (budget.value == null) {
    if (!gates.allowUnknownBudget) return 'no budget listed';
  } else if (budget.type === 'hourly' && gates.minHourlyRate && budget.value < gates.minHourlyRate) {
    return `hourly $${budget.value} under $${gates.minHourlyRate} floor`;
  } else if (budget.type === 'fixed' && gates.minFixedBudget && budget.value < gates.minFixedBudget) {
    return `fixed $${budget.value.toLocaleString()} under $${gates.minFixedBudget.toLocaleString()} floor`;
  }

  if (gates.minClientSpend && (job.clientSpend ?? 0) < gates.minClientSpend) {
    return `client spend under $${gates.minClientSpend.toLocaleString()}`;
  }
  if (gates.maxProposals && job.proposals != null && job.proposals > gates.maxProposals) {
    return `${job.proposals} proposals over cap`;
  }
  return null;
}

/** "More than 6 months" / "3 to 6 months" / "Less than 1 month" -> months. */
export function durationToMonths(text) {
  if (!text) return null;
  const s = String(text).toLowerCase();
  if (s.includes('more than 6')) return 7;
  if (s.includes('3 to 6') || s.includes('3-6')) return 4.5;
  if (s.includes('1 to 3') || s.includes('1-3')) return 2;
  if (s.includes('less than 1 month')) return 0.5;
  if (s.includes('less than a month')) return 0.5;
  if (s.includes('week')) return 0.25;
  const m = s.match(/(\d+)\+?\s*month/);
  if (m) return Number(m[1]);
  return null;
}

function haystackOf(job) {
  return `${job.title} ${job.description} ${(job.skills || []).join(' ')} ${(job.questions || []).join(' ')}`.toLowerCase();
}

export function scoreJob(job) {
  const disqualifiedReason = checkGates(job);
  const haystack = haystackOf(job);

  const reasons = [];
  let score = 0;
  const add = (points, label) => {
    if (!points) return;
    score += points;
    reasons.push(`${points > 0 ? '+' : ''}${points} ${label}`);
  };

  // --- Fit ---
  const budget = budgetOf(job);
  if (budget.type === 'hourly' && budget.value != null) {
    const b = band(scoring.hourlyBands, budget.value);
    if (b) add(b.points, `$${budget.value}/hr`);
  } else if (budget.type === 'fixed' && budget.value != null) {
    const b = band(scoring.fixedBands, budget.value);
    if (b) add(b.points, `$${budget.value.toLocaleString()} fixed`);
  } else {
    reasons.push('0 budget not listed');
  }

  for (const rule of scoring.positive) {
    const hit = rule.match.find((m) => haystack.includes(m));
    if (hit) add(rule.points, `fit: "${hit}"`);
  }
  for (const rule of scoring.negative) {
    const hit = rule.match.find((m) => haystack.includes(m));
    if (hit) add(rule.points, `flag: "${hit}"`);
  }

  const s = scoring.signals;
  if (job.paymentVerified === true) add(s.paymentVerified, 'payment verified');
  if (job.paymentVerified === false) add(s.notPaymentVerified, 'payment NOT verified');

  const spendBand = band(s.clientSpendBands, job.clientSpend);
  if (spendBand && job.clientSpend != null) add(spendBand.points, `client spend $${job.clientSpend.toLocaleString()}`);

  const propBand = band(s.proposalBands, job.proposals, 'max');
  if (propBand && job.proposals != null) add(propBand.points, `${job.proposals} proposals`);

  if (job.clientRating != null && job.clientRating >= 4.5) add(s.ratingAtLeast45, `rating ${job.clientRating}`);
  const country = canonicalCountry(job.clientCountry);
  if (country && s.countryPoints?.[country]) add(s.countryPoints[country], `${country} client`);

  if (job.postedHoursAgo != null) {
    const fresh = s.freshnessBands.find((b) => job.postedHoursAgo <= b.maxHours);
    if (fresh) add(fresh.points, `posted ${job.postedRelative || `${job.postedHoursAgo}h ago`}`);
  }

  // --- Retainer potential ---
  const r = scoreRetainer(job, haystack);

  const fitScore = Math.max(0, Math.round(score));
  return {
    score: fitScore,
    tier: disqualifiedReason
      ? 'DISQUALIFIED'
      : fitScore >= scoring.priorityScore
        ? 'PRIORITY'
        : fitScore >= scoring.minScore
          ? 'QUALIFIED'
          : 'SKIP',
    retainerScore: r.score,
    retainerLevel: r.level,
    retainerReasons: r.reasons,
    durationMonths: durationToMonths(job.estimatedDuration),
    country: canonicalCountry(job.clientCountry),
    reasons,
    disqualified: Boolean(disqualifiedReason),
    disqualifiedReason: disqualifiedReason || '',
  };
}

function scoreRetainer(job, haystack) {
  const reasons = [];
  let score = 0;
  const add = (points, label) => {
    if (!points) return;
    score += points;
    reasons.push(`${points > 0 ? '+' : ''}${points} ${label}`);
  };

  for (const rule of retainer.phrases) {
    const hit = rule.match.find((m) => haystack.includes(m));
    if (hit) add(rule.points, `"${hit}"`);
  }
  for (const rule of retainer.categoryBoosts) {
    const hit = rule.match.find((m) => haystack.includes(m));
    if (hit) add(rule.points, `recurring category: "${hit}"`);
  }

  const months = durationToMonths(job.estimatedDuration);
  if (months != null) {
    const b = band(retainer.durationBands, months, 'minMonths');
    if (b) add(b.points, `${job.estimatedDuration}`);
  }

  if (job.clientHires != null) {
    const b = band(retainer.clientHiresBands, job.clientHires);
    if (b) add(b.points, `${job.clientHires} past hires`);
  }

  if (job.contractType === 'hourly') add(retainer.hourlyContract, 'hourly contract');

  const final = Math.max(0, Math.round(score));
  return {
    score: final,
    level: final >= retainer.highAt ? 'HIGH' : final >= retainer.mediumAt ? 'MEDIUM' : 'LOW',
    reasons,
  };
}

/**
 * Sort key. Retainer potential leads, fit breaks ties - a HIGH-retainer job at
 * score 80 is worth more of your week than a LOW-retainer job at 110.
 */
export function rank(a, b) {
  const levelRank = { HIGH: 2, MEDIUM: 1, LOW: 0 };
  const byLevel = levelRank[b.retainerLevel] - levelRank[a.retainerLevel];
  if (byLevel !== 0) return byLevel;
  return b.score - a.score;
}
