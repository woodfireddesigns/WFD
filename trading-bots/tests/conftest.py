from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from tradingbots.data.sessions import BARS_PER_DAY, DayBars
from tradingbots.propsim.profile import Profile

ROOT = Path(__file__).resolve().parents[1]


def day_from_path(date: str, p: np.ndarray, volume: float = 1000.0) -> DayBars:
    """Build a day from 391 price points: bar i opens at p[i] and closes at p[i+1]."""
    assert len(p) == BARS_PER_DAY + 1
    o, c = p[:-1].copy(), p[1:].copy()
    return DayBars(pd.Timestamp(date), o, np.maximum(o, c), np.minimum(o, c), c,
                   np.full(BARS_PER_DAY, volume))


def tent_path(base: float = 5000.0, peak: float = 10.0) -> np.ndarray:
    """Rises `peak` points by midday, back to base by the close."""
    j = np.arange(BARS_PER_DAY + 1)
    return base + peak * np.where(j <= 195, j / 195.0, (390 - j) / 195.0)


def ramp_path(base: float = 5000.0, rise: float = 40.0) -> np.ndarray:
    return base + rise * np.arange(BARS_PER_DAY + 1) / 390.0


@pytest.fixture
def tent_history() -> list[DayBars]:
    dates = pd.bdate_range("2023-01-02", periods=14)
    return [day_from_path(str(d.date()), tent_path()) for d in dates]


@pytest.fixture
def root() -> Path:
    return ROOT


@pytest.fixture
def profile() -> Profile:
    return Profile.load(ROOT / "config" / "profiles" / "tradeify_select_50k_eval.yaml")
