"""Turn 1-minute bars into clean per-day arrays for regular trading hours.

Days that are not a complete 390-bar session are skipped and reported.
Nothing is filled in silently.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

BARS_PER_DAY = 390          # 9:30 AM to 3:59 PM ET, bar timestamp = bar start
SESSION_TZ = "America/New_York"
_COLUMNS = ["open", "high", "low", "close", "volume"]


@dataclass(frozen=True)
class DayBars:
    date: pd.Timestamp
    open: np.ndarray
    high: np.ndarray
    low: np.ndarray
    close: np.ndarray
    volume: np.ndarray


def to_day_arrays(bars: pd.DataFrame) -> tuple[list[DayBars], list[tuple[pd.Timestamp, str]]]:
    """Return (complete days, skipped days with the reason)."""
    if bars.index.tz is None:
        raise ValueError("bars index must be timezone-aware")
    missing = [c for c in _COLUMNS if c not in bars.columns]
    if missing:
        raise ValueError(f"bars missing columns: {missing}")
    if not bars.index.is_unique:
        raise ValueError("duplicate timestamps in bars")

    local = bars.tz_convert(SESSION_TZ).sort_index()
    rth = local.between_time("09:30", "15:59")
    days: list[DayBars] = []
    skipped: list[tuple[pd.Timestamp, str]] = []
    for date, frame in rth.groupby(rth.index.normalize()):
        day = pd.Timestamp(date.date())
        if len(frame) != BARS_PER_DAY:
            skipped.append((day, f"{len(frame)} bars, expected {BARS_PER_DAY}"))
            continue
        offsets = (frame.index.hour * 60 + frame.index.minute) - (9 * 60 + 30)
        if not np.array_equal(np.asarray(offsets), np.arange(BARS_PER_DAY)):
            skipped.append((day, "bars not on the one-minute grid"))
            continue
        values = frame[_COLUMNS].to_numpy(dtype=float)
        if np.isnan(values).any():
            skipped.append((day, "NaN values"))
            continue
        if (values[:, 4] <= 0).any():
            skipped.append((day, "zero-volume bars"))
            continue
        days.append(DayBars(day, values[:, 0], values[:, 1], values[:, 2], values[:, 3], values[:, 4]))
    return days, skipped
