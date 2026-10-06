"""Synthetic 1-minute bars for tests and demos only.

Results on this data say nothing about real markets.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .sessions import BARS_PER_DAY, SESSION_TZ


def make_bars(
    n_days: int = 120,
    start: str = "2023-01-02",
    start_price: float = 5000.0,
    daily_vol: float = 0.009,
    trend_day_prob: float = 0.0,
    trend_size: float = 0.008,
    tick: float = 0.25,
    wick_ticks: float = 1.0,
    seed: int = 7,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(start, periods=n_days)
    frames = []
    prev_close = start_price
    for date in dates:
        day_open = prev_close * (1 + rng.normal(0, daily_vol * 0.3))
        steps = rng.normal(0, daily_vol / np.sqrt(BARS_PER_DAY), BARS_PER_DAY)
        if rng.random() < trend_day_prob:
            steps += rng.choice([-1.0, 1.0]) * trend_size / BARS_PER_DAY
        close = day_open * np.exp(np.cumsum(steps))
        close = np.round(close / tick) * tick
        open_ = np.empty(BARS_PER_DAY)
        open_[0] = np.round(day_open / tick) * tick
        open_[1:] = close[:-1]
        wiggle = np.abs(rng.normal(0, tick * wick_ticks, BARS_PER_DAY))
        high = np.round((np.maximum(open_, close) + wiggle) / tick) * tick
        low = np.round((np.minimum(open_, close) - wiggle) / tick) * tick
        shape = 1.5 - np.sin(np.linspace(0, np.pi, BARS_PER_DAY))
        volume = np.maximum(1, rng.poisson(800 * shape))
        index = pd.date_range(
            f"{date.date()} 09:30", periods=BARS_PER_DAY, freq="1min", tz=SESSION_TZ
        )
        frames.append(
            pd.DataFrame(
                {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
                index=index,
            )
        )
        prev_close = close[-1]
    return pd.concat(frames)


def make_days_fine(
    n_days: int,
    seed: int = 0,
    sub_steps: int = 30,
    start_price: float = 5000.0,
    daily_vol: float = 0.009,
    tick: float = 0.25,
):
    """Zero-edge random walk with TRUE bar highs and lows, as DayBars.

    Each minute is built from `sub_steps` smaller moves, so the high and low
    are real extremes of the path. Use this, not make_bars, to test for
    future-data leakage. A walk whose lows are just min(open, close) hides
    dips that touched a stop and recovered, which flatters any stop-based
    strategy by a few dollars per contract.
    """
    from .sessions import DayBars

    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("1990-01-01", periods=n_days)
    volume = np.full(BARS_PER_DAY, 1000.0)
    days = []
    prev = start_price

    def on_grid(a):
        return np.round(a / tick) * tick

    for k in range(n_days):
        day_open = prev * (1 + rng.normal(0, daily_vol * 0.3))
        steps = rng.normal(0, daily_vol / np.sqrt(BARS_PER_DAY * sub_steps), BARS_PER_DAY * sub_steps)
        path = (day_open * np.exp(np.cumsum(steps))).reshape(BARS_PER_DAY, sub_steps)
        close = path[:, -1]
        open_ = np.empty(BARS_PER_DAY)
        open_[0] = day_open
        open_[1:] = close[:-1]
        high = np.maximum(path.max(axis=1), open_)
        low = np.minimum(path.min(axis=1), open_)
        days.append(DayBars(dates[k], on_grid(open_), on_grid(high), on_grid(low), on_grid(close), volume))
        prev = close[-1] if 0.4 * start_price < close[-1] < 2.5 * start_price else start_price
    return days
