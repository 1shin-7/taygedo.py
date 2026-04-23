"""``taygedo ht`` (alias ``taygedo tof``) — 幻塔 game record + sub-views.

The TOF backend exposes one big endpoint (``ht/getRoleGameRecord``) that
returns role + weapons + imitations + mounts + fashion in a single payload.
Sub-commands here just slice the same response into focused tables. The
``role_id`` is resolved once via ``getGameBindRole`` and cached in the
account's ``ht_role_id`` so subsequent commands skip the lookup.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import click

from ..client import TaygedoClient
from ..models import HtRoleGameRecord
from ._render import render
from ._shared import async_command, flush_session, load_client, storage
from ._storage import StoredAccount

__all__ = ["ht_group"]

HT_GAME_ID = 1256


def _uid_option(f: Callable[..., Any]) -> Callable[..., Any]:
    return click.option(
        "--uid", type=int, help="Use this account instead of the active one.",
    )(f)


def _role_id_option(f: Callable[..., Any]) -> Callable[..., Any]:
    return click.option(
        "--role-id",
        type=int,
        help="Override role id (default: cached from getGameBindRole).",
    )(f)


def _json_option(f: Callable[..., Any]) -> Callable[..., Any]:
    return click.option("--json", "json_out", is_flag=True, help="Output as JSON.")(f)


@click.group(name="ht")
def ht_group() -> None:
    """Tower of Fantasy (gameId=1256) data."""


async def _resolve_ht_role_id(
    client: TaygedoClient, account: StoredAccount, role_id: int | None,
) -> int:
    """--role-id wins; else cached account.ht_role_id; else look up + cache."""
    if role_id is not None:
        return role_id
    if account.ht_role_id:
        return account.ht_role_id
    env = await client.bind_role.get_game_bind_role(uid=account.uid, game_id=HT_GAME_ID)
    if env.data is None or env.data.role_id <= 0:
        raise click.ClickException("找不到幻塔绑定角色 — 请先在 App 中绑定")
    account.ht_role_id = env.data.role_id
    storage().upsert_account(account, set_active=False)
    return env.data.role_id


async def _fetch_record(uid: int | None, role_id: int | None) -> HtRoleGameRecord:
    client, account = load_client(uid=uid)
    async with client:
        rid = await _resolve_ht_role_id(client, account, role_id)
        env = await client.ht.get_role_game_record(role_id=rid)
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no record")
    return env.data


@ht_group.command()
@_uid_option
@_role_id_option
@_json_option
@async_command
async def info(uid: int | None, role_id: int | None, json_out: bool) -> None:
    """Headline numbers (level / power / achievements)."""
    rec = await _fetch_record(uid, role_id)
    if json_out:
        render(
            {
                "roleid": rec.roleid,
                "rolename": rec.rolename,
                "lev": rec.lev,
                "shengelev": rec.shengelev,
                "maxgs": rec.maxgs,
                "achievementpointall": rec.achievementpointall,
                "imitationCount": rec.imitation_count,
                "artifactcount": rec.artifactcount,
                "bigsecretround": rec.bigsecretround,
                "endlessidolumtotalscore": rec.endlessidolumtotalscore,
            },
            json_out=True,
        )
        return
    # Reuse the full-record renderer's KV header section by slicing.
    rec_slim = rec.model_copy(
        update={"weaponinfo": [], "imitationlist": [], "mountlist": [], "dressfashionlist": []},
    )
    render(rec_slim, json_out=False)


@ht_group.command()
@_uid_option
@_role_id_option
@_json_option
@async_command
async def record(uid: int | None, role_id: int | None, json_out: bool) -> None:
    """Full role record."""
    rec = await _fetch_record(uid, role_id)
    render(rec, json_out=json_out)


@ht_group.command()
@_uid_option
@_role_id_option
@_json_option
@async_command
async def weapon(uid: int | None, role_id: int | None, json_out: bool) -> None:
    """Equipped weapons + matrix levels."""
    rec = await _fetch_record(uid, role_id)
    render(rec.weaponinfo, json_out=json_out)


@ht_group.command()
@_uid_option
@_role_id_option
@_json_option
@async_command
async def imitation(uid: int | None, role_id: int | None, json_out: bool) -> None:
    """Imitations (拟态)."""
    rec = await _fetch_record(uid, role_id)
    render(rec.imitationlist, json_out=json_out)


@ht_group.command()
@_uid_option
@_role_id_option
@_json_option
@async_command
async def mount(uid: int | None, role_id: int | None, json_out: bool) -> None:
    """Mounts (坐骑)."""
    rec = await _fetch_record(uid, role_id)
    render(rec.mountlist, json_out=json_out)


@ht_group.command()
@_uid_option
@_role_id_option
@_json_option
@async_command
async def fashion(uid: int | None, role_id: int | None, json_out: bool) -> None:
    """Dress fashion (时装)."""
    rec = await _fetch_record(uid, role_id)
    render(rec.dressfashionlist, json_out=json_out)
