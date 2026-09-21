/**
 * Outputs: CSV for the pipeline, Markdown digest grouped by retainer potential.
 */

import fs from 'node:fs';
import path from 'node:path';
import { DATA_DIR } from './store.js';

const CSV_COLUMNS = [
  'retainerLevel', 'retainerScore', 'score', 'tier', 'title', 'url',
  'contractType', 'fixedBudget', 'hourlyMin', 'hourlyMax', 'estimatedDuration', 'durationMonths', 'workload',
  'proposals', 'paymentVerified', 'clientSpend', 'clientHires', 'clientHireRate', 'clientRating', 'clientCountry', 'country',
  'postedRelative', 'experienceLevel', 'connectsRequired', 'skills', 'sourceId', 'firstSeenAt',
];

function csvCell(value) {
  if (value == null) return '';
  const s = Array.isArray(value) ? value.join('; ') : String(value);
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

export function toCsv(jobs) {
  const rows = [CSV_COLUMNS.join(',')];
  for (const job of jobs) rows.push(CSV_COLUMNS.map((c) => csvCell(job[c])).join(','));
  return rows.join('\n');
}

function money(job) {
  if (job.contractType === 'hourly') {
    if (job.hourlyMin && job.hourlyMax) return `$${job.hourlyMin}-${job.hourlyMax}/hr`;
    if (job.hourlyMax || job.hourlyMin) return `$${job.hourlyMax || job.hourlyMin}/hr`;
    return 'hourly, rate not listed';
  }
  if (job.fixedBudget) return `$${job.fixedBudget.toLocaleString()} fixed`;
  return 'budget not listed';
}

/** The line that tells you whether this is a client or a transaction. */
function clientLine(job) {
  const bits = [];
  if (job.clientSpend != null) bits.push(`$${job.clientSpend.toLocaleString()} spent`);
  if (job.clientHires != null) bits.push(`${job.clientHires} hires`);
  if (job.clientHireRate) bits.push(`${job.clientHireRate} hire rate`);
  if (job.clientRating != null) bits.push(`${job.clientRating}★`);
  bits.push(job.clientCountry ? `${job.clientCountry}${job.country ? '' : ' (unrecognized)'}` : 'COUNTRY UNKNOWN — verify before bidding');
  return bits.join(' · ') || 'client history not shown';
}

function jobBlock(job) {
  const lines = [];
  lines.push(`### ${job.retainerLevel} retainer · fit ${job.score} · ${job.title}`);
  const terms = [money(job)];
  if (job.estimatedDuration) terms.push(job.estimatedDuration);
  if (job.workload) terms.push(job.workload);
  terms.push(`${job.proposals ?? '?'} proposals`);
  if (job.postedRelative) terms.push(job.postedRelative);
  if (job.connectsRequired) terms.push(`${job.connectsRequired} connects`);
  lines.push(terms.join(' · '));
  lines.push(`Client: ${clientLine(job)}`);
  lines.push(``);

  const desc = (job.description || '').replace(/\s+/g, ' ').slice(0, 360);
  if (desc) lines.push(`${desc}${desc.length >= 360 ? '…' : ''}`, ``);

  if (job.retainerReasons?.length) lines.push(`Retainer signals: ${job.retainerReasons.slice(0, 6).join(', ')}`);
  lines.push(`Fit: ${job.reasons.slice(0, 6).join(', ')}`);
  lines.push(``, `[Open job](${job.url})`, ``, `---`, ``);
  return lines;
}

export function toMarkdown(jobs, meta = {}) {
  const high = jobs.filter((j) => j.retainerLevel === 'HIGH');
  const medium = jobs.filter((j) => j.retainerLevel === 'MEDIUM');
  const low = jobs.filter((j) => j.retainerLevel === 'LOW');
  const stamp = new Date().toLocaleString('en-US', { timeZone: 'America/New_York' });

  const lines = [
    `# Upwork lead digest`,
    ``,
    `${stamp} ET · ${jobs.length} qualified · ${high.length} high retainer potential`,
  ];
  if (meta.disqualified) lines.push(`${meta.disqualified} dropped at the budget gate.`);
  if (meta.blockedPages) lines.push(``, `> ${meta.blockedPages} search page(s) came back blocked or empty. See README troubleshooting.`);
  lines.push(``);

  const section = (label, note, list) => {
    if (!list.length) return;
    lines.push(`## ${label}`, ``, `_${note}_`, ``);
    for (const job of list) lines.push(...jobBlock(job));
  };

  section('High retainer potential', 'Ongoing shape, repeat hirer, or long duration. Pitch the relationship, not the project.', high);
  section('Medium retainer potential', 'Could extend. Pitch the project, plant the seed for phase two.', medium);
  section('One-off, but worth the budget', 'Treat as project revenue. Bid only if the number justifies the connects.', low);

  if (!jobs.length) lines.push(`Nothing cleared the gates and score floor this run.`, ``);
  return lines.join('\n');
}

export function writeOutputs(jobs, meta) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  const day = new Date().toISOString().slice(0, 10);
  const csvPath = path.join(DATA_DIR, `leads-${day}.csv`);
  const mdPath = path.join(DATA_DIR, `digest-${day}.md`);

  const csv = toCsv(jobs);
  if (fs.existsSync(csvPath)) {
    fs.appendFileSync(csvPath, '\n' + csv.split('\n').slice(1).join('\n'));
  } else {
    fs.writeFileSync(csvPath, csv);
  }
  fs.writeFileSync(mdPath, toMarkdown(jobs, meta));
  return { csvPath, mdPath };
}

/** Optional push to Make/Zapier/n8n so leads land in Notion or Slack. */
export async function pushWebhook(jobs) {
  const url = process.env.WEBHOOK_URL;
  if (!url || !jobs.length) return { sent: 0 };
  let sent = 0;
  for (const job of jobs) {
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(job),
      });
      if (res.ok) sent++;
    } catch {
      /* a dead webhook should never kill the run */
    }
  }
  return { sent };
}
