/**
 * Outputs: CSV for the pipeline, Markdown digest for your morning scan.
 */

import fs from 'node:fs';
import path from 'node:path';
import { DATA_DIR } from './store.js';

const CSV_COLUMNS = [
  'score', 'tier', 'title', 'url', 'contractType', 'fixedBudget', 'hourlyMin', 'hourlyMax',
  'proposals', 'paymentVerified', 'clientSpend', 'clientRating', 'clientCountry',
  'postedRelative', 'experienceLevel', 'estimatedDuration', 'skills', 'sourceId', 'firstSeenAt',
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

export function toMarkdown(jobs, meta = {}) {
  const priority = jobs.filter((j) => j.tier === 'PRIORITY');
  const qualified = jobs.filter((j) => j.tier === 'QUALIFIED');
  const stamp = new Date().toLocaleString('en-US', { timeZone: 'America/New_York' });

  const lines = [
    `# Upwork lead digest`,
    ``,
    `${stamp} ET · ${jobs.length} new qualified · ${priority.length} priority`,
    meta.blockedPages ? `\n> ${meta.blockedPages} search page(s) came back blocked or empty. See README troubleshooting.` : '',
    ``,
  ];

  const section = (label, list) => {
    if (!list.length) return;
    lines.push(`## ${label}`, ``);
    for (const job of list) {
      lines.push(`### ${job.score} · ${job.title}`);
      lines.push(`${money(job)} · ${job.proposals ?? '?'} proposals · ${job.clientCountry || 'location n/a'} · ${job.postedRelative || 'posted n/a'}`);
      lines.push(``);
      const desc = (job.description || '').replace(/\s+/g, ' ').slice(0, 320);
      if (desc) lines.push(`${desc}${desc.length >= 320 ? '…' : ''}`, ``);
      lines.push(`Why it scored: ${job.reasons.slice(0, 6).join(', ')}`);
      lines.push(``);
      lines.push(`[Open job](${job.url})`);
      lines.push(``, `---`, ``);
    }
  };

  section('Priority — bid today', priority);
  section('Qualified', qualified);

  if (!jobs.length) lines.push(`No new jobs cleared the score floor this run.`, ``);
  return lines.join('\n');
}

export function writeOutputs(jobs, meta) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  const day = new Date().toISOString().slice(0, 10);
  const csvPath = path.join(DATA_DIR, `leads-${day}.csv`);
  const mdPath = path.join(DATA_DIR, `digest-${day}.md`);

  // Append to the day's CSV rather than clobbering it on the second run.
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
