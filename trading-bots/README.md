# trading-bots

Starter repo for the automated trading system. The engine-independent core is
built and tested. Nothing here has run on real market data yet.

## Quick start

    pip install -e ".[dev]"
    python -m pytest                    # 40 tests
    python scripts/demo_synthetic.py    # pipeline demo on fake data

## First session in Claude Code

Paste this:

> Read CLAUDE.md and docs/brief.md. Run the tests. Then do Phase 0 only: work
> through the Phase 0 checklist in CLAUDE.md, write your findings to
> docs/findings/, and stop. Do not download paid data or start Phase 1 until I
> have read the findings.

## Before that session

1. Create a private GitHub repo and push this folder.
2. Export the build brief from Claude as Markdown and save it as `docs/brief.md`.
3. Open a Databento account. Put the key in `.env` (copy `.env.example`).
4. Set your own budget caps in the brief.

Nothing in this repo is financial advice.
