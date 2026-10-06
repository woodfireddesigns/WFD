"""Append-only trial log. Every run is recorded, including failures.

The database refuses UPDATE and DELETE. A run with uncommitted code changes
is stored as unofficial and cannot count toward a promotion decision.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path

_SCHEMA = """
CREATE TABLE IF NOT EXISTS trials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    logged_at TEXT NOT NULL,
    strategy TEXT NOT NULL,
    config_json TEXT NOT NULL,
    config_hash TEXT NOT NULL,
    gates_hash TEXT NOT NULL,
    costs_hash TEXT NOT NULL,
    git_commit TEXT NOT NULL,
    official INTEGER NOT NULL,
    data_start TEXT NOT NULL,
    data_end TEXT NOT NULL,
    metrics_json TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS trials_no_update BEFORE UPDATE ON trials
BEGIN SELECT RAISE(ABORT, 'trial log is append-only'); END;
CREATE TRIGGER IF NOT EXISTS trials_no_delete BEFORE DELETE ON trials
BEGIN SELECT RAISE(ABORT, 'trial log is append-only'); END;
"""


def git_state(repo: str | Path = ".") -> tuple[str, bool]:
    """Return (commit, clean). Unknown and not clean when git is unavailable."""
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=True
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain"], cwd=repo, capture_output=True, text=True, check=True
        ).stdout.strip()
        return commit, dirty == ""
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown", False


def log_trial(
    db_path: str | Path,
    *,
    strategy: str,
    config: dict,
    protected_hashes: dict[str, str],
    data_start: str,
    data_end: str,
    metrics: dict,
    repo: str | Path = ".",
) -> int:
    commit, clean = git_state(repo)
    config_json = json.dumps(config, sort_keys=True, default=str)
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(_SCHEMA)
        cur = conn.execute(
            "INSERT INTO trials (logged_at, strategy, config_json, config_hash, gates_hash, costs_hash,"
            " git_commit, official, data_start, data_end, metrics_json) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                datetime.now(timezone.utc).isoformat(),
                strategy,
                config_json,
                hashlib.sha256(config_json.encode()).hexdigest()[:16],
                protected_hashes["gates.yaml"],
                protected_hashes["costs.yaml"],
                commit,
                int(clean),
                data_start,
                data_end,
                json.dumps(metrics, sort_keys=True, default=str),
            ),
        )
        return int(cur.lastrowid)


def count_trials(db_path: str | Path, strategy: str | None = None) -> int:
    """Distinct configurations tried. This is the N in the deflated Sharpe ratio."""
    if not Path(db_path).exists():
        return 0
    with sqlite3.connect(db_path) as conn:
        conn.executescript(_SCHEMA)
        if strategy is None:
            row = conn.execute("SELECT COUNT(DISTINCT config_hash) FROM trials").fetchone()
        else:
            row = conn.execute(
                "SELECT COUNT(DISTINCT config_hash) FROM trials WHERE strategy = ?", (strategy,)
            ).fetchone()
        return int(row[0])
