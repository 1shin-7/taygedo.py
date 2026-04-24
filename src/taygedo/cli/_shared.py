"""Shared CLI plumbing: storage singleton, client factory, async-command bridge.

Every CLI subcommand goes through ``load_client`` to obtain an authenticated
:class:`TaygedoClient` seeded from on-disk session state. The auth provider
reads the live ``client.session_state``, so a 401 → refresh inside the
endpoint engine transparently rewrites the in-memory tokens; the CLI then
flushes the rotated tokens back to disk via :func:`flush_session` when the
command completes.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from datetime import datetime, timezone
from functools import lru_cache, wraps
from typing import Any

import click

from ..client import TaygedoClient
from ..device import AndroidDeviceProfile
from ._storage import Storage, StoredAccount

__all__ = [
    "async_command",
    "flush_session",
    "load_client",
    "now_iso",
    "require_account",
    "storage",
]


@lru_cache(maxsize=1)
def storage() -> Storage:
    return Storage()


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def require_account(uid: int | None) -> StoredAccount:
    """Resolve a uid (or fall back to the active one) to a stored account."""
    s = storage()
    if uid is None:
        uid = s.active_uid()
        if uid is None:
            raise click.UsageError(
                "no account is logged in — run `taygedo auth login` first",
            )
    account = s.get_account(uid)
    if account is None:
        raise click.UsageError(f"no stored account with uid={uid}")
    return account


def load_client(*, uid: int | None = None) -> tuple[TaygedoClient, StoredAccount]:
    """Build a TaygedoClient seeded with the stored session and device.

    Returns ``(client, account)``. The caller is responsible for using the
    client as an async-context-manager; on exit, call :func:`flush_session`
    to persist any rotated tokens back to disk.
    """
    account = require_account(uid)
    device = AndroidDeviceProfile.for_htassistant(device_id=account.device_id or None)
    client = TaygedoClient(device=device)
    client.session_state.access_token = account.access_token
    client.session_state.refresh_token = account.refresh_token
    client.session_state.uid = account.uid
    client.session_state.laohu_token = account.laohu_token
    client.session_state.laohu_user_id = account.laohu_user_id
    return client, account


def flush_session(client: TaygedoClient, account: StoredAccount) -> None:
    """Write back any rotated tokens + bump last_used_at."""
    account.access_token = client.session_state.access_token
    account.refresh_token = client.session_state.refresh_token
    account.last_used_at = now_iso()
    storage().upsert_account(account, set_active=False)


def async_command(f: Callable[..., Any]) -> Callable[..., Any]:
    """Wrap an async click command function with ``asyncio.run``."""

    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return asyncio.run(f(*args, **kwargs))

    return wrapper
