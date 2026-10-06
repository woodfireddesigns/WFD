"""End-to-end demo on SYNTHETIC data. Proves the pipeline runs. Proves nothing about markets.

Run from the repo root:  python scripts/demo_synthetic.py
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tradingbots.config import load_yaml  # noqa: E402
from tradingbots.data.sessions import to_day_arrays  # noqa: E402
from tradingbots.data.synthetic import make_bars  # noqa: E402
from tradingbots.metrics.core import summarize  # noqa: E402
from tradingbots.metrics.deflated import deflated_sharpe  # noqa: E402
from tradingbots.propsim.evaluation import monte_carlo  # noqa: E402
from tradingbots.propsim.profile import Profile  # noqa: E402
from tradingbots.sim.reference import Costs, Risk, run_backtest  # noqa: E402
from tradingbots.strategies.intraday_momentum import Params  # noqa: E402


def main() -> None:
    cfg = ROOT / "config"
    gates = load_yaml(cfg / "gates.yaml")
    costs = Costs.from_config(load_yaml(cfg / "costs.yaml"))
    risk_cfg = load_yaml(cfg / "risk.yaml")
    strat = load_yaml(cfg / "strategies" / "intraday_momentum.yaml")
    params = Params(**{k: v for k, v in strat.items() if k != "neighbors"})
    profile = Profile.load(cfg / "profiles" / "tradeify_select_50k_eval.yaml")
    mc_cfg = gates["prop"]["monte_carlo"]

    print("=" * 64)
    print("SYNTHETIC DATA. Trend days are planted on purpose. Not evidence.")
    print("=" * 64)
    days, skipped = to_day_arrays(make_bars(n_days=400, trend_day_prob=0.35, seed=11))
    print(f"days loaded: {len(days)}   skipped: {len(skipped)}")

    for size in risk_cfg["sizing_grid"]:
        risk = Risk.from_config({**risk_cfg, "risk_per_trade": size})
        res = run_backtest(days, params, costs, risk)
        s = summarize(res.trades, res.daily)
        dsr = deflated_sharpe(res.daily["pnl"].to_numpy(), n_trials=1, trial_sharpe_std=0.0)
        mc = monte_carlo(
            res.daily, profile,
            floor_buffer=risk_cfg["floor_buffer"], risk_per_trade=size,
            paths=mc_cfg["paths"], block_days=mc_cfg["block_days"], max_days=mc_cfg["max_days"],
        )
        print(f"\nrisk per trade ${size}")
        print(f"  trades {s['trades']}   skipped {res.skipped_share:.0%} of signals")
        print(f"  net ${s['net_profit']:,.0f}   profit factor {s['profit_factor']:.2f}   Sharpe {s['sharpe']:.2f}"
              f"   deflated Sharpe {dsr:.2f}")
        print(f"  worst drawdown, intraday ${s['max_drawdown_intraday']:,.0f}")
        print(f"  evaluation: pass {mc.pass_probability:.0%}   breach {mc.breach_probability:.0%}"
              f"   stalled {mc.stall_probability:.0%}   timeout {mc.timeout_probability:.0%}"
              f"   median days to pass {mc.median_days_to_pass:.0f}")


if __name__ == "__main__":
    main()
