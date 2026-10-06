# Paper formulas versus the code

Zarattini, Aziz and Barbon (2024), "Beat the Market", SSRN 4824172.
Checked on 2026-10-06.

STATUS: NOT CONFIRMED FROM THE PAPER. The network proxy blocked SSRN, the
university PDF, Concretum, ResearchGate and arXiv. Everything below comes from
secondary sources (CXO Advisory, the SSRN abstract, public replications).
Michael needs to open the PDF and tick the boxes at the bottom.

## What secondary sources say, and whether the code matches

| Rule | Secondary sources | Code | Match |
| --- | --- | --- | --- |
| Typical move | 14-day average of abs(close at minute / that day's open - 1) | `move_matrix`, `typical_move` | Yes |
| Upper bound | max(Open_t, Close_t-1) x (1 + sigma) | `boundaries` | Yes |
| Lower bound | min(Open_t, Close_t-1) x (1 - sigma) | `boundaries` | Yes |
| Band multiplier | None in the paper (equals 1) | `band_mult=1.0`, varied only in stress | Yes |
| Decision times | Every 30 min, 10:00 to 15:30 | offsets 30 to 360 | Yes |
| Exit at close | Flat at 16:00 | close of the 15:59 bar | Yes |
| Trailing stop, longs | max(upper, VWAP) | `target_position` | Yes |
| Trailing stop, shorts | min(lower, VWAP) | `target_position` | Yes |
| Stop timing | Checked only at decision times | checked only at checks | Yes |
| VWAP | "Intraday VWAP". HLC/3 from 9:30 is unconfirmed | HLC/3 from 9:30 | UNCONFIRMED |
| Sample | SPY 1-min, May 2007 to April 2024 | `development_end: 2024-04-30` | Yes |

## Where the code deliberately departs from the paper

These are design choices, not bugs. Listed so nobody mistakes them for the
paper's results.

1. Hard stop. The paper has no hard stop. The code adds a resting stop one
   typical move from entry, used for risk-based sizing. It will cut some
   trades the paper would have held.
2. Sizing. The paper targets 2% daily volatility with up to 4x leverage. The
   code sizes by a fixed dollar risk per trade (`config/risk.yaml`).
3. Reversal. In the paper's base model a stop opens the opposite trade.
   Whether the final VWAP model also reverses is unconfirmed. The code exits,
   then can only re-enter at a later check.
4. Daily stop and the 3-entries cap come from the prop rules, not the paper.
5. Instrument. The paper trades SPY. The code trades MES futures.

The paper's headline numbers (Sharpe 1.33, 19.6% a year) therefore do not
transfer. Treat them as a sanity range, not a target.

## New risk found: the futures roll

Databento's continuous contracts are not back-adjusted
(`databento-data.md`). On a roll day, `Close_t-1` belongs to the old
contract and `Open_t` to the new one. The bounds use max/min of the two, so
the roll gap widens the noise area on that day and suppresses entries.

The typical move is roll-safe, because each day's move is measured against
that same day's open.

Fix in Phase 1, not now: take the prior close from the same contract, or
skip roll days and report them.

## For Michael: check these in the PDF

- [ ] Eq. 1, the sigma definition, matches the table above.
- [ ] VWAP uses (H+L+C)/3 x volume from 9:30, or something else.
- [ ] Whether the final VWAP-stop model reverses into the opposite trade.
- [ ] No hard stop anywhere in the paper.

Concretum Group's site hosts the authors' Python code, which settles the VWAP
question fastest.

Sources:
- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4824172
- https://www.cxoadvisory.com/momentum-investing/complex-intraday-time-series-momentum-strategy-applied-to-spy/
