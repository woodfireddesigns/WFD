"""Scoring metrics. Win rate is deliberately not the headline number."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def profit_factor(trade_net: np.ndarray) -> float:
    trade_net = np.asarray(trade_net, dtype=float)
    if trade_net.size == 0:
        return float("nan")
    gains = trade_net[trade_net > 0].sum()
    losses = -trade_net[trade_net < 0].sum()
    if losses == 0:
        return float("inf") if gains > 0 else float("nan")
    return float(gains / losses)


def sharpe(daily_pnl: np.ndarray, periods: int = TRADING_DAYS) -> float:
    """Annualized Sharpe on daily dollar P&L, flat days included."""
    daily_pnl = np.asarray(daily_pnl, dtype=float)
    if daily_pnl.size < 2:
        return float("nan")
    sd = daily_pnl.std(ddof=1)
    if sd == 0:
        return float("nan")
    return float(daily_pnl.mean() / sd * math.sqrt(periods))


def max_drawdown(daily_pnl: np.ndarray, min_equity: np.ndarray | None = None) -> float:
    """Worst peak-to-trough loss in dollars, as a positive number.

    With min_equity (each day's worst intraday point), the trough is measured
    intraday, which is what a real-time trailing drawdown sees.
    """
    daily_pnl = np.asarray(daily_pnl, dtype=float)
    if daily_pnl.size == 0:
        return 0.0
    cum = np.cumsum(daily_pnl)
    start_of_day = np.concatenate([[0.0], cum[:-1]])
    peak = np.maximum.accumulate(np.concatenate([[0.0], cum]))[:-1]
    peak = np.maximum(peak, 0.0)
    trough = cum if min_equity is None else start_of_day + np.asarray(min_equity, dtype=float)
    return float(max(0.0, (peak - trough).max()))


def yearly_stats(daily: pd.DataFrame) -> dict:
    by_year = daily.groupby(pd.to_datetime(daily["date"]).dt.year)["pnl"].sum()
    total = by_year.sum()
    return {
        "profitable_year_share": float((by_year > 0).mean()) if len(by_year) else float("nan"),
        "max_single_year_profit_share": float(by_year.max() / total) if total > 0 else float("nan"),
        "by_year": {int(k): float(v) for k, v in by_year.items()},
    }


def summarize(trades: pd.DataFrame, daily: pd.DataFrame) -> dict:
    net = trades["net"].to_numpy(dtype=float)
    pnl = daily["pnl"].to_numpy(dtype=float)
    out = {
        "trades": int(net.size),
        "days": int(pnl.size),
        "net_profit": float(pnl.sum()),
        "profit_factor": profit_factor(net),
        "sharpe": sharpe(pnl),
        "max_drawdown_eod": max_drawdown(pnl),
        "max_drawdown_intraday": max_drawdown(pnl, daily["min_equity"].to_numpy(dtype=float)),
        "win_rate": float((net > 0).mean()) if net.size else float("nan"),
        "avg_trade": float(net.mean()) if net.size else float("nan"),
    }
    out.update(yearly_stats(daily))
    return out
