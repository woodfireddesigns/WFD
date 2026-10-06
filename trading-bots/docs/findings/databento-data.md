# Databento data for ES and NQ

Checked on 2026-10-06. The network proxy blocked databento.com, so these come
from search snippets of Databento pages, not pages read in full. Items marked
VERIFY must be confirmed on the live docs before buying anything.

## Continuous symbol

- Format `[ROOT].[RULE].[RANK]` with `stype_in="continuous"`.
- `ES.v.0` and `NQ.v.0`: front contract ranked by the previous day's volume.
- Prices are NOT back-adjusted. Each date maps to the raw prices of the real
  contract. Expect a price jump at each roll. The strategy must not compare
  prices across a roll (prior close, 14-day lookback) without handling it.

## Dataset

- GLBX.MDP3 history starts 2010-06-06. Pre-2017 data was backfilled from CME
  DataMine.
- ohlcv-1m is aggregated from trades, so highs and lows should be true
  extremes. VERIFY that all trades are included.
- `ts_event` is the bar OPEN time, which matches our convention.
- VERIFY: minutes with no trades probably have no bar. `data/sessions.py`
  skips incomplete days, so check how many RTH days that drops on real data.
- MES and MNQ launched 2019-05-06. Their history cannot start earlier.

## Cost

- Historical data is pay-as-you-go, billed per GB. CME is advertised from
  $0.50/GB. VERIFY the ohlcv rate.
- New accounts get $125 credit, expiring 6 months after signup.
- Estimate (ours, not Databento's): about 0.3 GB each for ES and NQ, 2010 to
  2026. Likely a few dollars, under the $25 stop-and-ask line. Not confirmed.
- Get the exact quote before downloading. This call downloads nothing:

```python
import databento as db
client = db.Historical()  # reads DATABENTO_API_KEY
for sym in ["ES.v.0", "NQ.v.0"]:
    kw = dict(dataset="GLBX.MDP3", symbols=[sym], schema="ohlcv-1m",
              stype_in="continuous", start="2010-06-06", end="2026-10-01")
    cost = client.metadata.get_cost(**kw)
    size = client.metadata.get_billable_size(**kw)
    print(sym, f"${cost:.2f}", f"{size / 1e9:.3f} GB")
```

## Plans

- CME Standard plan rose to $199/month on 2026-06-22. It is only worth it
  once live data is needed. Pay-as-you-go covers Phase 1.
- VERIFY CME licence terms for personal versus professional use:
  https://api.databento.com/static/licensing/cme/cme-market-data-fee-list.pdf

Sources:
- https://docs.databento.com/knowledge-base/new-users/smart-symbology
- https://databento.com/blog/CME-history-extended-to-2010
- https://databento.com/blog/updates-to-subscription-pricing
- https://roadmap.databento.com/roadmap/provide-adjusted-continuous-contract
