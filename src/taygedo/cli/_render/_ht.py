"""幻塔 (HT) renderers — full role record, weapons, named-id lists, BindRole."""

from __future__ import annotations

from collections.abc import Callable

from rich.console import Console
from rich.table import Table

from taygedo.cli._render._helpers import kv_table
from taygedo.models import BindRole, HtNamedId, HtRoleGameRecord, HtWeaponInfo


def _named_id_table(title: str, items: list[HtNamedId]) -> Table:
    t = Table(title=title, show_lines=False)
    t.add_column("id")
    t.add_column("name")
    for it in items:
        t.add_row(it.id, it.name)
    return t


def _render_weapons(weapons: list[HtWeaponInfo], console: Console) -> None:
    t = Table(title=f"幻塔 · 武器 ({len(weapons)})", show_lines=False)
    t.add_column("id", justify="right")
    t.add_column("idStr")
    t.add_column("name")
    t.add_column("星", justify="right")
    t.add_column("品", justify="right")
    t.add_column("Lv", justify="right")
    t.add_column("矩阵 lv")
    for w in weapons:
        matrix = "/".join(str(m.lev) for m in w.matrix_info_list) or "—"
        t.add_row(
            str(w.id), w.id_str, w.name,
            str(w.star), str(w.color), str(w.lev), matrix,
        )
    console.print(t)


def _render_record(rec: HtRoleGameRecord, console: Console) -> None:
    info = kv_table(
        f"幻塔 · {rec.rolename}",
        [
            ("roleid", rec.roleid),
            ("group", rec.groupname),
            ("等级", rec.lev),
            ("升阶", rec.shengelev),
            ("最高战力", rec.maxgs),
            ("成就点", rec.achievementpointall),
            ("无尽幻镜", rec.endlessidolumtotalscore),
            ("拟态获得数", rec.imitation_count),
            ("神器", rec.artifactcount),
            ("装备槽等级", rec.equipslottypelevel),
            ("大秘境层数", rec.bigsecretround),
            ("创建时间", rec.createrole_time),
        ],
    )
    console.print(info)
    if rec.weaponinfo:
        _render_weapons(rec.weaponinfo, console)
    if rec.imitationlist:
        console.print(_named_id_table("拟态", rec.imitationlist))
    if rec.mountlist:
        console.print(_named_id_table("坐骑", rec.mountlist))
    if rec.dressfashionlist:
        console.print(_named_id_table("时装", rec.dressfashionlist))


def _render_named_id_list(items: list[HtNamedId], console: Console) -> None:
    console.print(_named_id_table(f"{len(items)} 项", items))


def _render_bind_role(b: BindRole, console: Console) -> None:
    console.print(
        kv_table(
            f"BindRole · gameId={b.game_id}",
            [
                ("roleId", b.role_id),
                ("roleName", b.role_name),
                ("server", b.server_name or b.server_id),
                ("account", b.account),
                ("等级", b.lev),
            ],
        ),
    )


def register(
    single: dict[type, Callable[..., None]],
    listed: dict[type, Callable[..., None]],
) -> None:
    single[HtRoleGameRecord] = _render_record
    single[BindRole] = _render_bind_role
    listed[HtWeaponInfo] = _render_weapons
    listed[HtNamedId] = _render_named_id_list
