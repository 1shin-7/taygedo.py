"""``taygedo community`` — BBS community views, App signin, tasks, shop."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import click
from rich.console import Console

from ._render import render
from ._shared import async_command, flush_session, load_client

__all__ = ["community_group"]


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
        help="Community ID (1 = 幻塔, 2 = 异环).",
    )(f)


def _json_option(f: Callable[..., Any]) -> Callable[..., Any]:
    return click.option("--json", "json_out", is_flag=True, help="Output as JSON.")(f)


@click.group(name="community")
def community_group() -> None:
    """BBS community: listings, signin, tasks, shop."""


# --- listings --------------------------------------------------------------


@community_group.command(name="list")
@_uid_option
@_json_option
@async_command
async def list_all(uid: int | None, json_out: bool) -> None:
    """List all communities (game forum sections)."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.community.list_all()
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "empty")
    render(env.data, json_out=json_out)


@community_group.command()
@click.argument("community_id", type=int)
@_uid_option
@_json_option
@async_command
async def home(community_id: int, uid: int | None, json_out: bool) -> None:
    """Show community home (banners + navigator)."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.community.get_home(community_id=community_id)
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no data")
    render(env.data, json_out=json_out)


@community_group.command()
@click.argument("column_id", type=int)
@_uid_option
@_json_option
@async_command
async def column(column_id: int, uid: int | None, json_out: bool) -> None:
    """Show a column's home (top posts + announcements)."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.community.get_column_home(column_id=column_id)
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no data")
    render(env.data, json_out=json_out)


@community_group.command()
@_cid_option
@click.option("--page", type=int, default=1, show_default=True)
@click.option("--count", type=int, default=20, show_default=True)
@_uid_option
@_json_option
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


@community_group.command()
@_cid_option
@click.option("--column-id", type=int, default=4, show_default=True)
@click.option("--page", type=int, default=1, show_default=True)
@click.option("--count", type=int, default=20, show_default=True)
@_uid_option
@_json_option
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


# --- App signin ------------------------------------------------------------


@community_group.command()
@_cid_option
@_uid_option
@_json_option
@async_command
async def signin(community_id: int, uid: int | None, json_out: bool) -> None:
    """Check in to a community today (rewards: exp + goldCoin)."""
    from ..services import SigninRequest

    client, account = load_client(uid=uid)
    console = Console()
    async with client:
        state_env = await client.community.get_sign_state(community_id=community_id)
        already = bool(state_env.data)
        if already:
            flush_session(client, account)
            if json_out:
                render({"already_signed": True}, json_out=True)
                return
            console.print("✓ 今日已签到")
            return
        env = await client.community.signin(
            body=SigninRequest.model_validate({"communityId": community_id}),
        )
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "signin failed")
    if json_out:
        render(env.data, json_out=True)
        return
    console.print(
        f"✓ 社区签到成功 — exp +[bold]{env.data.exp}[/bold] "
        f"coin +[bold]{env.data.gold_coin}[/bold]",
    )


@community_group.command(name="sign-state")
@_cid_option
@_uid_option
@_json_option
@async_command
async def sign_state(community_id: int, uid: int | None, json_out: bool) -> None:
    """Check whether today's community signin has already been claimed."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.community.get_sign_state(community_id=community_id)
        flush_session(client, account)
    render({"signed_today": bool(env.data)}, json_out=bool(json_out))
    if not json_out:
        Console().print("✓ 已签到" if env.data else "✗ 未签到")


# --- tasks / exp / coin ----------------------------------------------------


@community_group.command()
@_cid_option
@click.option("--gid", type=int, default=2, show_default=True)
@_uid_option
@_json_option
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


@community_group.command()
@_cid_option
@_uid_option
@_json_option
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


@community_group.command()
@_uid_option
@_json_option
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


# --- shop -----------------------------------------------------------------


@community_group.command()
@click.option("--tab", default="all", show_default=True, help="all | yh | ht")
@click.option("--count", type=int, default=20, show_default=True)
@_uid_option
@_json_option
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


# --- debug ----------------------------------------------------------------


@community_group.command()
@_uid_option
@_json_option
@async_command
async def startup(uid: int | None, json_out: bool) -> None:
    """Raw app-startup data (debug)."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.community.get_app_startup_data()
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no data")
    render(env.data, json_out=json_out or True)
