"""Development and holdout split. The holdout is locked by default."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .sessions import DayBars


class HoldoutLocked(RuntimeError):
    pass


def development_days(days: list[DayBars], gates: dict) -> list[DayBars]:
    end = pd.Timestamp(gates["data_split"]["development_end"])
    return [d for d in days if d.date <= end]


def holdout_days(
    days: list[DayBars],
    gates: dict,
    *,
    unlock: bool = False,
    reason: str = "",
    log_path: str | Path = "trials/holdout_unlocks.log",
    warmup_days: int = 0,
) -> list[DayBars]:
    """Return holdout days. Requires unlock=True and a reason. Every unlock is logged.

    warmup_days prepends that many development days so lookback windows are full.
    Results must only be measured on days at or after holdout_start.
    """
    if not unlock or not reason.strip():
        raise HoldoutLocked("holdout is locked: pass unlock=True and a written reason")
    start = pd.Timestamp(gates["data_split"]["holdout_start"])
    first = next((i for i, d in enumerate(days) if d.date >= start), len(days))
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(f"{datetime.now(timezone.utc).isoformat()}\t{reason.strip()}\n")
    return days[max(0, first - warmup_days):]
