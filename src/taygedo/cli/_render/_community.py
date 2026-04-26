"""Community / shop / tasks / exp / signin renderers."""

from __future__ import annotations

from collections.abc import Callable

from rich.console import Console
from rich.table import Table

from taygedo.cli._render._helpers import kv_table, truncate
from taygedo.models import (
    Community,
    CommunityHome,
    ExpLevel,
    ExpRecord,
    GameRecordCard,
    Good,
    GoodsPage,
    SignInResult,
    Task,
)


def _render_community_single(c: Community, console: Console) -> None:
    console.print(
        kv_table(
            f"Community #{c.id}",
            [
                ("name", c.name),
                ("gameId", c.game_id),
                ("state", c.state),
                ("columns", ", ".join(col.column_name for col in c.columns)),
            ],
        ),
    )


def _render_community_list(items: list[Community], console: Console) -> None:
    t = Table(title="Communities")
    t.add_column("id", style="cyan")
    t.add_column("name")
    t.add_column("gameId")
    t.add_column("columns")
    for c in items:
        t.add_row(
            str(c.id),
            c.name,
            str(c.game_id),
            ", ".join(col.column_name for col in c.columns),
        )
    console.print(t)


def _render_community_home(home: CommunityHome, console: Console) -> None:
    _render_community_single(home.community, console)
    if home.banners:
        t = Table(title="Banners")
        t.add_column("title")
        t.add_column("url")
        for b in home.banners:
            t.add_row(truncate(getattr(b, "title", ""), 40), getattr(b, "url", ""))
        console.print(t)
    if home.navigator:
        t = Table(title="Navigator")
        t.add_column("name")
        for n in home.navigator:
            t.add_row(n.name)
        console.print(t)


def _render_game_record_cards(cards: list[GameRecordCard], console: Console) -> None:
    t = Table(title="Game record cards")
    t.add_column("gameId", style="cyan")
    t.add_column("name")
    t.add_column("role")
    t.add_column("roleId")
    t.add_column("lev")
    for c in cards:
        t.add_row(
            str(c.game_id),
            c.game_name,
            c.bind_role_info.role_name,
            str(c.bind_role_info.role_id),
            str(c.bind_role_info.lev),
        )
    console.print(t)


def _render_tasks(tasks: list[Task], console: Console) -> None:
    t = Table(title="Daily tasks")
    t.add_column("key", style="cyan")
    t.add_column("title")
    t.add_column("exp")
    t.add_column("coin")
    t.add_column("progress")
    for task in tasks:
        t.add_row(
            task.task_key,
            task.title,
            str(task.exp),
            str(task.coin),
            f"{task.complete_times}/{task.limit_times}",
        )
    console.print(t)


def _render_exp_level(el: ExpLevel, console: Console) -> None:
    console.print(
        kv_table(
            "Exp / Level",
            [
                ("level", el.level),
                ("exp", el.exp),
                ("today +exp", el.today_exp),
                ("next level", el.next_level),
                ("next level exp", el.next_level_exp),
            ],
        ),
    )


def _render_exp_records(records: list[ExpRecord], console: Console) -> None:
    if not records:
        console.print("(no exp records)")
        return
    t = Table(title="Exp records")
    t.add_column("id", style="cyan")
    t.add_column("type")
    t.add_column("community")
    t.add_column("uid")
    for r in records:
        t.add_row(str(r.id), str(r.type), str(r.community_id), str(r.uid))
    console.print(t)


def _render_signin_result(r: SignInResult, console: Console) -> None:
    console.print(
        kv_table("Signin", [("exp", r.exp), ("goldCoin", r.gold_coin)]),
    )


def _render_goods(goods: list[Good], console: Console) -> None:
    t = Table(title="Shop goods")
    t.add_column("id", style="cyan")
    t.add_column("name")
    t.add_column("tab")
    t.add_column("price")
    t.add_column("stock")
    for g in goods:
        t.add_row(
            str(g.id),
            truncate(g.name, 40),
            g.tab,
            str(g.price),
            str(g.stock) if g.stock else "—",
        )
    console.print(t)


def _render_goods_page(page: GoodsPage, console: Console) -> None:
    _render_goods(page.goods, console)


def register(
    single: dict[type, Callable[..., None]],
    listed: dict[type, Callable[..., None]],
) -> None:
    single[Community] = _render_community_single
    single[CommunityHome] = _render_community_home
    single[ExpLevel] = _render_exp_level
    single[GoodsPage] = _render_goods_page
    single[SignInResult] = _render_signin_result
    listed[Community] = _render_community_list
    listed[GameRecordCard] = _render_game_record_cards
    listed[Task] = _render_tasks
    listed[ExpRecord] = _render_exp_records
    listed[Good] = _render_goods
