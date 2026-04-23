"""Public type aliases and TypeVars used across the framework."""

from __future__ import annotations

from typing import ParamSpec, TypeVar

#: Generic param spec for endpoint method signatures.
P = ParamSpec("P")

#: Return type of an endpoint coroutine (typically a pydantic model).
R = TypeVar("R")

#: Convenience alias for a JSON-like payload.
type JsonValue = (
    None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]
)
type JsonObject = dict[str, JsonValue]
