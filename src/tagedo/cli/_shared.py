"""Shared click options and output helpers used by every CLI subcommand."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

import click

from ..client import TajiduoClient

__all__ = ["base_url_option", "make_client", "render"]


def base_url_option(f: Callable[..., Any]) -> Callable[..., Any]:
    return click.option(
        "--base-url",
        default="https://bbs-api.tajiduo.com",
        show_default=True,
        help="API base URL.",
    )(f)


def make_client(base_url: str) -> TajiduoClient:
    return TajiduoClient(base_url=base_url)


def render(value: Any) -> None:
    """Pretty-print a result as JSON."""
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    click.echo(json.dumps(value, ensure_ascii=False, indent=2))
