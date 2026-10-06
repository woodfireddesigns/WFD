# Reference simulator validation

Checked on 2026-10-05 against synthetic data only.

## Zero-edge check

On a random walk with no edge, Strategy 1 should earn nothing before costs.

| Run | Days | Trades | Mean per contract | Standard error |
| --- | --- | --- | --- | --- |
| True bar highs and lows, zero cost | 60,000 | 68,136 | $0.004 | $0.42 |
| True bar highs and lows, zero cost | 6,000 | 5,867 | -$0.60 | $1.69 |
| True bar highs and lows, full cost | 6,000 | 5,888 | -$4.63, expected -$4.00 | $1.68 |

Result: no sign of future-data leakage or a generous fill model.

## A trap found on the way

The first version of this check used bars whose low was just min(open, close).
It showed a fake profit of $3.30 per contract, 6 standard errors from zero.

Cause: the test data, not the simulator. Without true lows, a dip that touches
the stop and recovers inside one bar is invisible, so the position survives
when a real stop would have filled. Every stop-based strategy looks better.

What this means for real data:

- Bar highs and lows must be true extremes. Exchange 1-minute bars are.
- Never build bars from sampled closes or from a feed that thins out ticks.
- The delayed feed planned for paper trading may be thinned. Check its bars
  against Databento's for the same day before trusting paper fills.

`make_days_fine` in `data/synthetic.py` builds the correct test data.
`tests/test_zero_edge.py` runs the 6,000-day version on every test run.
