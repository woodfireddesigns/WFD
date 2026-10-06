# NautilusTrader version to pin

Checked on 2026-10-06 against PyPI and the release notes. Wheel source for
1.221.0 and 1.231.0 was read directly.

## Recommendation

Pin `nautilus_trader==1.231.0` on Python 3.12.

- 1.231.0 (2026-08-02) is the latest stable release and likely the last v1.
- 2.0 is at rc6 (2026-10-05). It replaces Cython with Rust via PyO3 and the
  Python API is still changing between candidates. Stay off it until 2.0 final.
- v1 gets critical fixes only, for about 3 months after the switch. Plan a 2.x
  migration, probably early 2027.

## Python version

Every release since 1.222.0 (2026-01-02) requires Python >=3.12,<3.15.
The last release that runs on 3.11 is 1.221.0 (2025-10-26), a year old.

`pyproject.toml` says `>=3.11`. Moving to 3.12 is Michael's call. The current
core runs on either.

## Databento adapter

- `DatabentoDataLoader.from_dbn_file()` maps ohlcv-1m to `Bar` in both versions.
- `bars_timestamp_on_close=True` by default. Databento stamps bars at the open.
  Our convention is bar START, so the loader must convert explicitly.
  Do not set it to False to "fix" this: the strategy would see a full bar at
  its open time, which leaks future prices.
- UNCONFIRMED: how bars from a continuous request (`ES.v.0`) are keyed. They
  may load under the real contract ID and change ID at every roll.

## Conflict with our fill convention

Our rule: decide on the close of bar k-1, fill at the open of bar k.

NautilusTrader with bar data does not do this by default:

- `bar_execution=True` splits each bar into Open, High, Low, Close price points.
- The venue processes bar k-1 through its close before `on_bar` sees it.
- A market order sent in `on_bar` fills at bar k-1's CLOSE, not bar k's open.

Options: a custom `FillModel`, a latency model, or holding the order until
the next bar arrives. UNCONFIRMED which works cleanly.

Required before trusting the engine: a unit backtest proving a market order
fills at the next bar's open, matching `sim/reference.py`.

Sources:
- https://pypi.org/pypi/nautilus_trader/json
- https://github.com/nautechsystems/nautilus_trader/releases/tag/v2.0.0rc6
- https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/integrations/databento.md
