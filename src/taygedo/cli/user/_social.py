"""Social actions — follow / unfollow / list-follows."""

from __future__ import annotations

import click
from rich.console import Console

from taygedo.cli._options import json_option, uid_option
from taygedo.cli._render import render
from taygedo.cli._shared import async_command, flush_session, load_client
from taygedo.cli.user._helpers import resolve_target_uid


@click.command()
@click.argument("target_uid", type=int)
@uid_option
@json_option
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


@click.command()
@click.argument("target_uid", type=int)
@uid_option
@json_option
@async_command
async def unfollow(target_uid: int, uid: int | None, json_out: bool) -> None:
    """Unfollow another user."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.user.unfollow(uid=target_uid)
        flush_session(client, account)
    if json_out:
        render({"ok": env.is_ok, "unfollowed": target_uid}, json_out=True)
        return
    Console().print(
        f"✓ unfollowed uid={target_uid}" if env.is_ok else f"✗ failed: {env.msg}",
    )


@click.command()
@click.argument("target", type=int, required=False)
@uid_option
@click.option("--count", type=int, default=20, show_default=True)
@click.option("--last-id", type=int, default=0, show_default=True,
              help="Cursor: lastId from previous page.")
@json_option
@async_command
async def follows(
    target: int | None,
    uid: int | None,
    count: int,
    last_id: int,
    json_out: bool,
) -> None:
    """List who a user follows (default: yourself)."""
    target_uid, cmd_uid = resolve_target_uid(target, uid)
    client, account = load_client(uid=cmd_uid)
    async with client:
        env = await client.user.query_follows(
            uid=target_uid, count=count, last_id=last_id,
        )
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no data")
    render(env.data, json_out=json_out)
