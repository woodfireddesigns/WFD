"""Reference bar-by-bar backtester for Strategy 1.

This is a small, readable simulator used to test the strategy logic and the
fill model, and later to cross-check the NautilusTrader wrapper. It is not
the production engine.

Fill model (config/costs.yaml):
- A signal at a check fills at the OPEN of the next bar, one tick against us.
- A resting stop triggers when a bar trades through it and fills at the worse
  of the stop price and that bar's open, one tick against us.
- No fills inside the bar that produced the signal.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from ..data.sessions import BARS_PER_DAY, DayBars
from ..strategies import intraday_momentum as im

LAST_BAR = BARS_PER_DAY - 1


@dataclass(frozen=True)
class Costs:
    point_value: float = 5.0
    tick_size: float = 0.25
    commission_round_turn: float = 1.50
    slippage_ticks_per_side: float = 1.0

    @classmethod
    def from_config(cls, cfg: dict) -> "Costs":
        return cls(
            point_value=float(cfg["instrument"]["point_value"]),
            tick_size=float(cfg["instrument"]["tick_size"]),
            commission_round_turn=float(cfg["commission_round_turn"]),
            slippage_ticks_per_side=float(cfg["slippage_ticks_per_side"]),
        )


@dataclass(frozen=True)
class Risk:
    risk_per_trade: float = 150.0
    daily_stop: float = 400.0
    max_entries_per_day: int = 3
    contract_cap: int = 5

    @classmethod
    def from_config(cls, cfg: dict) -> "Risk":
        return cls(
            risk_per_trade=float(cfg["risk_per_trade"]),
            daily_stop=float(cfg["daily_stop"]),
            max_entries_per_day=int(cfg["max_entries_per_day"]),
            contract_cap=int(cfg["contract_cap"]),
        )


@dataclass
class BacktestResult:
    trades: pd.DataFrame      # one row per round trip
    daily: pd.DataFrame       # one row per tradable day, including flat days
    signals: int              # entry signals seen
    skipped_trades: int       # signals skipped because one contract exceeded the risk budget

    @property
    def skipped_share(self) -> float:
        return self.skipped_trades / self.signals if self.signals else 0.0


def run_backtest(
    days: list[DayBars],
    params: im.Params,
    costs: Costs,
    risk: Risk,
    *,
    cost_multiplier: float = 1.0,
    entry_delay_bars: int = 0,
) -> BacktestResult:
    pv = costs.point_value
    tick = costs.tick_size
    slip = costs.slippage_ticks_per_side * tick * cost_multiplier
    comm_side = costs.commission_round_turn / 2.0 * cost_multiplier
    checks = set(im.check_offsets(params))
    lookback = params.lookback_days

    opens = np.array([d.open[0] for d in days])
    closes = np.vstack([d.close for d in days]) if days else np.empty((0, BARS_PER_DAY))
    sigma_all = im.typical_move(im.move_matrix(opens, closes), lookback)

    trades: list[dict] = []
    daily: list[dict] = []
    signals = 0
    skipped = 0

    for d in range(lookback, len(days)):
        day = days[d]
        o, h, l, c = day.open, day.high, day.low, day.close
        sigma = sigma_all[d]
        upper, lower = im.boundaries(o[0], days[d - 1].close[-1], sigma, params.band_mult)
        vwap = im.session_vwap(h, l, c, day.volume)

        pos = 0            # direction: -1, 0, +1
        qty = 0
        entry_px = stop_px = 0.0
        entry_bar = -1
        entries = 0
        realized = 0.0     # net of commission
        day_min = 0.0      # worst mark-to-market point of the day
        halted = False
        pending: dict | None = None
        n_trades = 0

        def close_trade(px: float, reason: str, bar: int) -> None:
            nonlocal pos, qty, realized, n_trades
            gross = (px - entry_px) * pos * qty * pv
            commission = 2 * comm_side * qty
            realized += gross - comm_side * qty
            trades.append(
                {
                    "date": day.date,
                    "side": pos,
                    "qty": qty,
                    "entry_bar": entry_bar,
                    "exit_bar": bar,
                    "entry_px": entry_px,
                    "exit_px": px,
                    "stop_px": stop_px,
                    "exit_reason": reason,
                    "gross": gross,
                    "commission": commission,
                    "net": gross - commission,
                }
            )
            n_trades += 1
            pos = 0
            qty = 0

        for i in range(BARS_PER_DAY):
            # 1. Orders scheduled for this bar's open.
            if pending is not None and pending["bar"] == i:
                if pending["kind"] == "entry" and pos == 0 and not halted:
                    pos = pending["side"]
                    qty = pending["qty"]
                    entry_px = o[i] + pos * slip
                    stop_px = entry_px - pos * pending["dist"]
                    entry_bar = i
                    realized -= comm_side * qty
                    entries += 1
                elif pending["kind"] == "exit" and pos != 0:
                    close_trade(o[i] - pos * slip, pending["reason"], i)
                pending = None

            # 2. Resting stop.
            if pos > 0 and l[i] <= stop_px:
                close_trade(min(stop_px, o[i]) - slip, "stop", i)
            elif pos < 0 and h[i] >= stop_px:
                close_trade(max(stop_px, o[i]) + slip, "stop", i)

            # 3. Worst point of this bar, for the trailing-floor check.
            if pos != 0:
                worst = l[i] if pos > 0 else h[i]
                day_min = min(day_min, realized + (worst - entry_px) * pos * qty * pv)
            day_min = min(day_min, realized)

            # 4. Session close.
            if i == LAST_BAR:
                if pos != 0:
                    close_trade(c[i] - pos * slip, "close", i)
                    day_min = min(day_min, realized)
                break

            # 5. Bot's own daily stop, judged on the bar close.
            if not halted:
                equity = realized + ((c[i] - entry_px) * pos * qty * pv if pos else 0.0)
                if equity <= -risk.daily_stop:
                    halted = True
                    pending = {"kind": "exit", "reason": "daily_stop", "bar": i + 1} if pos else None

            # 6. Strategy check at the close of this bar.
            if (i + 1) in checks and not halted and pending is None:
                want = im.target_position(pos, c[i], upper[i], lower[i], vwap[i])
                if pos == 0 and want != 0 and entries < risk.max_entries_per_day:
                    signals += 1
                    dist = im.stop_distance(sigma[i], c[i], tick)
                    size = min(int(risk.risk_per_trade // (dist * pv)), risk.contract_cap)
                    if size < 1:
                        skipped += 1
                    else:
                        bar = i + 1 + entry_delay_bars
                        if bar <= LAST_BAR:
                            pending = {"kind": "entry", "side": want, "qty": size, "dist": dist, "bar": bar}
                elif pos != 0 and want == 0:
                    pending = {"kind": "exit", "reason": "signal", "bar": i + 1}

        daily.append({"date": day.date, "pnl": realized, "min_equity": day_min, "n_trades": n_trades})

    trade_cols = ["date", "side", "qty", "entry_bar", "exit_bar", "entry_px", "exit_px",
                  "stop_px", "exit_reason", "gross", "commission", "net"]
    return BacktestResult(
        trades=pd.DataFrame(trades, columns=trade_cols),
        daily=pd.DataFrame(daily, columns=["date", "pnl", "min_equity", "n_trades"]),
        signals=signals,
        skipped_trades=skipped,
    )
