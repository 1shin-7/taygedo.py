"""Smoke integration tests for the new CLI subcommands."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner

from taygedo.cli import app
from taygedo.cli._storage import Storage, StoredAccount
from taygedo.core import PreparedRequest, Response

from ._cli_fixtures import install_scripted_client, isolated_storage  # noqa: F401


def _seed(tmp_path: Path) -> None:
    Storage(config_dir=tmp_path).upsert_account(
        StoredAccount(
            uid=10000001,
            nickname="tester",
            cellphone_masked="138****0000",
            access_token="at",
            refresh_token="rt",
            laohu_token="lt",
            laohu_user_id=999,
            device_id="dev",
        ),
        set_active=True,
    )


def _ok(payload: dict[str, Any]) -> Response:
    return Response(
        status_code=200,
        headers={"content-type": "application/json"},
        content=json.dumps(payload).encode("utf-8"),
    )


def _responder() -> Callable[[PreparedRequest], Response]:
    def respond(req: PreparedRequest) -> Response:
        u = req.url
        if u.endswith("/getAllCommunity"):
            return _ok(
                {
                    "code": 0, "ok": True,
                    "data": [
                        {
                            "id": 2, "name": "异环", "gameId": 1289, "state": 0,
                            "createTime": 1000, "columns": [],
                        },
                        {
                            "id": 1, "name": "幻塔", "gameId": 1256, "state": 0,
                            "createTime": 1000, "columns": [],
                        },
                    ],
                },
            )
        if u.endswith("/getSignState"):
            return _ok({"code": 0, "ok": True, "data": False})
        if u.endswith("/apihub/api/signin"):
            return _ok({"code": 0, "ok": True, "data": {"exp": 5, "goldCoin": 40}})
        if u.endswith("/getUserExpLevel"):
            return _ok(
                {
                    "code": 0, "ok": True,
                    "data": {
                        "exp": 17, "level": 1, "levelExp": 17,
                        "nextLevel": 2, "nextLevelExp": 40, "todayExp": 0,
                    },
                },
            )
        if u.endswith("/getUserCoinTaskState"):
            return _ok(
                {
                    "code": 0, "ok": True,
                    "data": {"todayGet": 0, "todayTotal": 150, "total": 230},
                },
            )
        if u.endswith("/getUserTasks"):
            return _ok(
                {
                    "code": 0, "ok": True,
                    "data": {
                        "task_list3": [
                            {
                                "taskKey": "signin_exp", "title": "签到",
                                "exp": 5, "coin": 0, "completeTimes": 0,
                                "targetTimes": 1, "limitTimes": 1, "contTimes": 0,
                                "period": 20260425, "uid": 1,
                            },
                        ],
                    },
                },
            )
        if u.endswith("/shop/listGoods"):
            return _ok(
                {
                    "code": 0, "ok": True,
                    "data": {
                        "goods": [
                            {
                                "id": 12, "name": "游戏名片", "cover": "x", "icon": "y",
                                "price": 40, "sale": 0.0, "state": 1, "tab": "yh",
                            },
                        ],
                    },
                },
            )
        if u.endswith("/searchHotWords"):
            return _ok(
                {
                    "code": 0, "ok": True,
                    "data": [{"keyword": "Persona1", "count": 11}],
                },
            )
        if u.endswith("/searchTopic"):
            return _ok(
                {
                    "code": 0, "ok": True,
                    "data": {
                        "list": [
                            {
                                "id": 28, "topic": "Persona1",
                                "cover": "x", "icon": "y", "introduce": "desc",
                                "readNum": 0, "relatedNum": 1000,
                                "recommendTime": 0, "state": 0, "type": 0,
                                "createTime": 0, "updateTime": 0,
                            },
                        ],
                        "more": False, "page": 1,
                    },
                },
            )
        if u.endswith("/searchUser"):
            return _ok(
                {
                    "code": 0, "ok": True,
                    "data": {
                        "list": [
                            {
                                "uid": 10000002, "nickname": "matcher",
                                "account": "9_x", "ipRegion": "x",
                            },
                        ],
                        "more": False, "page": 1,
                    },
                },
            )
        if u.endswith("/searchPost"):
            return _ok(
                {
                    "code": 0, "ok": True,
                    "data": {
                        "hasMore": False, "page": 1, "version": 0,
                        "users": [],
                        "posts": [
                            {
                                "postId": 1001, "uid": 1, "communityId": 2,
                                "columnId": 4, "subject": "Hello", "content": "...",
                                "type": 1, "postStat": {"postId": 1001},
                            },
                        ],
                    },
                },
            )
        if u.endswith("/getPostFull"):
            return _ok(
                {
                    "code": 0, "ok": True,
                    "data": {
                        "post": {
                            "postId": 1001, "uid": 1, "communityId": 2,
                            "columnId": 4, "subject": "Hi", "content": "x",
                            "type": 1, "postStat": {"postId": 1001},
                        },
                        "users": [{"uid": 1, "nickname": "author"}],
                        "topics": [],
                        "hot": True,
                        "draftId": 0,
                    },
                },
            )
        if u.endswith("/getComments"):
            return _ok(
                {
                    "code": 0, "ok": True,
                    "data": {
                        "comments": [
                            {
                                "id": 10, "postId": 1001, "uid": 2,
                                "content": "nice", "createTime": 0,
                                "updateTime": 0, "isDelete": False,
                                "showingMissing": False, "parentId": 0,
                                "replyUid": 0,
                                "commentStat": {
                                    "commentId": 10, "postId": 1001,
                                    "likeNum": 3, "replyNum": 0,
                                },
                            },
                        ],
                        "users": [{"uid": 2, "nickname": "commenter"}],
                        "hasMore": False, "page": 1, "version": 0,
                    },
                },
            )
        if u.endswith("/post/like") or u.endswith("/post/collect"):
            return _ok({"code": 0, "ok": True, "data": True})
        if u.endswith("/apihub/api/getGameRecordCard"):
            return _ok(
                {
                    "code": 0, "ok": True,
                    "data": [
                        {
                            "gameId": 1289, "gameName": "异环",
                            "bindRoleInfo": {
                                "gameId": 1289, "roleId": 1, "roleName": "r",
                                "serverId": 1, "serverName": "s", "account": "a", "lev": 1,
                            },
                        },
                    ],
                },
            )
        if u.endswith("/yh/team"):
            return _ok(
                {
                    "code": 0, "ok": True,
                    "data": [
                        {"id": "1046", "name": "零", "icon": "x", "desc": "d", "imgs": []},
                    ],
                },
            )
        return _ok({"code": 0, "ok": True})

    return respond


def test_community_list(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed(isolated_storage)
    install_scripted_client(monkeypatch, _responder())
    result = CliRunner().invoke(app, ["community", "list"])
    assert result.exit_code == 0, result.output
    assert "异环" in result.output
    assert "幻塔" in result.output


def test_community_signin_awards_exp_and_coin(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed(isolated_storage)
    install_scripted_client(monkeypatch, _responder())
    result = CliRunner().invoke(app, ["community", "signin"])
    assert result.exit_code == 0, result.output
    assert "社区签到成功" in result.output
    assert "5" in result.output and "40" in result.output


def test_community_tasks(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed(isolated_storage)
    install_scripted_client(monkeypatch, _responder())
    result = CliRunner().invoke(app, ["community", "tasks"])
    assert result.exit_code == 0, result.output
    assert "signin_exp" in result.output


def test_community_exp(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed(isolated_storage)
    install_scripted_client(monkeypatch, _responder())
    result = CliRunner().invoke(app, ["community", "exp"])
    assert result.exit_code == 0, result.output


def test_community_shop(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed(isolated_storage)
    install_scripted_client(monkeypatch, _responder())
    result = CliRunner().invoke(app, ["community", "shop"])
    assert result.exit_code == 0, result.output
    assert "游戏名片" in result.output


def test_search_hot(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed(isolated_storage)
    install_scripted_client(monkeypatch, _responder())
    result = CliRunner().invoke(app, ["search", "hot"])
    assert result.exit_code == 0, result.output
    assert "Persona1" in result.output


def test_search_topics(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed(isolated_storage)
    install_scripted_client(monkeypatch, _responder())
    result = CliRunner().invoke(app, ["search", "topics", "Persona1"])
    assert result.exit_code == 0, result.output
    assert "Persona1" in result.output


def test_search_users(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed(isolated_storage)
    install_scripted_client(monkeypatch, _responder())
    result = CliRunner().invoke(app, ["search", "users", "matcher"])
    assert result.exit_code == 0, result.output
    assert "matcher" in result.output


def test_search_posts(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed(isolated_storage)
    install_scripted_client(monkeypatch, _responder())
    result = CliRunner().invoke(app, ["search", "posts", "hi"])
    assert result.exit_code == 0, result.output
    assert "Hello" in result.output


def test_post_show(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed(isolated_storage)
    install_scripted_client(monkeypatch, _responder())
    result = CliRunner().invoke(app, ["post", "show", "1001"])
    assert result.exit_code == 0, result.output
    assert "author" in result.output


def test_post_comments(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed(isolated_storage)
    install_scripted_client(monkeypatch, _responder())
    result = CliRunner().invoke(app, ["post", "comments", "1001"])
    assert result.exit_code == 0, result.output
    assert "nice" in result.output
    assert "commenter" in result.output


def test_post_like(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed(isolated_storage)
    install_scripted_client(monkeypatch, _responder())
    result = CliRunner().invoke(app, ["post", "like", "1001"])
    assert result.exit_code == 0, result.output
    assert "liked post 1001" in result.output


def test_post_collect(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed(isolated_storage)
    install_scripted_client(monkeypatch, _responder())
    result = CliRunner().invoke(app, ["post", "collect", "1001"])
    assert result.exit_code == 0, result.output
    assert "collected post 1001" in result.output


def test_user_follow(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed(isolated_storage)
    install_scripted_client(monkeypatch, _responder())
    result = CliRunner().invoke(app, ["user", "follow", "99"])
    assert result.exit_code == 0, result.output
    assert "followed uid=99" in result.output


def test_nte_team(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed(isolated_storage)
    install_scripted_client(monkeypatch, _responder())
    result = CliRunner().invoke(app, ["nte", "team"])
    assert result.exit_code == 0, result.output
    assert "零" in result.output


def test_nte_cards(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed(isolated_storage)
    install_scripted_client(monkeypatch, _responder())
    result = CliRunner().invoke(app, ["nte", "cards"])
    assert result.exit_code == 0, result.output
    assert "异环" in result.output


def test_ht_sign_placeholder(
    isolated_storage: Path,  # noqa: F811
) -> None:
    result = CliRunner().invoke(app, ["ht", "sign"])
    assert result.exit_code != 0
    assert "NOT YET IMPLEMENTED" in result.output or "暂未实现" in result.output


def test_tof_alias_for_sign_placeholder(
    isolated_storage: Path,  # noqa: F811
) -> None:
    result = CliRunner().invoke(app, ["tof", "sign"])
    assert result.exit_code != 0
