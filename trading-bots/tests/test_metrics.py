import math

import numpy as np
import pandas as pd
import pytest

from tradingbots.metrics import core
from tradingbots.metrics.deflated import deflated_sharpe, expected_max_sharpe, probabilistic_sharpe


def test_profit_factor():
    assert core.profit_factor([100, -50, 50]) == 3.0
    assert core.profit_factor([10, 20]) == float("inf")
    assert math.isnan(core.profit_factor([]))


def test_sharpe_matches_hand_calculation():
    x = np.array([1.0, 2.0, 3.0, 4.0])
    assert core.sharpe(x) == pytest.approx(2.5 / x.std(ddof=1) * math.sqrt(252))


def test_max_drawdown_end_of_day_and_intraday():
    pnl = [100, -50, -100, 200]
    assert core.max_drawdown(pnl) == 150                       # peak 100, trough -50
    # Day 3 dips 200 below its own start of 50: intraday trough is -150 against a peak of 100.
    assert core.max_drawdown(pnl, [0, -50, -200, 0]) == 250
    assert core.max_drawdown([10, 10, 10]) == 0


def test_yearly_stats():
    daily = pd.DataFrame({"date": pd.to_datetime(["2021-03-01", "2022-03-01", "2023-03-01"]),
                          "pnl": [300.0, -100.0, 200.0]})
    stats = core.yearly_stats(daily)
    assert stats["profitable_year_share"] == pytest.approx(2 / 3)
    assert stats["max_single_year_profit_share"] == pytest.approx(0.75)


def test_more_trials_raise_the_bar():
    assert expected_max_sharpe(1, 0.05) == 0.0
    assert expected_max_sharpe(100, 0.05) > expected_max_sharpe(10, 0.05) > 0
    x = np.random.default_rng(2).normal(0.08, 1.0, 1500)
    one = deflated_sharpe(x, 1, 0.03)
    many = deflated_sharpe(x, 200, 0.03)
    assert 0 < many < one < 1
    sr = x.mean() / x.std(ddof=1)
    z = (x - x.mean()) / x.std(ddof=0)
    assert one == pytest.approx(probabilistic_sharpe(sr, x.size, (z ** 3).mean(), (z ** 4).mean()))


def test_zero_edge_scores_near_coin_flip():
    x = np.random.default_rng(9).normal(0.0, 1.0, 5000)
    assert 0.05 < deflated_sharpe(x, 1, 0.0) < 0.95
