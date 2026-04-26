"""``taygedo search`` — posts / topics / users / hot keywords."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import click

from taygedo.cli._render import render
from taygedo.cli._shared import async_command, flush_session, load_client

__all__ = ["search_group"]


def _uid_option(f: Callable[..., Any]) -> Callable[..., Any]:
    return click.option(
        "--uid", type=int, help="Use this account instead of the active one.",
    )(f)


def _cid_option(f: Callable[..., Any]) -> Callable[..., Any]:
    return click.option(
        "-c", "--community",
        "community_id",
        type=int,
        default=2,
        show_default=True,
        help="Community ID to scope search to (1 = 幻塔, 2 = 异环).",
    )(f)


def _json_option(f: Callable[..., Any]) -> Callable[..., Any]:
    return click.option("--json", "json_out", is_flag=True, help="Output as JSON.")(f)


@click.group(name="search")
def search_group() -> None:
    """Search posts / topics / users / hot keywords."""


@search_group.command()
@click.argument("keyword")
@_cid_option
@click.option("--page", type=int, default=1, show_default=True)
@click.option("--size", type=int, default=20, show_default=True)
@click.option(
    "--order", "order_type", type=int, default=1, show_default=True,
    help="1 = relevance, 2 = recent.",
)
@_uid_option
@_json_option
@async_command
async def posts(
    keyword: str,
    community_id: int,
    page: int,
    size: int,
    order_type: int,
    uid: int | None,
    json_out: bool,
) -> None:
    """Full-text post search."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.search.search_posts(
            keyword=keyword,
            community_id=community_id,
            page=page,
            size=size,
            order_type=order_type,
        )
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no posts")
    render(env.data, json_out=json_out)


@search_group.command()
@click.argument("keyword")
@click.option("--size", type=int, default=20, show_default=True)
@_uid_option
@_json_option
@async_command
async def topics(
    keyword: str,
    size: int,
    uid: int | None,
    json_out: bool,
) -> None:
    """Topic search (community-wide tags)."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.search.search_topics(keyword=keyword, size=size)
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no topics")
    render(env.data, json_out=json_out)


@search_group.command()
@click.argument("keyword")
@click.option("--page", type=int, default=1, show_default=True)
@click.option("--size", type=int, default=20, show_default=True)
@_uid_option
@_json_option
@async_command
async def users(
    keyword: str,
    page: int,
    size: int,
    uid: int | None,
    json_out: bool,
) -> None:
    """User search by nickname."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.search.search_users(keyword=keyword, page=page, size=size)
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no users")
    render(env.data, json_out=json_out)


@search_group.command()
@_cid_option
@_uid_option
@_json_option
@async_command
async def hot(community_id: int, uid: int | None, json_out: bool) -> None:
    """Server-curated hot search keywords."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.search.hot_words(community_id=community_id)
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no hot words")
    render(env.data, json_out=json_out)
