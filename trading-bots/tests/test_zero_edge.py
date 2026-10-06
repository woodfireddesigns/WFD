"""Leakage check: on a random walk with no edge, the strategy must make nothing.

If this fails, the simulator is using information from the future or the
fill model is too generous. A 60,000-day run of the same check is recorded
in docs/findings/reference-sim-validation.md.
"""
import numpy as np

from tradingbots.data.synthetic import make_days_fine
from tradingbots.sim.reference import Costs, Risk, run_backtest
from tradingbots.strategies.intraday_momentum import Params


def test_zero_edge_walk_earns_nothing_before_costs_and_loses_costs_after():
    days = make_days_fine(6000, seed=2026)
    free = run_backtest(days, Params(), Costs(), Risk(), cost_multiplier=0.0)
    per_contract = (free.trades.gross / free.trades.qty).to_numpy()
    assert per_contract.size > 4000
    se = per_contract.std(ddof=1) / np.sqrt(per_contract.size)
    assert abs(per_contract.mean()) < 3 * se

    paid = run_backtest(days, Params(), Costs(), Risk())
    net = (paid.trades.net / paid.trades.qty).to_numpy()
    se = net.std(ddof=1) / np.sqrt(net.size)
    # $1.50 commission plus two ticks of slippage at $1.25 each.
    assert abs(net.mean() - (-4.0)) < 3 * se
