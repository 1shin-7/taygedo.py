"""Rich-table renderers for CLI output, with a uniform JSON fallback.

Each command calls :func:`render(value, json_out=...)`. When ``json_out`` is
True we dump the value as pretty JSON. Otherwise we look up the value's type
and pick a tailored Rich layout; unknown types fall back to JSON.

Renderers live in per-domain modules (``_nte``, ``_ht``, ``_post``, ``_search``,
``_community``, ``_user``). Each module exposes a ``register(single, listed)``
that fills two dispatch tables. Adding a new model = a new entry in one
module's ``register`` (or a new module + one line below).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import orjson
from pydantic import BaseModel
from rich.console import Console

from taygedo.cli._render import _community, _ht, _nte, _post, _search, _user

__all__ = ["render"]

# Built once at import time.
_SINGLE_RENDERERS: dict[type, Callable[..., None]] = {}
_LIST_RENDERERS: dict[type, Callable[..., None]] = {}
for _mod in (_nte, _ht, _post, _search, _community, _user):
    _mod.register(_SINGLE_RENDERERS, _LIST_RENDERERS)


def render(value: Any, *, json_out: bool = False, console: Console | None = None) -> None:
    """Render ``value`` to stdout."""
    console = console or Console()
    if json_out:
        console.print_json(_to_json_str(value))
        return
    renderer = _dispatch(value)
    if renderer is not None:
        renderer(value, console)
        return
    console.print(_to_json_str(value))


def _dispatch(value: Any) -> Callable[..., None] | None:
    for cls, fn in _SINGLE_RENDERERS.items():
        if isinstance(value, cls):
            return fn
    if isinstance(value, list) and value:
        first_cls = type(value[0])
        for cls, fn in _LIST_RENDERERS.items():
            if issubclass(first_cls, cls):
                return fn
    return None


_JSON_OPTIONS = orjson.OPT_INDENT_2 | orjson.OPT_NON_STR_KEYS


def _to_json_str(value: Any) -> str:
    if isinstance(value, BaseModel):
        return value.model_dump_json(indent=2, by_alias=True)
    if isinstance(value, list) and value and isinstance(value[0], BaseModel):
        return orjson.dumps(
            [v.model_dump(mode="json", by_alias=True) for v in value],
            option=_JSON_OPTIONS,
        ).decode("utf-8")
    if hasattr(value, "to_dict"):
        return orjson.dumps(value.to_dict(), option=_JSON_OPTIONS).decode("utf-8")
    if isinstance(value, list) and value and hasattr(value[0], "to_dict"):
        return orjson.dumps(
            [v.to_dict() for v in value], option=_JSON_OPTIONS,
        ).decode("utf-8")
    try:
        return orjson.dumps(value, default=str, option=_JSON_OPTIONS).decode("utf-8")
    except TypeError:
        return str(value)
