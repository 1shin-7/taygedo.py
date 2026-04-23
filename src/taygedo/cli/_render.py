"""Rich-table renderers for CLI output, with a uniform JSON fallback.

Each command calls :func:`render(value, json_out=...)`. When ``json_out`` is
True we dump the value as pretty JSON. Otherwise we look up the value's type
in :data:`_RENDERERS` and pick a tailored Rich layout; unknown types fall
back to a generic key/value table.

Renderers are deliberately kept short — they render *what HAR actually
gives us*, not every theoretical field. Adding columns is cheap; adding the
abstraction needed to make them dynamic is not, so we don't.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable
from typing import Any

from pydantic import BaseModel
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..models import (
    BindRole,
    HtNamedId,
    HtRoleGameRecord,
    HtWeaponInfo,
    NteArea,
    NteCharacter,
    NteRealestateData,
    NteRoleHome,
    NteSignReward,
    NteSignState,
    NteVehicleData,
)
from ._storage import StoredAccount

__all__ = ["render"]


def render(value: Any, *, json_out: bool = False, console: Console | None = None) -> None:
    """Render ``value`` to stdout.

    Pydantic models / lists thereof / StoredAccount lists get bespoke tables
    when ``json_out`` is False; everything else falls back to JSON.
    """
    console = console or Console()
    if json_out:
        console.print_json(_to_json_str(value))
        return

    renderer = _dispatch(value)
    if renderer is not None:
        renderer(value, console)
        return

    # Generic fallback: dump as JSON inside a panel so it still looks fine.
    console.print(_to_json_str(value))


def _to_json_str(value: Any) -> str:
    if isinstance(value, BaseModel):
        return value.model_dump_json(indent=2, by_alias=True)
    if isinstance(value, list) and value and isinstance(value[0], BaseModel):
        return json.dumps(
            [v.model_dump(mode="json", by_alias=True) for v in value],
            ensure_ascii=False, indent=2,
        )
    if hasattr(value, "to_dict"):
        return json.dumps(value.to_dict(), ensure_ascii=False, indent=2)
    if isinstance(value, list) and value and hasattr(value[0], "to_dict"):
        return json.dumps([v.to_dict() for v in value], ensure_ascii=False, indent=2)
    try:
        return json.dumps(value, ensure_ascii=False, indent=2, default=str)
    except TypeError:
        return str(value)


def _dispatch(value: Any) -> Callable[[Any, Console], None] | None:
    if isinstance(value, NteRoleHome):
        return _render_nte_role_home
    if isinstance(value, NteRealestateData):
        return _render_nte_realestate
    if isinstance(value, NteVehicleData):
        return _render_nte_vehicles
    if isinstance(value, NteSignState):
        return _render_nte_sign_state
    if isinstance(value, HtRoleGameRecord):
        return _render_ht_record
    if isinstance(value, BindRole):
        return _render_bind_role
    if isinstance(value, list) and value:
        first = value[0]
        if isinstance(first, NteCharacter):
            return _render_nte_characters
        if isinstance(first, NteArea):
            return _render_nte_areas
        if isinstance(first, NteSignReward):
            return _render_nte_sign_rewards
        if isinstance(first, HtWeaponInfo):
            return _render_ht_weapons
        if isinstance(first, HtNamedId):
            return _render_ht_named_id_list
        if isinstance(first, StoredAccount):
            return _render_account_list
    return None


# ---------- helpers ----------------------------------------------------------


def _kv_table(title: str, pairs: Iterable[tuple[str, Any]]) -> Table:
    t = Table(title=title, show_header=False, box=None, pad_edge=False)
    t.add_column("key", style="bold cyan")
    t.add_column("value")
    for k, v in pairs:
        t.add_row(str(k), "" if v is None else str(v))
    return t


# ---------- NTE renderers ----------------------------------------------------


def _render_nte_role_home(home: NteRoleHome, console: Console) -> None:
    info = _kv_table(
        f"异环 · {home.rolename}",
        [
            ("roleId", home.roleid),
            ("server", home.servername or home.serverid),
            ("等级", home.lev),
            ("世界等级", home.worldlevel),
            ("大富翁等级", home.tycoon_level),
            ("登录天数", home.rolelogin_days),
            ("拥有角色数", home.charid_cnt),
            ("成就总数", home.achieve_progress.total),
            ("展示房产", f"{home.realestate.show_name} ({home.realestate.total} 套)"),
            ("展示载具", f"{home.vehicle.show_name} ({home.vehicle.total} 辆)"),
        ],
    )
    console.print(info)
    if home.area_progress:
        ap = Table(title="区域进度", show_lines=False)
        ap.add_column("id")
        ap.add_column("区域")
        ap.add_column("总分", justify="right")
        for a in home.area_progress:
            ap.add_row(a.id, a.name, str(a.total))
        console.print(ap)
    if home.characters:
        ch = Table(title="角色摘要", show_lines=False)
        ch.add_column("id")
        ch.add_column("name")
        ch.add_column("品质")
        ch.add_column("元素")
        ch.add_column("阵营")
        for c in home.characters:
            ch.add_row(c.id, c.name, c.quality, c.element_type, c.group_type)
        console.print(ch)


def _render_nte_characters(chars: list[NteCharacter], console: Console) -> None:
    t = Table(title=f"异环 · 角色 ({len(chars)})", show_lines=False)
    t.add_column("id")
    t.add_column("name")
    t.add_column("品质")
    t.add_column("元素")
    t.add_column("阵营")
    t.add_column("觉醒", justify="right")
    t.add_column("属性数", justify="right")
    t.add_column("技能数", justify="right")
    for c in chars:
        t.add_row(
            c.id,
            c.name,
            c.quality,
            c.element_type,
            c.group_type,
            str(c.awaken_lev),
            str(len(c.properties)),
            str(len(c.skills)),
        )
    console.print(t)


def _render_nte_realestate(data: NteRealestateData, console: Console) -> None:
    t = Table(title=f"异环 · 不动产 (拥有 {data.total})", show_lines=False)
    t.add_column("id")
    t.add_column("name")
    t.add_column("已入手")
    t.add_column("家具", justify="right")
    for h in data.detail:
        owned = sum(1 for f in h.fdetail if f.own)
        t.add_row(h.id, h.name, "✓" if h.own else "—", f"{owned}/{len(h.fdetail)}")
    console.print(t)


def _render_nte_vehicles(data: NteVehicleData, console: Console) -> None:
    t = Table(
        title=f"异环 · 载具 (展示中: {data.show_name}, 拥有 {data.total})",
        show_lines=False,
    )
    t.add_column("id")
    t.add_column("name")
    t.add_column("已入手")
    for v in data.detail:
        t.add_row(v.id, v.name, "✓" if v.own else "—")
    console.print(t)


def _render_nte_areas(areas: list[NteArea], console: Console) -> None:
    t = Table(title="异环 · 区域进度", show_lines=False)
    t.add_column("id")
    t.add_column("区域")
    t.add_column("总分", justify="right")
    t.add_column("子任务种类", justify="right")
    t.add_column("子任务总数", justify="right")
    for a in areas:
        sub_total = sum(d.total for d in a.detail)
        t.add_row(a.id, a.name, str(a.total), str(len(a.detail)), str(sub_total))
    console.print(t)


def _render_nte_sign_state(state: NteSignState, console: Console) -> None:
    today = "已签到" if state.today_sign else "未签到"
    text = Text(
        f"{state.month}/{state.day} · {today} · "
        f"累计 {state.days} · 补签 {state.re_sign_cnt}",
    )
    console.print(Panel(text, title="异环签到状态"))


def _render_nte_sign_rewards(rewards: list[NteSignReward], console: Console) -> None:
    t = Table(title=f"异环 · 当月奖励池 ({len(rewards)} 天)", show_lines=False)
    t.add_column("Day", justify="right")
    t.add_column("奖励")
    t.add_column("数量", justify="right")
    for i, r in enumerate(rewards, 1):
        t.add_row(str(i), r.name, str(r.num))
    console.print(t)


# ---------- HT renderers -----------------------------------------------------


def _render_ht_record(rec: HtRoleGameRecord, console: Console) -> None:
    info = _kv_table(
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
        _render_ht_weapons(rec.weaponinfo, console)
    if rec.imitationlist:
        console.print(_named_id_table("拟态", rec.imitationlist))
    if rec.mountlist:
        console.print(_named_id_table("坐骑", rec.mountlist))
    if rec.dressfashionlist:
        console.print(_named_id_table("时装", rec.dressfashionlist))


def _render_ht_weapons(weapons: list[HtWeaponInfo], console: Console) -> None:
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
        t.add_row(str(w.id), w.id_str, w.name, str(w.star), str(w.color), str(w.lev), matrix)
    console.print(t)


def _render_ht_named_id_list(items: list[HtNamedId], console: Console) -> None:
    console.print(_named_id_table(f"{len(items)} 项", items))


def _named_id_table(title: str, items: list[HtNamedId]) -> Table:
    t = Table(title=title, show_lines=False)
    t.add_column("id")
    t.add_column("name")
    for it in items:
        t.add_row(it.id, it.name)
    return t


# ---------- generic ---------------------------------------------------------


def _render_bind_role(b: BindRole, console: Console) -> None:
    console.print(
        _kv_table(
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


def _render_account_list(accounts: list[StoredAccount], console: Console) -> None:
    from ._shared import storage  # local import to avoid cycle at module load

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
