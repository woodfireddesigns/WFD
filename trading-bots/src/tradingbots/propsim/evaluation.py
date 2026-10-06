"""Evaluation-stage simulator and Monte Carlo pass probability.

Each trading day is one record: net P&L, the worst intraday mark-to-market
point (min_equity, zero or negative, relative to the day's start), and
whether any trade happened.

Rules applied, in order, each day:
1. Bot's pre-trade check. If the room above the floor is smaller than
   floor_buffer + risk_per_trade, the bot will not trade. An account that
   cannot trade can never recover, so it is counted as STALLED.
2. Trailing floor, real time. If balance + min_equity touches the floor,
   the account is BREACHED.
3. End of day. Balance updates, the floor trails the highest end-of-day
   balance, and the pass conditions are checked.

Not modeled yet: daily loss limits, funded-stage payouts, drawdown locks.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .profile import Profile

ACTIVE, PASSED, BREACHED, STALLED = 0, 1, 2, 3
STATUS_NAMES = {ACTIVE: "timeout", PASSED: "passed", BREACHED: "breached", STALLED: "stalled"}


def simulate_paths(
    pnl: np.ndarray,
    min_equity: np.ndarray,
    traded: np.ndarray,
    profile: Profile,
    *,
    floor_buffer: float,
    risk_per_trade: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Run many paths at once. Inputs are (paths, days). Returns (status, end_day).

    end_day is the 1-based day the path ended on, or the horizon for timeouts.
    """
    if profile.daily_loss_limit is not None:
        raise NotImplementedError("daily loss limits are not modeled yet")
    pnl = np.atleast_2d(np.asarray(pnl, dtype=float))
    min_equity = np.atleast_2d(np.asarray(min_equity, dtype=float))
    traded = np.atleast_2d(np.asarray(traded)).astype(bool)
    n_paths, n_days = pnl.shape

    balance = np.full(n_paths, profile.start_balance)
    floor = balance - profile.trailing_drawdown
    high = balance.copy()
    best_day = np.zeros(n_paths)
    days_traded = np.zeros(n_paths, dtype=int)
    status = np.full(n_paths, ACTIVE)
    end_day = np.full(n_paths, n_days)
    need = floor_buffer + risk_per_trade

    for t in range(n_days):
        active = status == ACTIVE
        if not active.any():
            break

        stalled = active & (balance - floor < need)
        status[stalled] = STALLED
        end_day[stalled] = t + 1
        active &= ~stalled

        breached = active & (balance + min_equity[:, t] <= floor)
        status[breached] = BREACHED
        end_day[breached] = t + 1
        active &= ~breached

        balance = np.where(active, balance + pnl[:, t], balance)
        best_day = np.where(active, np.maximum(best_day, pnl[:, t]), best_day)
        days_traded = np.where(active & traded[:, t], days_traded + 1, days_traded)
        high = np.where(active, np.maximum(high, balance), high)
        floor = high - profile.trailing_drawdown

        profit = balance - profile.start_balance
        ok = active & (profit >= profile.profit_target) & (days_traded >= profile.min_trading_days)
        if profile.consistency_max_day_share is not None:
            ok &= best_day <= profile.consistency_max_day_share * profit
        status[ok] = PASSED
        end_day[ok] = t + 1

    return status, end_day


def simulate_evaluation(daily, profile: Profile, *, floor_buffer: float, risk_per_trade: float) -> dict:
    """One real sequence of days, in order. `daily` has pnl, min_equity, n_trades columns."""
    status, end_day = simulate_paths(
        daily["pnl"].to_numpy()[None, :],
        daily["min_equity"].to_numpy()[None, :],
        (daily["n_trades"].to_numpy() > 0)[None, :],
        profile,
        floor_buffer=floor_buffer,
        risk_per_trade=risk_per_trade,
    )
    return {"outcome": STATUS_NAMES[int(status[0])], "days": int(end_day[0])}


@dataclass(frozen=True)
class MonteCarloResult:
    paths: int
    horizon_days: int
    pass_probability: float
    breach_probability: float
    stall_probability: float
    timeout_probability: float
    median_days_to_pass: float
    p90_days_to_pass: float

    def as_dict(self) -> dict:
        return dict(self.__dict__)


def block_bootstrap_indices(n_records: int, n_paths: int, n_days: int, block: int, rng) -> np.ndarray:
    """Resample days in consecutive blocks so winning and losing streaks survive."""
    if n_records < block:
        raise ValueError(f"need at least {block} daily records, got {n_records}")
    n_blocks = -(-n_days // block)
    starts = rng.integers(0, n_records - block + 1, size=(n_paths, n_blocks))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]).reshape(n_paths, -1)
    return idx[:, :n_days]


def monte_carlo(
    daily,
    profile: Profile,
    *,
    floor_buffer: float,
    risk_per_trade: float,
    paths: int = 10_000,
    block_days: int = 5,
    max_days: int = 250,
    seed: int = 0,
) -> MonteCarloResult:
    rng = np.random.default_rng(seed)
    pnl = daily["pnl"].to_numpy(dtype=float)
    mn = daily["min_equity"].to_numpy(dtype=float)
    traded = daily["n_trades"].to_numpy() > 0
    idx = block_bootstrap_indices(len(pnl), paths, max_days, block_days, rng)
    status, end_day = simulate_paths(
        pnl[idx], mn[idx], traded[idx], profile,
        floor_buffer=floor_buffer, risk_per_trade=risk_per_trade,
    )
    passed = status == PASSED
    days = end_day[passed]
    return MonteCarloResult(
        paths=paths,
        horizon_days=max_days,
        pass_probability=float(passed.mean()),
        breach_probability=float((status == BREACHED).mean()),
        stall_probability=float((status == STALLED).mean()),
        timeout_probability=float((status == ACTIVE).mean()),
        median_days_to_pass=float(np.median(days)) if days.size else float("nan"),
        p90_days_to_pass=float(np.percentile(days, 90)) if days.size else float("nan"),
    )
