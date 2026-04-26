"""异环 (NTE) renderers."""

from __future__ import annotations

from collections.abc import Callable

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from taygedo.cli._render._helpers import kv_table, truncate
from taygedo.models import (
    NteArea,
    NteCharacter,
    NteRealestateData,
    NteRoleHome,
    NteSignReward,
    NteSignState,
    NteTeamRecommend,
    NteVehicleData,
)


def _render_role_home(home: NteRoleHome, console: Console) -> None:
    info = kv_table(
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


def _render_characters(chars: list[NteCharacter], console: Console) -> None:
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
            c.id, c.name, c.quality, c.element_type, c.group_type,
            str(c.awaken_lev), str(len(c.properties)), str(len(c.skills)),
        )
    console.print(t)


def _render_realestate(data: NteRealestateData, console: Console) -> None:
    t = Table(title=f"异环 · 不动产 (拥有 {data.total})", show_lines=False)
    t.add_column("id")
    t.add_column("name")
    t.add_column("已入手")
    t.add_column("家具", justify="right")
    for h in data.detail:
        owned = sum(1 for f in h.fdetail if f.own)
        t.add_row(h.id, h.name, "✓" if h.own else "—", f"{owned}/{len(h.fdetail)}")
    console.print(t)


def _render_vehicles(data: NteVehicleData, console: Console) -> None:
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


def _render_areas(areas: list[NteArea], console: Console) -> None:
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


def _render_sign_state(state: NteSignState, console: Console) -> None:
    today = "已签到" if state.today_sign else "未签到"
    text = Text(
        f"{state.month}/{state.day} · {today} · "
        f"累计 {state.days} · 补签 {state.re_sign_cnt}",
    )
    console.print(Panel(text, title="异环签到状态"))


def _render_sign_rewards(rewards: list[NteSignReward], console: Console) -> None:
    t = Table(title=f"异环 · 当月奖励池 ({len(rewards)} 天)", show_lines=False)
    t.add_column("Day", justify="right")
    t.add_column("奖励")
    t.add_column("数量", justify="right")
    for i, r in enumerate(rewards, 1):
        t.add_row(str(i), r.name, str(r.num))
    console.print(t)


def _render_teams(teams: list[NteTeamRecommend], console: Console) -> None:
    t = Table(title="Team recommendations")
    t.add_column("id", style="cyan")
    t.add_column("name")
    t.add_column("desc")
    for team in teams:
        t.add_row(team.id, team.name, truncate(team.desc, 60))
    console.print(t)


def register(
    single: dict[type, Callable[..., None]],
    listed: dict[type, Callable[..., None]],
) -> None:
    single[NteRoleHome] = _render_role_home
    single[NteRealestateData] = _render_realestate
    single[NteVehicleData] = _render_vehicles
    single[NteSignState] = _render_sign_state
    listed[NteCharacter] = _render_characters
    listed[NteArea] = _render_areas
    listed[NteSignReward] = _render_sign_rewards
    listed[NteTeamRecommend] = _render_teams
