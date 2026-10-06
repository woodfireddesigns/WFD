"""Strategy 1: intraday momentum on the S&P.

Pure logic only. Arrays in, decisions out. Nothing here imports an engine,
a broker, or a clock, so the same functions serve backtest, paper and live.

Source: Zarattini, Aziz and Barbon (2024), "Beat the Market".
VERIFY the boundary and VWAP stop formulas against the paper itself.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np


@dataclass(frozen=True)
class Params:
    lookback_days: int = 14
    check_interval_min: int = 30
    band_mult: float = 1.0
    first_check_offset: int = 30    # minutes after 9:30 AM ET
    last_check_offset: int = 360    # 3:30 PM ET

    def with_changes(self, **changes) -> "Params":
        return replace(self, **changes)


def check_offsets(p: Params) -> list[int]:
    """Minute offsets from the open at which the strategy may act."""
    first = p.first_check_offset
    k = -(-first // p.check_interval_min)  # ceil
    return list(range(k * p.check_interval_min, p.last_check_offset + 1, p.check_interval_min))


def move_matrix(day_opens: np.ndarray, closes: np.ndarray) -> np.ndarray:
    """|close at minute m / day open - 1| for every day and minute."""
    return np.abs(closes / day_opens[:, None] - 1.0)


def typical_move(moves: np.ndarray, lookback: int) -> np.ndarray:
    """Average move at each minute over the PRIOR `lookback` days.

    Row d uses days d-lookback .. d-1 only. The first `lookback` rows are NaN.
    """
    n_days, n_min = moves.shape
    out = np.full((n_days, n_min), np.nan)
    if n_days <= lookback:
        return out
    csum = np.vstack([np.zeros((1, n_min)), np.cumsum(moves, axis=0)])
    out[lookback:] = (csum[lookback:n_days] - csum[: n_days - lookback]) / lookback
    return out


def boundaries(day_open: float, prev_close: float, sigma: np.ndarray, band_mult: float):
    """Noise area for one day. The gap adjustment widens the area, never narrows it."""
    upper = max(day_open, prev_close) * (1.0 + band_mult * sigma)
    lower = min(day_open, prev_close) * (1.0 - band_mult * sigma)
    return upper, lower


def session_vwap(high: np.ndarray, low: np.ndarray, close: np.ndarray, volume: np.ndarray) -> np.ndarray:
    typical = (high + low + close) / 3.0
    cum_vol = np.cumsum(volume)
    return np.cumsum(typical * volume) / np.where(cum_vol > 0, cum_vol, 1.0)


def target_position(position: int, close: float, upper: float, lower: float, vwap: float) -> int:
    """Desired direction (-1, 0, +1) given the current direction and prices at a check."""
    if position == 0:
        if close > upper:
            return 1
        if close < lower:
            return -1
        return 0
    if position > 0:
        return 0 if close < max(upper, vwap) else 1
    return 0 if close > min(lower, vwap) else -1


def stop_distance(sigma_at_signal: float, price: float, tick: float) -> float:
    """Hard stop distance in points: one typical move, on the tick grid, at least one tick."""
    return max(tick, round(sigma_at_signal * price / tick) * tick)
