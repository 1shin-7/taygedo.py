"""User / account renderers."""

from __future__ import annotations

from collections.abc import Callable

from rich.console import Console
from rich.table import Table

from taygedo.cli._render._helpers import kv_table
from taygedo.cli._storage import StoredAccount
from taygedo.models import User, UserFullInfo


def _render_user_full_info(info: UserFullInfo, console: Console) -> None:
    u = info.user
    console.print(
        kv_table(
            f"User #{u.uid}",
            [
                ("nickname", u.nickname),
                ("account", u.account),
                ("region", u.ip_region),
                ("realname", "✓" if u.is_realname else "✗"),
                ("fans", info.user_stat.fans_cnt),
                ("follows", info.user_stat.follow_cnt),
                ("posts", info.user_stat.post_num),
            ],
        ),
    )


def _render_user_list(users: list[User], console: Console) -> None:
    t = Table(title="Users")
    t.add_column("uid", style="cyan")
    t.add_column("nickname")
    t.add_column("account")
    t.add_column("region")
    for u in users:
        t.add_row(str(u.uid), u.nickname, u.account, u.ip_region)
    console.print(t)


def _render_account_list(accounts: list[StoredAccount], console: Console) -> None:
    from taygedo.cli._shared import storage  # avoid cycle at module load

    active = storage().active_uid()
    t = Table(title=f"账号 ({len(accounts)})", show_lines=False)
    t.add_column("uid")
    t.add_column("nickname")
    t.add_column("cellphone")
    t.add_column("active")
    t.add_column("last used")
    for a in accounts:
        t.add_row(
            str(a.uid),
            a.nickname or "—",
            a.cellphone_masked or "—",
            "✓" if a.uid == active else "",
            a.last_used_at or "—",
        )
    console.print(t)


def register(
    single: dict[type, Callable[..., None]],
    listed: dict[type, Callable[..., None]],
) -> None:
    single[UserFullInfo] = _render_user_full_info
    listed[User] = _render_user_list
    listed[StoredAccount] = _render_account_list
