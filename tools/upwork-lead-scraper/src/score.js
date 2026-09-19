/**
 * ICP scoring. Turns a normalized job into an uncapped point score plus the
 * reasons behind it, so the digest tells you WHY something is worth connects.
 * Typical range is 0-150. Thresholds live in config.js.
 */

import { scoring } from '../config.js';

function band(bands, value, keyName = 'min') {
  if (value == null) return null;
  for (const b of bands) {
    if (keyName === 'min' && value >= b.min) return b;
    if (keyName === 'max' && value <= b.max) return b;
  }
  return null;
}

export function scoreJob(job) {
  const reasons = [];
  let score = 0;
  const add = (points, label) => {
    if (!points) return;
    score += points;
    reasons.push(`${points > 0 ? '+' : ''}${points} ${label}`);
  };

  const haystack = `${job.title} ${job.description} ${(job.skills || []).join(' ')}`.toLowerCase();

  // Budget
  if (job.contractType === 'hourly') {
    const rate = job.hourlyMax ?? job.hourlyMin;
    const b = band(scoring.hourlyBands, rate);
    if (b) add(b.points, `hourly rate $${rate}/hr`);
    else reasons.push('0 hourly rate unknown');
  } else if (job.fixedBudget != null) {
    const b = band(scoring.fixedBands, job.fixedBudget);
    if (b) add(b.points, `fixed budget $${job.fixedBudget.toLocaleString()}`);
  } else {
    reasons.push('0 budget not listed');
  }

  // Keyword fit
  for (const rule of scoring.positive) {
    const hit = rule.match.find((m) => haystack.includes(m));
    if (hit) add(rule.points, `fit: "${hit}"`);
  }
  for (const rule of scoring.negative) {
    const hit = rule.match.find((m) => haystack.includes(m));
    if (hit) add(rule.points, `flag: "${hit}"`);
  }

  // Client quality
  const s = scoring.signals;
  if (job.paymentVerified === true) add(s.paymentVerified, 'payment verified');
  if (job.paymentVerified === false) add(s.notPaymentVerified, 'payment NOT verified');

  const spendBand = band(s.clientSpendBands, job.clientSpend);
  if (spendBand) add(spendBand.points, `client spend $${(job.clientSpend || 0).toLocaleString()}`);

  const propBand = band(s.proposalBands, job.proposals, 'max');
  if (propBand && job.proposals != null) add(propBand.points, `${job.proposals} proposals`);

  if (job.clientRating != null && job.clientRating >= 4.5) add(s.ratingAtLeast45, `client rating ${job.clientRating}`);
  if (/united states|usa|us$/i.test(job.clientCountry || '')) add(s.usClient, 'US client');

  const fresh = s.freshnessBands.find((b) => (job.postedHoursAgo ?? Infinity) <= b.maxHours);
  if (fresh && job.postedHoursAgo != null) add(fresh.points, `posted ${job.postedRelative || `${job.postedHoursAgo}h ago`}`);

  const final = Math.max(0, Math.round(score));
  return {
    score: final,
    tier: final >= scoring.priorityScore ? 'PRIORITY' : final >= scoring.minScore ? 'QUALIFIED' : 'SKIP',
    reasons,
  };
}

export function qualifies(job) {
  return (job.score ?? 0) >= scoring.minScore;
}
