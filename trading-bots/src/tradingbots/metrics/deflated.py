"""Deflated Sharpe ratio (Bailey and Lopez de Prado, 2014).

Answers: given how many configurations were tried, how likely is it that the
best one's Sharpe is real and not the luckiest draw? All Sharpe inputs here
are PER PERIOD (daily), not annualized.
"""
from __future__ import annotations

import math
from statistics import NormalDist

import numpy as np

_EULER = 0.5772156649015329
_N = NormalDist()


def expected_max_sharpe(n_trials: int, trial_sharpe_std: float) -> float:
    """Sharpe you would expect from the best of n zero-edge trials."""
    if n_trials <= 1 or trial_sharpe_std <= 0:
        return 0.0
    return trial_sharpe_std * (
        (1 - _EULER) * _N.inv_cdf(1 - 1.0 / n_trials)
        + _EULER * _N.inv_cdf(1 - 1.0 / (n_trials * math.e))
    )


def probabilistic_sharpe(sr: float, n_obs: int, skew: float, kurt: float, benchmark: float = 0.0) -> float:
    """Probability the true per-period Sharpe exceeds the benchmark. kurt is non-excess (normal = 3)."""
    if n_obs < 3:
        return float("nan")
    var = 1 - skew * sr + (kurt - 1) / 4.0 * sr * sr
    if var <= 0:
        return float("nan")
    return _N.cdf((sr - benchmark) * math.sqrt(n_obs - 1) / math.sqrt(var))


def deflated_sharpe(daily_pnl: np.ndarray, n_trials: int, trial_sharpe_std: float) -> float:
    """trial_sharpe_std: standard deviation of the per-period Sharpe across all trials."""
    x = np.asarray(daily_pnl, dtype=float)
    if x.size < 3 or x.std(ddof=1) == 0:
        return float("nan")
    sr = x.mean() / x.std(ddof=1)
    z = (x - x.mean()) / x.std(ddof=0)
    skew = float((z ** 3).mean())
    kurt = float((z ** 4).mean())
    return probabilistic_sharpe(sr, x.size, skew, kurt, expected_max_sharpe(n_trials, trial_sharpe_std))
