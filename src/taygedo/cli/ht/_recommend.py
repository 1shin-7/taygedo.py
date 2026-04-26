"""幻塔 game-scoped recommended-post feed."""

from __future__ import annotations

import click

from taygedo.cli._options import json_option, uid_option
from taygedo.cli._render import render
from taygedo.cli._shared import async_command, flush_session, load_client


@click.command()
@uid_option
@json_option
@async_command
async def recommend(uid: int | None, json_out: bool) -> None:
    """Game-scoped recommended posts (gameId=1256)."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.ht.recommend_posts()
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no data")
    render(env.data, json_out=json_out)
