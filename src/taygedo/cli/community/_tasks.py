"""Daily task / exp / coin progress."""

from __future__ import annotations

import click

from taygedo.cli._options import cid_option, json_option, uid_option
from taygedo.cli._render import render
from taygedo.cli._shared import async_command, flush_session, load_client


@click.command()
@cid_option
@click.option("--gid", type=int, default=2, show_default=True)
@uid_option
@json_option
@async_command
async def tasks(
    community_id: int, gid: int, uid: int | None, json_out: bool,
) -> None:
    """Daily task progress."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.community.get_user_tasks(
            community_id=community_id, gid=gid,
        )
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no data")
    render(env.data.task_list3, json_out=json_out)


@click.command()
@cid_option
@uid_option
@json_option
@async_command
async def exp(community_id: int, uid: int | None, json_out: bool) -> None:
    """Current user level + exp in this community."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.community.get_exp_level(community_id=community_id)
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no data")
    render(env.data, json_out=json_out)


@click.command()
@uid_option
@json_option
@async_command
async def coins(uid: int | None, json_out: bool) -> None:
    """Gold-coin progress today."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.community.get_coin_task_state()
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no data")
    render(env.data, json_out=json_out)
