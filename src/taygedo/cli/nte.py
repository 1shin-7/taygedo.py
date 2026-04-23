"""``taygedo nte`` (alias ``taygedo yh``) — 异环 game queries + sign-in."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import click
from rich.console import Console

from ..client import TaygedoClient
from ..core import ApiError
from ._render import render
from ._shared import async_command, flush_session, load_client

__all__ = ["nte_group"]


def _uid_option(f: Callable[..., Any]) -> Callable[..., Any]:
    return click.option(
        "--uid", type=int, help="Use this account instead of the active one.",
    )(f)


def _role_id_option(f: Callable[..., Any]) -> Callable[..., Any]:
    return click.option(
        "--role-id",
        type=int,
        help="Override role id (default: derived from /yh/roleHome).",
    )(f)


def _json_option(f: Callable[..., Any]) -> Callable[..., Any]:
    return click.option("--json", "json_out", is_flag=True, help="Output as JSON.")(f)


@click.group(name="nte")
def nte_group() -> None:
    """异环 (gameId=1289) data + monthly sign-in."""


async def _resolve_role_id(client: TaygedoClient, role_id: int | None) -> int:
    """If role_id is None, hit /yh/roleHome to discover it."""
    if role_id is not None:
        return role_id
    home = await client.nte.get_role_home()
    if home.data is None:
        raise click.ClickException("could not resolve role id from /yh/roleHome")
    return int(home.data.roleid)


@nte_group.command()
@_uid_option
@_json_option
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


@nte_group.command()
@_uid_option
@_role_id_option
@click.option("--id", "char_id", help="Filter to one character id.")
@_json_option
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
        rid = await _resolve_role_id(client, role_id)
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


@nte_group.command()
@_uid_option
@_role_id_option
@click.option("--house", help="Filter to one house id.")
@_json_option
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
        rid = await _resolve_role_id(client, role_id)
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


@nte_group.command()
@_uid_option
@_role_id_option
@_json_option
@async_command
async def vehicle(uid: int | None, role_id: int | None, json_out: bool) -> None:
    """Vehicle collection."""
    client, account = load_client(uid=uid)
    async with client:
        rid = await _resolve_role_id(client, role_id)
        env = await client.nte.get_vehicles(role_id=rid)
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no vehicles")
    render(env.data, json_out=json_out)


@nte_group.command()
@_uid_option
@_role_id_option
@click.option("--id", "area_id", help="Filter to one area id.")
@_json_option
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
        rid = await _resolve_role_id(client, role_id)
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


@nte_group.command()
@_uid_option
@_role_id_option
@click.option(
    "--preview",
    is_flag=True,
    help="Show this month's reward pool + state without signing.",
)
@click.option(
    "--raw",
    is_flag=True,
    help="Dump the underlying server JSON instead of the formatted result.",
)
@_json_option
@async_command
async def sign(
    uid: int | None,
    role_id: int | None,
    preview: bool,
    raw: bool,
    json_out: bool,
) -> None:
    """Submit today's monthly sign-in for the active role."""
    client, account = load_client(uid=uid)
    console = Console()
    async with client:
        rid = await _resolve_role_id(client, role_id)
        state_env = await client.nte_sign.get_state()
        if state_env.data is None:
            raise click.ClickException(state_env.msg or "no signin state")
        state = state_env.data

        if preview:
            rewards_env = await client.nte_sign.get_rewards(role_id=rid)
            flush_session(client, account)
            if raw:
                render(
                    {
                        "state": state.model_dump(mode="json"),
                        "rewards": (
                            [r.model_dump(mode="json") for r in rewards_env.data]
                            if rewards_env.data
                            else []
                        ),
                    },
                    json_out=json_out,
                )
                return
            render(state, json_out=json_out)
            if rewards_env.data:
                render(rewards_env.data, json_out=json_out)
            return

        if state.today_sign:
            flush_session(client, account)
            if json_out or raw:
                render({"already_signed": True, "state": state.model_dump(mode="json")},
                       json_out=True)
                return
            console.print(
                f"已签到 (累计 [bold]{state.days}[/bold] 天)",
            )
            return

        try:
            sign_env = await client.nte_sign.sign_role(role_id=rid)
        except ApiError as exc:
            raise click.ClickException(f"签到失败: {exc.body}") from exc
        new_state_env = await client.nte_sign.get_state()
        new_state = new_state_env.data or state
        rewards_env = await client.nte_sign.get_rewards(role_id=rid)
        flush_session(client, account)

        today_idx = max(new_state.day - 1, 0)
        reward = (
            rewards_env.data[today_idx]
            if rewards_env.data and today_idx < len(rewards_env.data)
            else None
        )

        if raw:
            render(
                {
                    "sign": sign_env.model_dump(mode="json"),
                    "state": new_state.model_dump(mode="json"),
                    "today_reward": reward.model_dump(mode="json") if reward else None,
                },
                json_out=json_out or True,
            )
            return
        if json_out:
            render(
                {
                    "ok": sign_env.is_ok,
                    "days": new_state.days,
                    "today_reward": reward.model_dump(mode="json") if reward else None,
                },
                json_out=True,
            )
            return
        console.print(f"✓ 今日签到成功 (累计 [bold]{new_state.days}[/bold] 天)")
        if reward:
            console.print(f"🎁 [bold]{reward.name}[/bold] x{reward.num}")
