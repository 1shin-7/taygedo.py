"""Shared helpers for ``taygedo ht`` subcommands."""

from __future__ import annotations

import click

from taygedo.cli._shared import flush_session, load_client, storage
from taygedo.cli._storage import StoredAccount
from taygedo.client import TaygedoClient
from taygedo.models import HtRoleGameRecord

HT_GAME_ID = 1256


async def resolve_ht_role_id(
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


async def fetch_record(uid: int | None, role_id: int | None) -> HtRoleGameRecord:
    client, account = load_client(uid=uid)
    async with client:
        rid = await resolve_ht_role_id(client, account, role_id)
        env = await client.ht.get_role_game_record(role_id=rid)
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no record")
    return env.data
