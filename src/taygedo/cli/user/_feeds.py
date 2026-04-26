"""User-scoped feeds — posts / browse / collects / replies / exp."""

from __future__ import annotations

import click

from taygedo.cli._options import cid_option, json_option, uid_option
from taygedo.cli._render import render
from taygedo.cli._shared import async_command, flush_session, load_client, require_account
from taygedo.cli.user._helpers import resolve_target_uid


@click.command()
@click.argument("target", type=int, required=False)
@uid_option
@click.option("--count", type=int, default=10, show_default=True)
@json_option
@async_command
async def posts(
    target: int | None,
    uid: int | None,
    count: int,
    json_out: bool,
) -> None:
    """Posts written by a user (default: yourself)."""
    target_uid, cmd_uid = resolve_target_uid(target, uid)
    client, account = load_client(uid=cmd_uid)
    async with client:
        env = await client.user.get_post_list(uid=target_uid, count=count)
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no data")
    render(env.data, json_out=json_out)


@click.command()
@uid_option
@click.option("--count", type=int, default=20, show_default=True)
@json_option
@async_command
async def browse(uid: int | None, count: int, json_out: bool) -> None:
    """Your own browse history."""
    require_account(uid)
    client, account = load_client(uid=uid)
    async with client:
        env = await client.user.get_browse_records(uid=account.uid, count=count)
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no data")
    render(env.data, json_out=json_out)


@click.command()
@click.argument("target", type=int, required=False)
@uid_option
@click.option("--count", type=int, default=20, show_default=True)
@json_option
@async_command
async def collects(
    target: int | None,
    uid: int | None,
    count: int,
    json_out: bool,
) -> None:
    """Posts collected by a user (default: yourself)."""
    target_uid, cmd_uid = resolve_target_uid(target, uid)
    client, account = load_client(uid=cmd_uid)
    async with client:
        env = await client.user.get_collect_posts(uid=target_uid, count=count)
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no data")
    render(env.data, json_out=json_out)


@click.command()
@click.argument("target", type=int, required=False)
@uid_option
@click.option("--count", type=int, default=20, show_default=True)
@json_option
@async_command
async def replies(
    target: int | None,
    uid: int | None,
    count: int,
    json_out: bool,
) -> None:
    """Reply feeds for a user (default: yourself)."""
    target_uid, cmd_uid = resolve_target_uid(target, uid)
    client, account = load_client(uid=cmd_uid)
    async with client:
        env = await client.user.get_reply_feeds(uid=target_uid, count=count)
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no data")
    render(env.data, json_out=json_out)


@click.command()
@cid_option
@uid_option
@json_option
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
