# Upwork Lead Scraper (Firecrawl)

Pulls Upwork job posts through Firecrawl, gates out anything without a serious budget, scores
what's left on two axes (fit and retainer potential), dedupes against everything already seen,
and spits out a CSV plus a morning digest grouped by how likely the job turns into monthly work.

Target: **ecommerce management and brand identity work with real budgets that can grow into a
retainer.** Posts almost never say "retainer" out loud, so it's inferred from proxy signals.

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

### 1. `gates` — the serious-budget filter

Hard disqualifiers, applied **before** scoring. Fail any one and the job is dropped, no matter
how well it reads. This is what keeps the digest short.

```js
requirePaymentVerified: true,
allowedCountries: ['United States', 'United Kingdom', 'Canada'],
allowUnknownCountry: true,  // keep jobs whose card omits country; enrichment recovers it
minFixedBudget: 2000,
minHourlyRate: 45,
allowUnknownBudget: true,   // search cards often omit budget; enrichment recovers it
minClientSpend: 0,          // set to 5000 once volume is healthy
maxProposals: 0,            // 0 = off
```

**Country is enforced twice, on purpose.** Every search URL carries
`&location=United States,United Kingdom,Canada`, and the gate re-checks the extracted
client country after the fact. The URL filter saves credits; the gate is what actually
guarantees correctness if Upwork changes or ignores that param.

Matching handles aliases: "USA", "U.S.", "England", "Scotland", "Britain" all resolve.
Bare "CA" is deliberately NOT treated as Canada — it reads as California far more often.

A country that is **present but not on the list** is always dropped. A **missing** country
is governed by `allowUnknownCountry`. Set it to `false` to drop anything you can't confirm,
at the cost of losing real US jobs whose cards hide the field. Jobs that stay unknown through
enrichment are flagged `COUNTRY UNKNOWN — verify before bidding` in the digest.

Raise `minFixedBudget` to 3500 and `minHourlyRate` to 60 after a week if too much junk gets through.
Set `allowUnknownBudget: false` to be ruthless, at the cost of missing real jobs whose cards hide
the number.

### 2. `searches` — what gets pulled

Ten searches, weighted toward recurring-by-nature work:

| Search | Why it's here |
|---|---|
| `shopify-store-management` | Ongoing by definition |
| `ecommerce-manager` | Ongoing by definition |
| `klaviyo-email-design` | Email is a monthly need, never one-and-done |
| `shopify-cro-product-pages` | Repeats every product launch |
| `brand-identity` | Core offer, highest project value |
| `brand-strategist` | Highest-ticket positioning work |
| `dtc-brand-designer` | Where brand and ecommerce overlap |
| `rebrand` | Big budgets, often opens the door to ongoing |
| `ongoing-design-partner` | Explicitly retainer-shaped |
| `creative-director-part-time` | Expert tier only, usually a monthly arrangement |

Each entry becomes an Upwork search URL:

```js
{
  id: 'framer-website',
  q: 'Framer website',
  pages: 2,
  filters: {
    paymentVerified: true,
    fixedMin: 2000,        // -> &amount=2000-
    hourlyMin: 50,         // -> &hourly_rate=50-
    tiers: ['intermediate', 'expert'],
    contractType: 'fixed', // optional: 'fixed' | 'hourly', default both
    location: 'United States', // optional
  },
}
```

### 3. `scoring` — fit

How well the work matches what you sell. Budget bands carry the most weight, then category
keywords (store management, brand identity, brand strategy, Klaviyo, CRO), then client-quality
signals (spend, proposals, rating, country, freshness).

Negatives do real work here: contests (-50), equity-only (-50), "just a logo" (-30), Canva (-22),
dropshipping (-20), WordPress (-16).

`minScore` (60) is the floor for the digest. `priorityScore` (100) is the fit ceiling flag.

### 4. `retainer` — the part that matters

Scored **separately** from fit, because a $14k one-and-done rebrand and a $3k store-management
gig that runs all year are both good for different reasons, and you want to know which is which
before you spend connects.

Five proxy groups, none of which require the word "retainer":

- **Ongoing language** — "long term", "grow with us", "more projects", "phase 1", "day to day",
  "hours per week", "manage our".
- **Recurring categories** — store management, Klaviyo/email, lifecycle, campaigns, product
  launches, seasonal work, ad creative. Structurally repeat business.
- **Contract duration** — "More than 6 months" is worth +30. "Less than 1 month" is worth -8.
- **Client hire count** — someone with 22 past hires hires again. 25+ hires is +24.
- **Hourly vs fixed** — hourly contracts renew, fixed-price contracts end. +14 for hourly.

Output is a `HIGH` / `MEDIUM` / `LOW` label (thresholds `highAt: 55`, `mediumAt: 28`).

**The digest sorts by retainer level first, fit second.** A HIGH-retainer job at fit 80 outranks
a LOW-retainer job at fit 110, on purpose.

Worked example — this post never says "retainer" and scores HIGH (144):

> "We need someone to manage our Shopify store day to day. Product launches, collection pages,
> Klaviyo campaigns each month. We are scaling fast and want someone who can grow with us."
> $55-80/hr · More than 6 months · client has 22 past hires, $180k spent

### 5. `run` — enrichment

`enrichAboveScore` (60) and `maxEnrichPerRun` (20) control detail-page pulls. Enrichment is
deliberately aggressive now: duration, weekly hours, client hire count, and the tail of the
description are where nearly all retainer signal lives, and none of it reliably appears on the
search card. Jobs missing those fields get enriched first.

---

## Cost per run

Default config, worst case: 15 search scrapes + up to 20 enrichments = 35 Firecrawl calls.
Stealth proxy costs more credits per call than basic. Run every 4 hours and you're at roughly
210 calls a day.

To cut it: drop `pages` to 1 across the board (15 -> 10 search calls), or lower `maxEnrichPerRun`.
Do **not** reach for `--no-enrich` as your first lever — that's the setting that buys you the
retainer signal. Cut search breadth before you cut enrichment depth.

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

**Everything comes back LOW retainer.** Enrichment isn't running or isn't finding duration and
hire counts. Confirm you're not passing `--no-enrich`, then check that `enrichAboveScore` isn't
set above what your jobs actually score.

**Digest is empty but the run found jobs.** The gates are eating them. The run log prints how many
were dropped and an example reason. Lower `gates.minFixedBudget` or set `allowUnknownBudget: true`.

---

## Files

```
config.js            gates + searches + fit scoring + retainer signals   <- you edit this
src/index.js         CLI
src/firecrawl.js     Firecrawl v2 client, retries, backoff
src/upwork.js        URL builder, extraction schemas, normalization
src/score.js         gates, fit scoring, retainer scoring, ranking
src/store.js         JSON dedupe store
src/report.js        CSV, retainer-grouped digest, webhook push
```
