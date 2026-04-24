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

from collections.abc import Callable, Iterable
from typing import Any

import orjson
from pydantic import BaseModel
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..models import (
    AppStartupData,
    BindRole,
    Comment,
    CommentPage,
    Community,
    CommunityHome,
    CursorPage,
    ExpLevel,
    ExpRecord,
    GameRecordCard,
    Good,
    GoodsPage,
    HotWord,
    HtNamedId,
    HtRoleGameRecord,
    HtWeaponInfo,
    NteArea,
    NteCharacter,
    NteRealestateData,
    NteRoleHome,
    NteSignReward,
    NteSignState,
    NteTeamRecommend,
    NteVehicleData,
    Post,
    PostFull,
    Reply,
    ReplyFeedPage,
    SearchTopicResult,
    SearchUsersPage,
    SignInResult,
    Task,
    Topic,
    User,
    UserFullInfo,
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


_JSON_OPTIONS = orjson.OPT_INDENT_2 | orjson.OPT_NON_STR_KEYS


def _to_json_str(value: Any) -> str:
    if isinstance(value, BaseModel):
        return value.model_dump_json(indent=2, by_alias=True)
    if isinstance(value, list) and value and isinstance(value[0], BaseModel):
        return orjson.dumps(
            [v.model_dump(mode="json", by_alias=True) for v in value],
            option=_JSON_OPTIONS,
        ).decode("utf-8")
    if hasattr(value, "to_dict"):
        return orjson.dumps(value.to_dict(), option=_JSON_OPTIONS).decode("utf-8")
    if isinstance(value, list) and value and hasattr(value[0], "to_dict"):
        return orjson.dumps(
            [v.to_dict() for v in value], option=_JSON_OPTIONS,
        ).decode("utf-8")
    try:
        return orjson.dumps(value, default=str, option=_JSON_OPTIONS).decode("utf-8")
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
    if isinstance(value, PostFull):
        return _render_post_full
    if isinstance(value, Post):
        return _render_post_single
    if isinstance(value, CommentPage):
        return _render_comment_page
    if isinstance(value, SearchTopicResult):
        return _render_search_topic_result
    if isinstance(value, SearchUsersPage):
        return _render_search_users_page
    if isinstance(value, CursorPage):
        return _render_cursor_page_of_posts
    if isinstance(value, ReplyFeedPage):
        return _render_reply_feed_page
    if isinstance(value, GoodsPage):
        return _render_goods_page
    if isinstance(value, ExpLevel):
        return _render_exp_level
    if isinstance(value, SignInResult):
        return _render_signin_result
    if isinstance(value, Community):
        return _render_community_single
    if isinstance(value, CommunityHome):
        return _render_community_home
    if isinstance(value, UserFullInfo):
        return _render_user_full_info
    if isinstance(value, AppStartupData):
        return None  # falls back to JSON — startup is a debug dump
    if isinstance(value, list) and value:
        first = value[0]
        if isinstance(first, NteCharacter):
            return _render_nte_characters
        if isinstance(first, NteArea):
            return _render_nte_areas
        if isinstance(first, NteSignReward):
            return _render_nte_sign_rewards
        if isinstance(first, NteTeamRecommend):
            return _render_nte_teams
        if isinstance(first, HtWeaponInfo):
            return _render_ht_weapons
        if isinstance(first, HtNamedId):
            return _render_ht_named_id_list
        if isinstance(first, StoredAccount):
            return _render_account_list
        if isinstance(first, Community):
            return _render_community_list
        if isinstance(first, GameRecordCard):
            return _render_game_record_cards
        if isinstance(first, Task):
            return _render_tasks
        if isinstance(first, ExpRecord):
            return _render_exp_records
        if isinstance(first, HotWord):
            return _render_hot_words
        if isinstance(first, Good):
            return _render_goods
        if isinstance(first, Topic):
            return _render_topics
        if isinstance(first, User):
            return _render_user_list
        if isinstance(first, Comment):
            return _render_comments
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


# ---------- posts / comments ------------------------------------------------


def _truncate(s: str, limit: int = 80) -> str:
    s = s.replace("\n", " ")
    return s if len(s) <= limit else s[: limit - 1] + "…"


def _render_post_single(post: Post, console: Console) -> None:
    console.print(
        _kv_table(
            f"Post #{post.post_id}",
            [
                ("subject", post.subject),
                ("uid", post.uid),
                ("community", post.community_id),
                ("column", post.column_id),
                ("type", post.type),
                ("likes", post.post_stat.like_num),
                ("comments", post.post_stat.comment_num),
                ("collects", post.post_stat.collect_num),
                ("region", post.region or "—"),
                ("created", post.create_time),
            ],
        ),
    )
    if post.content:
        console.print(Panel(Text(_truncate(post.content, 400)), title="content"))


def _render_post_full(value: PostFull, console: Console) -> None:
    _render_post_single(value.post, console)
    if value.users:
        author = value.users[0]
        console.print(
            _kv_table(
                "author",
                [
                    ("uid", author.uid),
                    ("nickname", author.nickname),
                    ("ipRegion", author.ip_region),
                ],
            ),
        )


def _render_cursor_page_of_posts(page: CursorPage[Post], console: Console) -> None:
    t = Table(title=f"Posts (page={page.page} hasMore={page.has_more})")
    t.add_column("id", style="cyan")
    t.add_column("subject")
    t.add_column("uid")
    t.add_column("likes")
    t.add_column("comments")
    for p in page.items:
        t.add_row(
            str(p.post_id),
            _truncate(p.subject, 50),
            str(p.uid),
            str(p.post_stat.like_num),
            str(p.post_stat.comment_num),
        )
    console.print(t)


def _render_reply_feed_page(page: ReplyFeedPage[Reply], console: Console) -> None:
    t = Table(title=f"Reply feed (more={page.more})")
    t.add_column("reply_id")
    t.add_column("post_id")
    t.add_column("uid")
    t.add_column("content")
    for r in page.items:
        t.add_row(
            str(r.reply_id or "—"),
            str(r.post_id or "—"),
            str(r.uid or "—"),
            _truncate(r.content, 50),
        )
    console.print(t)


def _render_comment_page(page: CommentPage, console: Console) -> None:
    # uid -> nickname lookup
    names = {u.uid: u.nickname for u in page.users}
    t = Table(title=f"Comments (page={page.page} hasMore={page.has_more})")
    t.add_column("id", style="cyan")
    t.add_column("uid")
    t.add_column("author")
    t.add_column("likes")
    t.add_column("content")
    for c in page.comments:
        likes = c.comment_stat.like_num if c.comment_stat else 0
        t.add_row(
            str(c.id),
            str(c.uid),
            names.get(c.uid, "—"),
            str(likes),
            _truncate(c.content, 50),
        )
    console.print(t)


def _render_comments(items: list[Comment], console: Console) -> None:
    t = Table(title="Comments")
    t.add_column("id", style="cyan")
    t.add_column("uid")
    t.add_column("content")
    for c in items:
        t.add_row(str(c.id), str(c.uid), _truncate(c.content, 60))
    console.print(t)


# ---------- search ----------------------------------------------------------


def _render_hot_words(words: list[HotWord], console: Console) -> None:
    t = Table(title="Hot keywords")
    t.add_column("keyword")
    t.add_column("count")
    for w in words:
        t.add_row(w.keyword, str(w.count))
    console.print(t)


def _render_topics(topics: list[Topic], console: Console) -> None:
    t = Table(title="Topics")
    t.add_column("id", style="cyan")
    t.add_column("topic")
    t.add_column("related")
    t.add_column("introduce")
    for tp in topics:
        t.add_row(
            str(tp.id),
            tp.topic,
            str(tp.related_num),
            _truncate(tp.introduce, 50),
        )
    console.print(t)


def _render_search_topic_result(result: SearchTopicResult, console: Console) -> None:
    _render_topics(result.items, console)


def _render_user_list(users: list[User], console: Console) -> None:
    t = Table(title="Users")
    t.add_column("uid", style="cyan")
    t.add_column("nickname")
    t.add_column("account")
    t.add_column("region")
    for u in users:
        t.add_row(str(u.uid), u.nickname, u.account, u.ip_region)
    console.print(t)


def _render_search_users_page(page: SearchUsersPage, console: Console) -> None:
    _render_user_list(page.items, console)


# ---------- community / shop / tasks / exp ---------------------------------


def _render_community_single(c: Community, console: Console) -> None:
    console.print(
        _kv_table(
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
            t.add_row(_truncate(getattr(b, "title", ""), 40), getattr(b, "url", ""))
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
        _kv_table(
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
        _kv_table("Signin", [("exp", r.exp), ("goldCoin", r.gold_coin)]),
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
            _truncate(g.name, 40),
            g.tab,
            str(g.price),
            str(g.stock) if g.stock else "—",
        )
    console.print(t)


def _render_goods_page(page: GoodsPage, console: Console) -> None:
    _render_goods(page.goods, console)


# ---------- user full info -------------------------------------------------


def _render_user_full_info(info: UserFullInfo, console: Console) -> None:
    u = info.user
    console.print(
        _kv_table(
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


# ---------- NTE team recommendations ---------------------------------------


def _render_nte_teams(teams: list[NteTeamRecommend], console: Console) -> None:
    t = Table(title="Team recommendations")
    t.add_column("id", style="cyan")
    t.add_column("name")
    t.add_column("desc")
    for team in teams:
        t.add_row(team.id, team.name, _truncate(team.desc, 60))
    console.print(t)
