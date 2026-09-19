# Upwork Lead Scraper (Firecrawl)

Pulls Upwork job posts through Firecrawl, scores them against the Wood Fired Designs ICP,
dedupes against everything already seen, and spits out a CSV plus a morning digest.

Zero dependencies. Node 20+. Nothing to build.

---

## Read this before you run it

Upwork sits behind Cloudflare and pushes logged-out visitors toward a login wall. Firecrawl's
stealth proxy gets through a good share of the time, not all of the time. Plan for it:

- Run it on a schedule (every few hours), not as a one-shot. Misses even out.
- `--source=web` is the backup path: Firecrawl web search over indexed `upwork.com/jobs` URLs.
  Lower volume, staler, but it works when the on-site search is walled.
- If you end up needing 100% reliability, the real answer is Upwork's official API
  (`marketplaceJobPostingsSearch`, OAuth2, request a key at developers.upwork.com) and this
  scraper becomes the stopgap. Apify's Upwork actors are the other fallback since you already run Apify.

Scraping a logged-out public page is not the same as violating Upwork's ToS with a logged-in
session, but this is still a gray zone. Do not feed it your Upwork credentials or cookies.

---

## Setup

```bash
cd tools/upwork-lead-scraper
cp .env.example .env
# paste your Firecrawl key into .env
npm run smoke        # verifies the key against example.com, costs ~1 credit
```

## Usage

```bash
npm run dry                      # print the URLs it would hit, spend nothing
npm run scrape                   # full run across every search in config.js
node src/index.js run --query="brand identity" --pages=1
node src/index.js run --source=web        # fallback discovery path
node src/index.js run --no-enrich         # skip detail-page enrichment, cheaper
node src/index.js run --min-score=70      # tighter filter for this run only
node src/index.js report --limit=25       # rebuild digest from stored jobs, no API calls
```

Outputs land in `data/` (gitignored):

- `jobs.json` — every job ever seen, the dedupe memory. Auto-pruned at 45 days.
- `leads-YYYY-MM-DD.csv` — import into Notion, Sheets, or your CRM.
- `digest-YYYY-MM-DD.md` — the scan-in-90-seconds version, priority jobs first.

Set `WEBHOOK_URL` in `.env` and every qualified job also POSTs as JSON to Make/Zapier/n8n,
which is how you get these into Notion or a Slack channel without touching this code.

---

## Tuning

Everything you'll actually want to change lives in `config.js`.

**`searches`** — the queries and filters. Each entry becomes an Upwork search URL:

```js
{
  id: 'framer-website',
  q: 'Framer website',
  pages: 2,
  filters: {
    paymentVerified: true,
    fixedMin: 1000,        // -> &amount=1000-
    hourlyMin: 50,         // -> &hourly_rate=50-
    tiers: ['intermediate', 'expert'],
    contractType: 'fixed', // optional: 'fixed' | 'hourly', default both
    location: 'United States', // optional
  },
}
```

Each page costs one Firecrawl scrape call. The default config is 11 calls a run.

**`scoring`** — the point weights.

- `fixedBands` / `hourlyBands`: budget is the heaviest single signal.
- `positive`: phrases that mean it's your work. Brand identity, Framer, rebrand, retainer language.
- `negative`: phrases that mean walk away. Contests, Canva, SEO, "beginner welcome".
- `signals`: payment verified, client spend, proposal count, rating, country, freshness.
- `minScore` (55) is the floor for the digest. `priorityScore` (95) flags "bid today".

Calibration: a plain $2k website job lands around 55-65. A $6k brand-identity-plus-Framer job
with a verified, high-spend US client lands 120+. Adjust the floor after a week of real runs —
if the digest is too long, raise `minScore` before you touch anything else.

**`run`** — `enrichAboveScore` (65) pulls the full job page for high scorers so you get the
complete description, screening questions, and connects cost before you spend connects.
Each enrichment is one extra scrape call, capped at `maxEnrichPerRun` (12).

---

## Cost per run

Default config, worst case: 11 search scrapes + up to 12 enrichments = 23 Firecrawl calls.
Stealth proxy costs more credits per call than basic. Run every 4 hours and you're at roughly
140 calls a day. Drop `pages` to 1 and set `--no-enrich` if you want that cut roughly in half.

---

## Scheduling

`github-action.example.yml` is a ready-to-go workflow. It is intentionally NOT active — this repo
is the marketing site. To use it, copy it to `.github/workflows/upwork-scraper.yml`, add
`FIRECRAWL_API_KEY` as a repo secret, and decide whether you want the digest committed back
or just uploaded as an artifact.

A cron on your own machine works just as well:

```
0 */4 * * * cd ~/WFD/tools/upwork-lead-scraper && /usr/local/bin/node src/index.js run >> data/run.log 2>&1
```

---

## Troubleshooting

**Every page returns 0 jobs.** Cloudflare. In order: confirm `FIRECRAWL_PROXY=stealth`,
raise `FIRECRAWL_WAIT_FOR` to 10000, then fall back to `--source=web`.

**Firecrawl 402.** Out of credits.

**Firecrawl 401.** Bad or revoked key.

**Jobs come back with null budgets.** The extractor didn't find the values on the card. Enrichment
usually fixes it for the high scorers. If it's systemic, Upwork changed their markup — tighten the
field descriptions in `JOB_FIELDS` in `src/upwork.js`.

**Same job appears twice.** Both would need to have different `~0...` ids in their URLs. Check
`data/jobs.json`; delete it to reset the dedupe memory entirely.

---

## Files

```
config.js            searches + scoring weights   <- you edit this
src/index.js         CLI
src/firecrawl.js     Firecrawl v2 client, retries, backoff
src/upwork.js        URL builder, extraction schemas, normalization
src/score.js         ICP scoring
src/store.js         JSON dedupe store
src/report.js        CSV, markdown digest, webhook push
```
