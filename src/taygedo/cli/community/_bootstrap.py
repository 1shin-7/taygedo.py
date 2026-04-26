"""Community/column listings + app-startup debug + cross-community columns."""

from __future__ import annotations

import click

from taygedo.cli._options import json_option, uid_option
from taygedo.cli._render import render
from taygedo.cli._shared import async_command, flush_session, load_client


@click.command(name="list")
@uid_option
@json_option
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


@click.command()
@click.argument("community_id", type=int)
@uid_option
@json_option
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


@click.command()
@click.argument("column_id", type=int)
@uid_option
@json_option
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


@click.command(name="all-columns")
@uid_option
@json_option
@async_command
async def all_columns(uid: int | None, json_out: bool) -> None:
    """Cross-community column listing (every game's column tree)."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.community.list_all_columns()
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no data")
    render(env.data, json_out=json_out)


@click.command()
@uid_option
@json_option
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
