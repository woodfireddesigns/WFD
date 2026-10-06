"""Hand-built scenarios for the Tradeify $50k Select evaluation rules."""
import numpy as np
import pandas as pd
import pytest

from tradingbots.propsim.evaluation import (
    block_bootstrap_indices, monte_carlo, simulate_evaluation,
)
from tradingbots.propsim.profile import Profile

KW = dict(floor_buffer=300.0, risk_per_trade=150.0)


def days(rows):
    """rows: (pnl, min_equity) or (pnl, min_equity, n_trades)."""
    rows = [r if len(r) == 3 else (*r, 1) for r in rows]
    return pd.DataFrame(rows, columns=["pnl", "min_equity", "n_trades"])


def test_three_even_days_pass(profile):
    out = simulate_evaluation(days([(1000, 0)] * 3), profile, **KW)
    assert out == {"outcome": "passed", "days": 3}


def test_target_alone_is_not_enough(profile):
    # $3,000 in two days: fails the 3-day minimum and the 40% consistency rule.
    assert simulate_evaluation(days([(1500, 0)] * 2), profile, **KW)["outcome"] == "timeout"
    # A third traded day at breakeven: 3 days now, but the best day is still 50% of profit.
    assert simulate_evaluation(days([(1500, 0), (1500, 0), (0, 0)]), profile, **KW)["outcome"] == "timeout"
    # $750 more makes the best day exactly 40% of $3,750.
    out = simulate_evaluation(days([(1500, 0), (1500, 0), (0, 0), (750, 0)]), profile, **KW)
    assert out == {"outcome": "passed", "days": 4}


def test_flat_days_do_not_count_as_trading_days(profile):
    rows = [(1000, 0), (1000, 0), (0, 0, 0), (1000, 0)]
    assert simulate_evaluation(days(rows), profile, **KW) == {"outcome": "passed", "days": 4}


def test_intraday_touch_fails_even_if_the_day_ends_green(profile):
    out = simulate_evaluation(days([(100, -2000)]), profile, **KW)
    assert out == {"outcome": "breached", "days": 1}


def test_floor_trails_end_of_day_highs_and_never_drops(profile):
    rows = [
        (1000, 0),        # balance 51,000, floor 49,000
        (-500, -1900),    # low 49,100 holds. Balance 50,500, floor stays 49,000
        (0, -1500),       # low 49,000 touches the floor
    ]
    assert simulate_evaluation(days(rows), profile, **KW) == {"outcome": "breached", "days": 3}
    rows[2] = (0, -1499)
    assert simulate_evaluation(days(rows), profile, **KW)["outcome"] == "timeout"


def test_account_that_cannot_place_a_trade_is_stalled(profile):
    # Balance 48,400, floor 48,000: $400 of room is less than the $300 buffer plus $150 risk.
    out = simulate_evaluation(days([(-1600, -1600), (500, 0)]), profile, **KW)
    assert out == {"outcome": "stalled", "days": 2}


def test_daily_loss_limit_profiles_are_refused_until_modeled(profile):
    dll = Profile(**{**profile.__dict__, "daily_loss_limit": 1000.0})
    with pytest.raises(NotImplementedError):
        simulate_evaluation(days([(0, 0)]), dll, **KW)


def test_bootstrap_blocks_are_consecutive_days():
    idx = block_bootstrap_indices(100, 50, 23, 5, np.random.default_rng(1))
    assert idx.shape == (50, 23) and idx.min() >= 0 and idx.max() < 100
    assert (np.diff(idx[:, :5], axis=1) == 1).all()


def test_monte_carlo_certain_outcomes(profile):
    winners = days([(500, 0)] * 20)
    mc = monte_carlo(winners, profile, paths=500, max_days=60, **KW)
    assert mc.pass_probability == 1.0 and mc.median_days_to_pass == 6     # $3,000 / $500
    losers = days([(-300, -300)] * 20)
    mc = monte_carlo(losers, profile, paths=500, max_days=60, **KW)
    assert mc.pass_probability == 0.0
    assert mc.breach_probability + mc.stall_probability == 1.0


def test_monte_carlo_is_reproducible(profile):
    rng = np.random.default_rng(5)
    pnl = rng.normal(40, 250, 300)
    mixed = days([(p, min(0.0, p) - 50) for p in pnl])
    a = monte_carlo(mixed, profile, paths=2000, seed=11, **KW)
    b = monte_carlo(mixed, profile, paths=2000, seed=11, **KW)
    assert a == b
    total = a.pass_probability + a.breach_probability + a.stall_probability + a.timeout_probability
    assert total == pytest.approx(1.0)
