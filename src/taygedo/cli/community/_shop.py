"""Point-shop / merchandise listing."""

from __future__ import annotations

import click

from taygedo.cli._options import json_option, uid_option
from taygedo.cli._render import render
from taygedo.cli._shared import async_command, flush_session, load_client


@click.command()
@click.option("--tab", default="all", show_default=True, help="all | yh | ht")
@click.option("--count", type=int, default=20, show_default=True)
@uid_option
@json_option
@async_command
async def shop(tab: str, count: int, uid: int | None, json_out: bool) -> None:
    """Browse point-shop inventory."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.community.list_goods(tab=tab, count=count)
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no data")
    render(env.data, json_out=json_out)
