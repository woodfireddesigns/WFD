"""Known-answer tests. Expected values are worked out by hand in each test."""
import numpy as np
import pandas as pd
import pytest

from conftest import day_from_path, ramp_path
from tradingbots.data.sessions import to_day_arrays
from tradingbots.data.synthetic import make_bars
from tradingbots.sim.reference import Costs, Risk, run_backtest
from tradingbots.strategies.intraday_momentum import Params

P, C = Params(), Costs()
ENTRY = 5000 + 40 * 30 / 390 + 0.25        # open of the 10:00 bar plus one tick
STOP = ENTRY - 1.5                         # one typical move at 10:00, on the tick grid


def test_trend_day_long_held_to_close(tent_history):
    days = tent_history + [day_from_path("2023-01-20", ramp_path())]
    res = run_backtest(days, P, C, Risk())
    assert len(res.trades) == 1 and len(res.daily) == 1
    t = res.trades.iloc[0]
    # Signal at 10:00: close 5003.08 is above the 5001.54 boundary. Fill next bar.
    assert (t.side, t.entry_bar, t.exit_reason) == (1, 30, "close")
    assert t.qty == 5                       # $150 / (1.5 pts x $5) = 20, capped at 5
    assert t.entry_px == pytest.approx(ENTRY)
    assert t.stop_px == pytest.approx(STOP)
    assert t.exit_px == pytest.approx(5040 - 0.25)
    expected = (5039.75 - ENTRY) * 5 * 5.0 - 5 * 1.50
    assert t.net == pytest.approx(expected)
    assert res.daily.pnl.iloc[0] == pytest.approx(expected)
    assert res.daily.min_equity.iloc[0] <= 0


def _crash_day(open_after: float, floor_price: float):
    p = ramp_path()
    day = day_from_path("2023-01-20", p)
    o, h, l, c = day.open.copy(), day.high.copy(), day.low.copy(), day.close.copy()
    o[31:], c[31:], l[31:], h[31:] = floor_price, floor_price, floor_price, floor_price
    o[31] = open_after
    h[31] = max(open_after, floor_price)
    return type(day)(day.date, o, h, l, c, day.volume)


def test_stop_fills_at_stop_price_minus_one_tick(tent_history):
    day = _crash_day(open_after=5000 + 40 * 31 / 390, floor_price=4990.0)
    res = run_backtest(tent_history + [day], P, C, Risk(max_entries_per_day=1))
    t = res.trades.iloc[0]
    assert (t.exit_reason, t.exit_bar) == ("stop", 31)
    assert t.exit_px == pytest.approx(STOP - 0.25)
    assert t.net == pytest.approx((STOP - 0.25 - ENTRY) * 25 - 7.5)   # -51.25
    assert res.daily.min_equity.iloc[0] <= res.daily.pnl.iloc[0]


def test_stop_gap_fills_at_the_open_not_the_stop(tent_history):
    day = _crash_day(open_after=4995.0, floor_price=4990.0)
    res = run_backtest(tent_history + [day], P, C, Risk(max_entries_per_day=1))
    t = res.trades.iloc[0]
    assert t.exit_reason == "stop"
    assert t.exit_px == pytest.approx(4995.0 - 0.25)


def test_daily_stop_halts_new_entries(tent_history):
    day = _crash_day(open_after=4900.0, floor_price=4900.0)   # gap far through the stop
    res = run_backtest(tent_history + [day], P, C, Risk())
    assert len(res.trades) == 1                               # price sits below the lower boundary all day
    assert res.daily.pnl.iloc[0] < -400
    same_day_no_halt = run_backtest(tent_history + [day], P, C, Risk(daily_stop=1e9))
    assert len(same_day_no_halt.trades) > 1                   # without the halt it would re-enter short


def test_trade_skipped_when_one_contract_exceeds_risk(tent_history):
    days = tent_history + [day_from_path("2023-01-20", ramp_path())]
    res = run_backtest(days, P, C, Risk(risk_per_trade=5.0))
    assert len(res.trades) == 0 and res.signals > 0
    assert res.skipped_trades == res.signals and res.skipped_share == 1.0


def test_no_trades_before_lookback_is_full(tent_history):
    res = run_backtest(tent_history, P, C, Risk())
    assert len(res.daily) == 0 and len(res.trades) == 0


def test_entry_delay_moves_the_fill_bar(tent_history):
    days = tent_history + [day_from_path("2023-01-20", ramp_path())]
    res = run_backtest(days, P, C, Risk(), entry_delay_bars=1)
    assert res.trades.iloc[0].entry_bar == 31


@pytest.fixture(scope="module")
def synthetic_days():
    days, skipped = to_day_arrays(make_bars(n_days=80, trend_day_prob=0.3, seed=3))
    assert not skipped
    return days


def test_same_inputs_same_outputs(synthetic_days):
    a = run_backtest(synthetic_days, P, C, Risk())
    b = run_backtest(synthetic_days, P, C, Risk())
    pd.testing.assert_frame_equal(a.trades, b.trades)
    pd.testing.assert_frame_equal(a.daily, b.daily)


def test_accounting_invariants(synthetic_days):
    res = run_backtest(synthetic_days, P, C, Risk())
    assert len(res.trades) > 10
    assert len(res.daily) == len(synthetic_days) - P.lookback_days
    # Daily P&L is exactly the sum of that day's trades.
    by_day = res.trades.groupby("date")["net"].sum()
    daily = res.daily.set_index("date")["pnl"]
    np.testing.assert_allclose(daily[by_day.index].to_numpy(), by_day.to_numpy())
    assert (res.daily.min_equity <= res.daily.pnl + 1e-9).all()
    assert (res.daily.min_equity <= 1e-9).all()
    assert (res.trades.qty <= 5).all() and (res.trades.qty >= 1).all()
    assert res.trades.groupby("date").size().max() <= 3
    # Every stop exit is on the losing side of entry.
    stops = res.trades[res.trades.exit_reason == "stop"]
    assert ((stops.exit_px - stops.entry_px) * stops.side < 0).all()


def test_doubling_costs_lowers_profit(synthetic_days):
    base = run_backtest(synthetic_days, P, C, Risk())
    stressed = run_backtest(synthetic_days, P, C, Risk(), cost_multiplier=2.0)
    assert stressed.daily.pnl.sum() < base.daily.pnl.sum()
