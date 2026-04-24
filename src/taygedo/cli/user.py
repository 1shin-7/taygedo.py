"""``taygedo user`` — profile, feeds, follow."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import click
from rich.console import Console

from ._render import render
from ._shared import async_command, flush_session, load_client, require_account

__all__ = ["user_group"]


def _uid_option(f: Callable[..., Any]) -> Callable[..., Any]:
    return click.option(
        "--uid", type=int, help="Use this account instead of the active one.",
    )(f)


def _json_option(f: Callable[..., Any]) -> Callable[..., Any]:
    return click.option("--json", "json_out", is_flag=True, help="Output as JSON.")(f)


@click.group(name="user")
def user_group() -> None:
    """User profile, feeds, follow."""


@user_group.command()
@_uid_option
@_json_option
@async_command
async def me(uid: int | None, json_out: bool) -> None:
    """Show the active user's full profile (alias of `auth info`)."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.user.get_user_full_info()
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no data")
    render(env.data, json_out=json_out)


def _resolve_target_uid(target: int | None, uid: int | None) -> tuple[int, int | None]:
    """Pick (target_uid, command_uid). If target absent, use the active uid."""
    if target is not None:
        return target, uid
    account = require_account(uid)
    return account.uid, uid


@user_group.command()
@click.argument("target", type=int, required=False)
@_uid_option
@click.option("--count", type=int, default=10, show_default=True)
@_json_option
@async_command
async def posts(
    target: int | None,
    uid: int | None,
    count: int,
    json_out: bool,
) -> None:
    """Posts written by a user (default: yourself)."""
    target_uid, cmd_uid = _resolve_target_uid(target, uid)
    client, account = load_client(uid=cmd_uid)
    async with client:
        env = await client.user.get_post_list(uid=target_uid, count=count)
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no data")
    render(env.data, json_out=json_out)


@user_group.command()
@_uid_option
@click.option("--count", type=int, default=20, show_default=True)
@_json_option
@async_command
async def browse(uid: int | None, count: int, json_out: bool) -> None:
    """Your own browse history."""
    account = require_account(uid)
    client, account = load_client(uid=uid)
    async with client:
        env = await client.user.get_browse_records(uid=account.uid, count=count)
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no data")
    render(env.data, json_out=json_out)


@user_group.command()
@click.argument("target", type=int, required=False)
@_uid_option
@click.option("--count", type=int, default=20, show_default=True)
@_json_option
@async_command
async def collects(
    target: int | None,
    uid: int | None,
    count: int,
    json_out: bool,
) -> None:
    """Posts collected by a user (default: yourself)."""
    target_uid, cmd_uid = _resolve_target_uid(target, uid)
    client, account = load_client(uid=cmd_uid)
    async with client:
        env = await client.user.get_collect_posts(uid=target_uid, count=count)
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no data")
    render(env.data, json_out=json_out)


@user_group.command()
@click.argument("target", type=int, required=False)
@_uid_option
@click.option("--count", type=int, default=20, show_default=True)
@_json_option
@async_command
async def replies(
    target: int | None,
    uid: int | None,
    count: int,
    json_out: bool,
) -> None:
    """Reply feeds for a user (default: yourself)."""
    target_uid, cmd_uid = _resolve_target_uid(target, uid)
    client, account = load_client(uid=cmd_uid)
    async with client:
        env = await client.user.get_reply_feeds(uid=target_uid, count=count)
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no data")
    render(env.data, json_out=json_out)


@user_group.command()
@click.argument("target_uid", type=int)
@_uid_option
@_json_option
@async_command
async def follow(target_uid: int, uid: int | None, json_out: bool) -> None:
    """Follow another user."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.user.follow(uid=target_uid)
        flush_session(client, account)
    if json_out:
        render({"ok": env.is_ok, "followed": target_uid}, json_out=True)
        return
    Console().print(
        f"✓ followed uid={target_uid}" if env.is_ok else f"✗ failed: {env.msg}",
    )


@user_group.command()
@click.option(
    "-c", "--community",
    "community_id",
    type=int,
    default=2,
    show_default=True,
    help="Community ID (1 = 幻塔, 2 = 异环).",
)
@_uid_option
@_json_option
@async_command
async def exp(community_id: int, uid: int | None, json_out: bool) -> None:
    """Recent exp records in this community."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.user.get_exp_records(community_id=community_id)
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no data")
    render(env.data, json_out=json_out)
