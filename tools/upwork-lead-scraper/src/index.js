#!/usr/bin/env node
/**
 * WFD Upwork lead scraper.
 *
 *   node src/index.js run            # full run across config.js searches
 *   node src/index.js run --dry-run  # print the URLs it would hit, spend nothing
 *   node src/index.js run --query="brand identity" --pages=1
 *   node src/index.js run --source=web    # fallback via Firecrawl web search
 *   node src/index.js smoke          # verify the API key works
 *   node src/index.js report         # rebuild the digest from stored jobs
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
loadDotEnv(path.join(ROOT, '.env'));

const { searches, scoring, run: runCfg } = await import('../config.js');
const { scrapeSearchPage, scrapeJobDetail, discoverViaWebSearch, buildSearchUrl } = await import('./upwork.js');
const { scrapeJson, hasKey } = await import('./firecrawl.js');
const { scoreJob, rank } = await import('./score.js');
const store = await import('./store.js');
const { writeOutputs, pushWebhook, toMarkdown } = await import('./report.js');

const argv = process.argv.slice(2);
const command = argv.find((a) => !a.startsWith('-')) || 'run';
const flags = Object.fromEntries(
  argv.filter((a) => a.startsWith('--')).map((a) => {
    const [k, v] = a.replace(/^--/, '').split('=');
    return [k, v === undefined ? true : v];
  })
);

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const log = (...a) => console.log(...a);

async function main() {
  if (command === 'smoke') return smoke();
  if (command === 'report') return report();
  return doRun();
}

async function doRun() {
  const dryRun = Boolean(flags['dry-run']);
  const minScore = Number(flags['min-score'] ?? scoring.minScore);
  const targets = flags.query
    ? [{ id: 'adhoc', q: String(flags.query), pages: Number(flags.pages || 1), filters: {} }]
    : searches.map((s) => ({ ...s, pages: Number(flags.pages || s.pages || 1) }));

  if (dryRun) {
    log('Dry run. URLs that would be scraped:\n');
    for (const s of targets) {
      for (let p = 1; p <= s.pages; p++) log(`  [${s.id}] ${buildSearchUrl(s, p)}`);
    }
    log(`\n${targets.reduce((n, s) => n + s.pages, 0)} Firecrawl scrape calls. No credits spent.`);
    return;
  }

  if (!hasKey()) {
    console.error('FIRECRAWL_API_KEY is not set. Copy .env.example to .env and add your key, or export it in your shell.');
    process.exit(1);
  }

  const state = store.prune(store.load());
  const collected = [];
  let blockedPages = 0;

  for (const s of targets) {
    if (flags.source === 'web') {
      log(`[${s.id}] web-search fallback: "${s.q}"`);
      try {
        collected.push(...(await discoverViaWebSearch(s.q, { limit: Number(flags.limit || 20) })));
      } catch (err) {
        console.error(`[${s.id}] web search failed: ${err.message}`);
      }
      await sleep(runCfg.delayMs);
      continue;
    }

    for (let page = 1; page <= s.pages; page++) {
      try {
        const res = await scrapeSearchPage(s, page);
        if (res.blocked || res.jobs.length === 0) {
          blockedPages++;
          log(`[${s.id}] page ${page}: 0 jobs (status ${res.statusCode ?? '?'}${res.blocked ? ', looks blocked' : ''})`);
        } else {
          log(`[${s.id}] page ${page}: ${res.jobs.length} jobs`);
        }
        collected.push(...res.jobs);
      } catch (err) {
        blockedPages++;
        console.error(`[${s.id}] page ${page} failed: ${err.message}`);
        if (err.status === 401 || err.status === 402) process.exit(1);
      }
      await sleep(runCfg.delayMs);
    }
  }

  // Dedupe within this run, then against everything seen before.
  const byId = new Map();
  for (const job of collected) if (job.id && job.url) byId.set(job.id, { ...byId.get(job.id), ...job });
  const { fresh } = store.split(state, [...byId.values()]);
  log(`\n${byId.size} unique jobs scraped, ${fresh.length} never seen before.`);

  const scored = fresh.map((job) => ({ ...job, ...scoreJob(job) }));
  const gated = scored.filter((j) => j.disqualified);
  if (gated.length) {
    log(`${gated.length} dropped at the gates (e.g. ${gated[0].disqualifiedReason}).`);
  }

  let qualified = scored.filter((j) => !j.disqualified && j.score >= minScore).sort(rank);

  // Enrich with full job-page detail, then rescore. This is where retainer signal
  // actually lives: duration, weekly hours, client hire count, and the tail end of
  // the description where "looking for someone long term" usually hides. Jobs still
  // missing those fields go first.
  if (!flags['no-enrich']) {
    const needsDetail = (j) => j.estimatedDuration === '' || j.clientHires == null;
    const toEnrich = qualified
      .filter((j) => j.score >= runCfg.enrichAboveScore)
      .sort((a, b) => Number(needsDetail(b)) - Number(needsDetail(a)) || rank(a, b))
      .slice(0, runCfg.maxEnrichPerRun);

    for (const job of toEnrich) {
      try {
        const detail = await scrapeJobDetail(job.url);
        if (detail) {
          Object.assign(job, { ...detail, id: job.id, sourceId: job.sourceId, firstSeenAt: job.firstSeenAt });
          Object.assign(job, scoreJob(job));
          log(`  enriched: ${job.title.slice(0, 55)} -> fit ${job.score}, retainer ${job.retainerLevel}`);
        }
      } catch (err) {
        console.error(`  enrich failed (${job.url}): ${err.message}`);
      }
      await sleep(runCfg.delayMs);
    }
    // Enrichment can disqualify a job that looked fine on the card.
    qualified = qualified.filter((j) => !j.disqualified && j.score >= minScore).sort(rank);
  }

  store.commit(state, scored);
  store.save(state);

  const { csvPath, mdPath } = writeOutputs(qualified, { blockedPages, disqualified: gated.length });
  const hook = await pushWebhook(qualified);

  const high = qualified.filter((j) => j.retainerLevel === 'HIGH').length;
  const medium = qualified.filter((j) => j.retainerLevel === 'MEDIUM').length;
  log(`\n${qualified.length} qualified (fit >= ${minScore}) · ${high} high retainer potential · ${medium} medium.`);
  log(`CSV:    ${csvPath}`);
  log(`Digest: ${mdPath}`);
  if (hook.sent) log(`Webhook: ${hook.sent} pushed`);
  if (blockedPages) {
    log(`\n${blockedPages} page(s) returned nothing. Try FIRECRAWL_PROXY=stealth, raise FIRECRAWL_WAIT_FOR, or rerun with --source=web.`);
  }
}

async function report() {
  const state = store.load();
  const jobs = Object.values(state.jobs)
    .map((j) => ({ ...j, ...scoreJob(j) }))
    .filter((j) => !j.disqualified && j.score >= Number(flags['min-score'] ?? scoring.minScore))
    .sort(rank)
    .slice(0, Number(flags.limit || 50));
  log(toMarkdown(jobs));
}

async function smoke() {
  log('Testing Firecrawl credentials against example.com ...');
  const res = await scrapeJson('https://example.com', {
    schema: { type: 'object', properties: { heading: { type: 'string' } } },
    prompt: 'Return the main heading text.',
    proxy: 'basic',
    waitFor: 0,
  });
  log(`HTTP ${res.statusCode} · extracted:`, JSON.stringify(res.json));
  log('Key works.');
}

/** Tiny .env loader so there is no dotenv dependency. */
function loadDotEnv(file) {
  if (!fs.existsSync(file)) return;
  for (const line of fs.readFileSync(file, 'utf8').split('\n')) {
    const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/i);
    if (!m) continue;
    const value = m[2].replace(/^["']|["']$/g, '');
    if (value && !process.env[m[1]]) process.env[m[1]] = value;
  }
}

main().catch((err) => {
  console.error(`\nFailed: ${err.message}`);
  process.exit(1);
});
