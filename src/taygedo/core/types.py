"""Public type aliases and TypeVars used across the framework."""

from __future__ import annotations

from typing import Any, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

JsonObject = dict[str, Any]
