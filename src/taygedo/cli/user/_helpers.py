"""Internal helpers shared across user/ subcommands."""

from __future__ import annotations

from taygedo.cli._shared import require_account


def resolve_target_uid(target: int | None, uid: int | None) -> tuple[int, int | None]:
    """Pick (target_uid, command_uid). If target absent, use the active uid."""
    if target is not None:
        return target, uid
    account = require_account(uid)
    return account.uid, uid
