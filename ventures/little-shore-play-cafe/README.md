# Little Shore Play Cafe: founder simulation

A full run of the [founder-skill](https://github.com/Jakeschincariol/founder-skill) pack (all 11 skills) on Little Shore Play Cafe, run Oct 8, 2026.

**Computed verdict: Not yet.** Year 1 is a $4,012 operating loss, and 24 of 100 simulated buyers buy against a 25% bar. Unit economics ($17.05 contribution per paying family visit) and capacity pass.

Start here:

- `founder/summary.md`: half a page, the verdict and the one thing to do this week
- `founder/one-pager.md`: for family, sponsors, lenders (fill the bracketed ask)
- `founder/business-plan.md`: everything, compiled by the pack's `compile.py`
- `simulation-report.html`: the visual summary

Inside `founder/`: `board/` (3 lens memos), `competitors.md/.csv`, `panel/` (100 buyers, seed 2026) and `panel-v2/` (20-buyer offer re-test), `pricing.md` + curves, `offer.md`, `cfo.md` + `cfo-sources.md` + `numbers.json`, `model/` (revenue-mix bridge and scenarios), `marketing.md`, `brand.md`, `ops.md`, `launch.md`.

Re-run the numbers (point `<founder-skill>` at a clone of that repo):

```bash
python3 founder/model/mix.py founder/model/scenario-v2-recommended.json --out founder/numbers.json
python3 <founder-skill>/skills/founder-cfo/unit_economics.py founder/numbers.json
python3 <founder-skill>/skills/founder-plan/compile.py --dir founder --check
```

Buyers are simulated, competitor facts come from linked search excerpts, and most costs are estimates. Not financial, legal or tax advice. Internal planning material: keep it off the public site.
