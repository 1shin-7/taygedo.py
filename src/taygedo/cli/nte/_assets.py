"""异环 collectibles + meta — realestate / vehicle / area / cards / team."""

from __future__ import annotations

import click

from taygedo.cli._options import json_option, role_id_option, uid_option
from taygedo.cli._render import render
from taygedo.cli._shared import async_command, flush_session, load_client
from taygedo.cli.nte._helpers import resolve_role_id


@click.command()
@uid_option
@role_id_option
@click.option("--house", help="Filter to one house id.")
@json_option
@async_command
async def realestate(
    uid: int | None,
    role_id: int | None,
    house: str | None,
    json_out: bool,
) -> None:
    """Realestate / furniture collection."""
    client, account = load_client(uid=uid)
    async with client:
        rid = await resolve_role_id(client, role_id)
        env = await client.nte.get_realestate(role_id=rid)
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no realestate")
    data = env.data
    if house:
        data = data.model_copy(update={"detail": [h for h in data.detail if h.id == house]})
        if not data.detail:
            raise click.ClickException(f"no house with id={house}")
    render(data, json_out=json_out)


@click.command()
@uid_option
@role_id_option
@json_option
@async_command
async def vehicle(uid: int | None, role_id: int | None, json_out: bool) -> None:
    """Vehicle collection."""
    client, account = load_client(uid=uid)
    async with client:
        rid = await resolve_role_id(client, role_id)
        env = await client.nte.get_vehicles(role_id=rid)
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no vehicles")
    render(env.data, json_out=json_out)


@click.command()
@uid_option
@role_id_option
@click.option("--id", "area_id", help="Filter to one area id.")
@json_option
@async_command
async def area(
    uid: int | None,
    role_id: int | None,
    area_id: str | None,
    json_out: bool,
) -> None:
    """Per-area sub-task progress."""
    client, account = load_client(uid=uid)
    async with client:
        rid = await resolve_role_id(client, role_id)
        env = await client.nte.get_area_progress(role_id=rid)
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no area progress")
    areas = env.data
    if area_id:
        areas = [a for a in areas if a.id == area_id]
        if not areas:
            raise click.ClickException(f"no area with id={area_id}")
    render(areas, json_out=json_out)


@click.command()
@uid_option
@json_option
@async_command
async def team(uid: int | None, json_out: bool) -> None:
    """Server-curated team-recommendation list."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.nte.get_team_recommends()
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no data")
    render(env.data, json_out=json_out)


@click.command()
@uid_option
@json_option
@async_command
async def cards(uid: int | None, json_out: bool) -> None:
    """Game-record cards bound to your bbs uid (across all games)."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.community.get_game_record_cards(uid=account.uid)
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no data")
    render(env.data, json_out=json_out)
