"""Profile read/write — me / nickname / avatar / avatars."""

from __future__ import annotations

import click
from rich.console import Console

from taygedo.cli._options import json_option, uid_option
from taygedo.cli._render import render
from taygedo.cli._shared import async_command, flush_session, load_client
from taygedo.services import UpdateUserInfoRequest


@click.command()
@uid_option
@json_option
@async_command
async def me(uid: int | None, json_out: bool) -> None:
    """Show the active user's full profile (alias of `auth info`)."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.user.get_user_full_info()
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no data")
    render(env.data, json_out=json_out)


@click.command()
@click.argument("nickname")
@uid_option
@json_option
@async_command
async def nickname(nickname: str, uid: int | None, json_out: bool) -> None:
    """Update the active account's nickname."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.user.update_info(
            body=UpdateUserInfoRequest(nickname=nickname),
        )
        flush_session(client, account)
    if json_out:
        render({"ok": env.is_ok, "msg": env.msg, "nickname": nickname}, json_out=True)
        return
    if env.is_ok:
        Console().print(f"✓ nickname updated to [bold]{nickname}[/bold]")
    else:
        raise click.ClickException(env.msg or "update failed")


@click.command()
@click.argument("avatar_url")
@uid_option
@json_option
@async_command
async def avatar(avatar_url: str, uid: int | None, json_out: bool) -> None:
    """Update the active account's avatar (pass a URL from `user avatars`)."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.user.update_info(
            body=UpdateUserInfoRequest(avatar=avatar_url),
        )
        flush_session(client, account)
    if json_out:
        render({"ok": env.is_ok, "msg": env.msg, "avatar": avatar_url}, json_out=True)
        return
    if env.is_ok:
        Console().print("✓ avatar updated")
    else:
        raise click.ClickException(env.msg or "update failed")


@click.command()
@uid_option
@json_option
@async_command
async def avatars(uid: int | None, json_out: bool) -> None:
    """List the system avatar pool (id / name / icon URL)."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.user.list_sys_avatars()
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no data")
    render(env.data, json_out=json_out)
