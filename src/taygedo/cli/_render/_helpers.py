"""Shared helpers used by every renderer module."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from rich.table import Table


def kv_table(title: str, pairs: Iterable[tuple[str, Any]]) -> Table:
    """Two-column key-value rich Table — used for single-record renderers."""
    t = Table(title=title, show_header=False, box=None, pad_edge=False)
    t.add_column("key", style="bold cyan")
    t.add_column("value")
    for k, v in pairs:
        t.add_row(str(k), "" if v is None else str(v))
    return t


def truncate(s: str, limit: int = 80) -> str:
    s = s.replace("\n", " ")
    return s if len(s) <= limit else s[: limit - 1] + "…"
