"""Config loading and hashing. Protected files are hashed into every trial."""
from __future__ import annotations

import hashlib
from pathlib import Path

import yaml

PROTECTED = ("gates.yaml", "costs.yaml")


def load_yaml(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def file_hash(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]


def protected_hashes(config_dir: str | Path) -> dict[str, str]:
    config_dir = Path(config_dir)
    return {name: file_hash(config_dir / name) for name in PROTECTED}
