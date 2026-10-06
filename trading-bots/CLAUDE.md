# Trading bots: rules for Claude Code

A gated backtest machine for rule-based intraday futures strategies. The full
plan is the build brief. Export it from Claude and save it as `docs/brief.md`.

## Rules

1. Build only the current phase. Stop at its acceptance tests and report back.
2. Never edit `config/gates.yaml` or `config/costs.yaml`. Michael edits those.
   Never change a pass mark, holdout date or cost to make a result pass.
3. The holdout is locked. Do not call `holdout_days(unlock=True)` without
   Michael's written go-ahead for that specific finalist.
4. Every backtest run goes in the trial log, including failures.
5. Items marked VERIFY are unconfirmed. Confirm from primary documentation first.
6. Paper mode is the default. No live order code exists before Phase 3.
7. No LLM call sits between a signal and an order.
8. "Nothing passed" is a valid result. Do not loosen rules to fix it.

## Status

Built and tested (40 tests, `python -m pytest`):

- `strategies/intraday_momentum.py`: pure signal logic for Strategy 1.
- `sim/reference.py`: reference bar-by-bar backtester with the fill and cost model.
- `metrics/`: profit factor, Sharpe, drawdown, deflated Sharpe.
- `propsim/`: Tradeify $50k Select evaluation rules and Monte Carlo pass probability.
- `data/`: session cleaning, development and holdout split with the lock.
- `trials/log.py`: append-only trial log.

Not built yet:

- Real data loader (Databento). Nothing has touched real market data.
- NautilusTrader wrapper. The reference simulator is a cross-check, not the engine.
- Pass-mark evaluator, stress runner, morning leaderboard report.
- Funded-stage payout simulation and daily loss limits. The rules are unverified.
- A Topstep rule profile.

## Phase 0, do these first

- [ ] Read the paper (SSRN 4824172). Confirm the boundary and VWAP stop formulas
      in `strategies/intraday_momentum.py`. The code followed a secondary summary.
      Secondary sources match the code. Michael to confirm 4 items from the PDF.
      See `docs/findings/paper-formulas.md`.
- [x] Decide the NautilusTrader version to pin: 1.231.0 on Python 3.12.
      Not installed yet. See `docs/findings/nautilustrader-version.md`.
- [ ] Confirm Databento's volume-roll continuous symbol, dataset start date, and
      the cost of ES and NQ 1-minute bars. Stop and ask if cost exceeds $25.
      Symbol and start date found. Exact cost needs `get_cost` with an API key.
      See `docs/findings/databento-data.md`.
- [x] Write findings to `docs/findings/`.

## Conventions

- Bars are 1-minute, timestamped at the bar START, in America/New_York.
- A session is 390 bars, 9:30 AM to 3:59 PM ET. Incomplete days are skipped and reported.
- Minute offsets count from 9:30. Offset 30 is 10:00 AM.
- A check at offset k reads the close of bar k-1 and fills at the open of bar k.
- Bar highs and lows must be true extremes. See `docs/findings/reference-sim-validation.md`.
- All time rules read data timestamps, never the wall clock.

## Commands

    pip install -e ".[dev]"
    python -m pytest
    python scripts/demo_synthetic.py
