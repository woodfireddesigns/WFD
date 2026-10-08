# Little Shore Play Cafe: founder simulation

A full run of the [founder-skill](https://github.com/Jakeschincariol/founder-skill) pack (all 11 skills) on Little Shore Play Cafe, run Oct 8, 2026.

**Computed verdict: Profitable** (after the Year 1 optimization). Year 1 operating profit $30,290, break-even 29 paying family visits a day against ~106 capacity, 71 of 100 simulated buyers buy. With a $150k loan and $3k/mo owner pay, break-even rises to 40 a day. See `founder/optimization.md`.

Start here:

- `founder/summary.md`: half a page, the verdict and the one thing to do this week
- `founder/optimization.md`: every offer tested, every lever kept or cut, and the guardrails
- `founder/one-pager.md`: for family, sponsors, lenders (fill the bracketed ask)
- `founder/business-plan.md`: everything, compiled by the pack's `compile.py`
- `simulation-report.html`: the visual summary

Inside `founder/`: `board/` (3 lens memos), `competitors.md/.csv`, `panel/` (final 100 buyers, seed 2026), `panel-v1/` (original 100), `panel-v2/`, `panel-v3/`, `round1/`, `round2/` (offer tests), `pricing.md` + curves, `offer.md`, `cfo.md` + `cfo-sources.md` + `numbers.json`, `model/` (revenue-mix bridge and scenarios), `marketing.md`, `brand.md`, `ops.md`, `launch.md`.

Re-run the numbers (point `<founder-skill>` at a clone of that repo):

```bash
python3 founder/model/mix.py founder/model/scenario-v5-final.json --out founder/numbers.json
python3 <founder-skill>/skills/founder-cfo/unit_economics.py founder/numbers.json
python3 <founder-skill>/skills/founder-plan/compile.py --dir founder --check
```

Buyers are simulated, competitor facts come from linked search excerpts, and most costs are estimates. Not financial, legal or tax advice. Internal planning material: keep it off the public site.
