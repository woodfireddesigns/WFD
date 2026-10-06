"""A prop firm rule set, loaded from a data file in config/profiles/."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from ..config import load_yaml


@dataclass(frozen=True)
class Profile:
    name: str
    firm: str
    stage: str
    source: str
    verified_on: date
    start_balance: float
    profit_target: float
    trailing_drawdown: float
    daily_loss_limit: float | None
    consistency_max_day_share: float | None
    min_trading_days: int

    @classmethod
    def load(cls, path: str | Path) -> "Profile":
        raw = load_yaml(path)
        return cls(
            name=raw["name"],
            firm=raw["firm"],
            stage=raw["stage"],
            source=raw["source"],
            verified_on=date.fromisoformat(str(raw["verified_on"])),
            start_balance=float(raw["start_balance"]),
            profit_target=float(raw["profit_target"]),
            trailing_drawdown=float(raw["trailing_drawdown"]),
            daily_loss_limit=None if raw.get("daily_loss_limit") is None else float(raw["daily_loss_limit"]),
            consistency_max_day_share=(
                None if raw.get("consistency_max_day_share") is None
                else float(raw["consistency_max_day_share"])
            ),
            min_trading_days=int(raw.get("min_trading_days", 1)),
        )

    def is_stale(self, today: date, max_age_days: int = 30) -> bool:
        """Live mode must refuse to start on a stale profile. Rules change often."""
        return (today - self.verified_on).days > max_age_days
