"""Tests for the rules that keep the process honest."""
import sqlite3
from datetime import date

import pandas as pd
import pytest

from tradingbots.config import load_yaml, protected_hashes
from tradingbots.data.sessions import to_day_arrays
from tradingbots.data.split import HoldoutLocked, development_days, holdout_days
from tradingbots.data.synthetic import make_bars
from tradingbots.trials.log import count_trials, log_trial


def test_incomplete_days_are_skipped_and_reported():
    bars = make_bars(n_days=5, seed=1)
    days, skipped = to_day_arrays(bars.drop(bars.index[400]))      # one bar missing on day 2
    assert len(days) == 4 and len(skipped) == 1
    assert "389 bars" in skipped[0][1]


def test_bars_must_be_timezone_aware():
    bars = make_bars(n_days=2, seed=1)
    with pytest.raises(ValueError):
        to_day_arrays(bars.tz_localize(None))


def test_utc_input_is_converted_to_new_york():
    bars = make_bars(n_days=3, seed=1).tz_convert("UTC")
    days, skipped = to_day_arrays(bars)
    assert len(days) == 3 and not skipped


def test_holdout_is_locked_by_default(root, tmp_path):
    gates = load_yaml(root / "config" / "gates.yaml")
    days, _ = to_day_arrays(make_bars(n_days=30, start="2024-04-15", seed=1))
    dev = development_days(days, gates)
    assert dev and max(d.date for d in dev) <= pd.Timestamp("2024-04-30")
    with pytest.raises(HoldoutLocked):
        holdout_days(days, gates)
    with pytest.raises(HoldoutLocked):
        holdout_days(days, gates, unlock=True, reason="  ")
    log = tmp_path / "unlocks.log"
    held = holdout_days(days, gates, unlock=True, reason="finalist run for strategy 1", log_path=log)
    assert min(d.date for d in held) >= pd.Timestamp("2024-05-01")
    assert len(dev) + len(held) == len(days)
    assert "finalist run" in log.read_text()


def test_trial_log_is_append_only(root, tmp_path):
    db = tmp_path / "trials.db"
    hashes = protected_hashes(root / "config")
    common = dict(strategy="intraday_momentum", protected_hashes=hashes, data_start="2010-06-07",
                  data_end="2024-04-30", metrics={"profit_factor": 1.1}, repo=tmp_path)
    log_trial(db, config={"lookback_days": 14}, **common)
    log_trial(db, config={"lookback_days": 14}, **common)      # same config again
    log_trial(db, config={"lookback_days": 20}, **common)
    assert count_trials(db) == 2                               # distinct configs, not rows
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT COUNT(*), SUM(official) FROM trials").fetchone() == (3, 0)
        for statement in ("DELETE FROM trials", "UPDATE trials SET metrics_json = '{}'"):
            with pytest.raises(sqlite3.DatabaseError):
                conn.execute(statement)


def test_profile_loads_and_goes_stale(profile):
    assert (profile.start_balance, profile.profit_target, profile.trailing_drawdown) == (50000, 3000, 2000)
    assert profile.consistency_max_day_share == 0.40 and profile.min_trading_days == 3
    assert profile.daily_loss_limit is None
    assert not profile.is_stale(date(2026, 10, 20))
    assert profile.is_stale(date(2026, 12, 1))
