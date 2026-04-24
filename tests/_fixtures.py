"""Load sanitized JSON fixtures committed to ``tests/fixtures/``.

These fixtures are committed snapshots of API responses with all PII
stripped. Tests load them as plain JSON so the suite has no external-file
dependency beyond the repo.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

FIXTURE_DIR = Path(__file__).parent / "fixtures"


@lru_cache(maxsize=128)
def load_fixture(name: str) -> Any:
    """Load a fixture by stem (without ``.json``)."""
    path = FIXTURE_DIR / f"{name}.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)
