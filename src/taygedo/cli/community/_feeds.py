"""Post / topic discovery feeds (recommend / official / topics)."""

from __future__ import annotations

import click

from taygedo.cli._options import cid_option, json_option, uid_option
from taygedo.cli._render import render
from taygedo.cli._shared import async_command, flush_session, load_client


@click.command()
@cid_option
@click.option("--page", type=int, default=1, show_default=True)
@click.option("--count", type=int, default=20, show_default=True)
@uid_option
@json_option
@async_command
async def recommend(
    community_id: int, page: int, count: int, uid: int | None, json_out: bool,
) -> None:
    """Recommended post feed."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.community.recommend_posts(
            community_id=community_id, page=page, count=count,
        )
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no data")
    render(env.data, json_out=json_out)


@click.command()
@cid_option
@click.option("--column-id", type=int, default=4, show_default=True)
@click.option("--page", type=int, default=1, show_default=True)
@click.option("--count", type=int, default=20, show_default=True)
@uid_option
@json_option
@async_command
async def official(
    community_id: int,
    column_id: int,
    page: int,
    count: int,
    uid: int | None,
    json_out: bool,
) -> None:
    """Official post feed (official_type=1)."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.community.official_posts(
            community_id=community_id,
            column_id=column_id,
            page=page,
            count=count,
        )
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no data")
    render(env.data, json_out=json_out)


@click.command()
@cid_option
@uid_option
@json_option
@async_command
async def topics(community_id: int, uid: int | None, json_out: bool) -> None:
    """Server-curated recommended topics for a community."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.community.recommend_topics(community_id=community_id)
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no data")
    render(env.data, json_out=json_out)
