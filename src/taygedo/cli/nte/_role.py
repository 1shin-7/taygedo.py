"""Role overview + character listing."""

from __future__ import annotations

import click

from taygedo.cli._options import json_option, role_id_option, uid_option
from taygedo.cli._render import render
from taygedo.cli._shared import async_command, flush_session, load_client
from taygedo.cli.nte._helpers import resolve_role_id


@click.command()
@uid_option
@json_option
@async_command
async def info(uid: int | None, json_out: bool) -> None:
    """Role-home overview."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.nte.get_role_home()
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "empty roleHome response")
    render(env.data, json_out=json_out)


@click.command()
@uid_option
@role_id_option
@click.option("--id", "char_id", help="Filter to one character id.")
@json_option
@async_command
async def character(
    uid: int | None,
    role_id: int | None,
    char_id: str | None,
    json_out: bool,
) -> None:
    """Full character list (optionally filtered by --id)."""
    client, account = load_client(uid=uid)
    async with client:
        rid = await resolve_role_id(client, role_id)
        env = await client.nte.get_characters(role_id=rid)
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no characters")
    chars = env.data
    if char_id:
        chars = [c for c in chars if c.id == char_id]
        if not chars:
            raise click.ClickException(f"no character with id={char_id}")
    render(chars, json_out=json_out)
