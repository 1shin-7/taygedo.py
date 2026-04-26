"""Shared CLI option decorators used across taygedo subcommands."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import click


def uid_option(f: Callable[..., Any]) -> Callable[..., Any]:
    return click.option(
        "--uid", type=int, help="Use this account instead of the active one.",
    )(f)


def cid_option(f: Callable[..., Any]) -> Callable[..., Any]:
    return click.option(
        "-c", "--community",
        "community_id",
        type=int,
        default=2,
        show_default=True,
        help="Community ID (1 = 幻塔, 2 = 异环).",
    )(f)


def json_option(f: Callable[..., Any]) -> Callable[..., Any]:
    return click.option(
        "--json", "json_out", is_flag=True, help="Output as JSON.",
    )(f)


def role_id_option(f: Callable[..., Any]) -> Callable[..., Any]:
    return click.option(
        "--role-id",
        type=int,
        help="Override role id (default: cached or auto-resolved).",
    )(f)
