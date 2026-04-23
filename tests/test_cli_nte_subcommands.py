"""nte (& yh alias) subcommands: info / character / realestate / vehicle / area / sign."""

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


_ROLE_HOME_DATA = {
    "code": 0, "ok": True,
    "data": {
        "roleid": "200000000001",
        "rolename": "Tester",
        "userid": "u1",
        "lev": 5,
        "tycoonLevel": 2,
        "worldlevel": 1,
        "roleloginDays": 7,
        "charidCnt": 1,
        "achieveProgress": {"total": 100},
        "areaProgress": [{"id": "001", "name": "桥间地", "total": 1500}],
        "characters": [
            {
                "id": "1051",
                "name": "零",
                "quality": "ITEM_QUALITY_ORANGE",
                "elementType": "CHARACTER_ELEMENT_TYPE_COSMOS",
                "groupType": "CHARACTER_GROUP_TYPE_ONE",
            },
        ],
        "realestate": {"showId": "h1", "showName": "维纳公寓", "total": 5},
        "vehicle": {"showId": "v1", "showName": "M1000", "total": 17},
    },
}


def _full_responder() -> Callable[[PreparedRequest], Response]:
    def respond(req: PreparedRequest) -> Response:
        if req.url.endswith("/yh/roleHome"):
            return _ok(_ROLE_HOME_DATA)
        if req.url.endswith("/yh/characters"):
            return _ok(
                {
                    "code": 0, "ok": True,
                    "data": [
                        {
                            "id": "1051",
                            "name": "零",
                            "quality": "ITEM_QUALITY_ORANGE",
                            "elementType": "CHARACTER_ELEMENT_TYPE_COSMOS",
                            "groupType": "CHARACTER_GROUP_TYPE_ONE",
                            "awakenLev": 0, "awakenEffect": [],
                            "properties": [], "skills": [], "citySkills": [],
                            "fork": {"id": "", "alev": "", "blev": "",
                                     "slev": "", "properties": []},
                            "suit": {"suitActivateNum": 0},
                        },
                    ],
                },
            )
        if req.url.endswith("/yh/realestate"):
            return _ok(
                {
                    "code": 0, "ok": True,
                    "data": {
                        "total": 1,
                        "detail": [
                            {
                                "id": "h1", "name": "维纳公寓", "own": False,
                                "fdetail": [{"id": "f1", "name": "x", "own": True}],
                            },
                        ],
                    },
                },
            )
        if req.url.endswith("/yh/vehicles"):
            return _ok(
                {
                    "code": 0, "ok": True,
                    "data": {
                        "total": 1, "showId": "v1", "showName": "M1000",
                        "detail": [{"id": "v1", "name": "M1000", "own": False}],
                    },
                },
            )
        if req.url.endswith("/yh/areaProgress"):
            return _ok(
                {
                    "code": 0, "ok": True,
                    "data": [
                        {
                            "id": "001", "name": "桥间地", "total": 1500,
                            "detail": [{"id": "callbox", "name": "电话亭", "total": 2}],
                        },
                    ],
                },
            )
        if req.url.endswith("/awapi/signin/state"):
            return _ok(
                {
                    "code": 0, "ok": True,
                    "data": {
                        "month": 4, "day": 23, "days": 1,
                        "todaySign": False, "reSignCnt": 0,
                    },
                },
            )
        if req.url.endswith("/awapi/sign/rewards"):
            return _ok(
                {
                    "code": 0, "ok": True,
                    "data": [
                        {"icon": "https://x", "name": "甲硬币", "num": 10000}
                        for _ in range(30)
                    ],
                },
            )
        if req.url.endswith("/awapi/sign"):
            return _ok({"code": 0, "ok": True})
        return _ok({"code": 0, "ok": True})

    return respond


def test_nte_info(isolated_storage: Path, monkeypatch: pytest.MonkeyPatch) -> None:  # noqa: F811
    _seed(isolated_storage)
    install_scripted_client(monkeypatch, _full_responder())
    result = CliRunner().invoke(app, ["nte", "info"])
    assert result.exit_code == 0, result.output
    assert "Tester" in result.output
    assert "维纳公寓" in result.output


def test_yh_info_alias(isolated_storage: Path, monkeypatch: pytest.MonkeyPatch) -> None:  # noqa: F811
    _seed(isolated_storage)
    install_scripted_client(monkeypatch, _full_responder())
    result = CliRunner().invoke(app, ["yh", "info"])
    assert result.exit_code == 0, result.output
    assert "Tester" in result.output


def test_nte_character(isolated_storage: Path, monkeypatch: pytest.MonkeyPatch) -> None:  # noqa: F811
    _seed(isolated_storage)
    install_scripted_client(monkeypatch, _full_responder())
    result = CliRunner().invoke(app, ["nte", "character"])
    assert result.exit_code == 0, result.output
    assert "1051" in result.output and "零" in result.output


def test_nte_character_filtered(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed(isolated_storage)
    install_scripted_client(monkeypatch, _full_responder())
    result = CliRunner().invoke(app, ["nte", "character", "--id", "9999"])
    assert result.exit_code != 0


def test_nte_realestate(isolated_storage: Path, monkeypatch: pytest.MonkeyPatch) -> None:  # noqa: F811
    _seed(isolated_storage)
    install_scripted_client(monkeypatch, _full_responder())
    result = CliRunner().invoke(app, ["nte", "realestate"])
    assert result.exit_code == 0, result.output
    assert "维纳公寓" in result.output


def test_nte_vehicle(isolated_storage: Path, monkeypatch: pytest.MonkeyPatch) -> None:  # noqa: F811
    _seed(isolated_storage)
    install_scripted_client(monkeypatch, _full_responder())
    result = CliRunner().invoke(app, ["nte", "vehicle"])
    assert result.exit_code == 0, result.output
    assert "M1000" in result.output


def test_nte_area(isolated_storage: Path, monkeypatch: pytest.MonkeyPatch) -> None:  # noqa: F811
    _seed(isolated_storage)
    install_scripted_client(monkeypatch, _full_responder())
    result = CliRunner().invoke(app, ["nte", "area"])
    assert result.exit_code == 0, result.output
    assert "桥间地" in result.output


def test_nte_sign_default_signs_and_shows_reward(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed(isolated_storage)
    state = {"signed": False}

    def respond(req: PreparedRequest) -> Response:
        if req.url.endswith("/awapi/signin/state"):
            return _ok(
                {
                    "code": 0, "ok": True,
                    "data": {
                        "month": 4, "day": 1, "days": 0 if not state["signed"] else 1,
                        "todaySign": state["signed"], "reSignCnt": 0,
                    },
                },
            )
        if req.url.endswith("/awapi/sign") and req.method == "POST":
            state["signed"] = True
            return _ok({"code": 0, "ok": True})
        return _full_responder()(req)

    install_scripted_client(monkeypatch, respond)
    result = CliRunner().invoke(app, ["nte", "sign"])
    assert result.exit_code == 0, result.output
    assert "签到成功" in result.output
    assert "甲硬币" in result.output


def test_nte_sign_already_signed(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed(isolated_storage)

    def respond(req: PreparedRequest) -> Response:
        if req.url.endswith("/awapi/signin/state"):
            return _ok(
                {
                    "code": 0, "ok": True,
                    "data": {
                        "month": 4, "day": 23, "days": 5, "todaySign": True, "reSignCnt": 0,
                    },
                },
            )
        return _full_responder()(req)

    install_scripted_client(monkeypatch, respond)
    result = CliRunner().invoke(app, ["nte", "sign"])
    assert result.exit_code == 0, result.output
    assert "已签到" in result.output


def test_nte_sign_preview_does_not_sign(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed(isolated_storage)
    seen_methods: list[str] = []

    def respond(req: PreparedRequest) -> Response:
        seen_methods.append(req.method + " " + req.url)
        return _full_responder()(req)

    install_scripted_client(monkeypatch, respond)
    result = CliRunner().invoke(app, ["nte", "sign", "--preview"])
    assert result.exit_code == 0, result.output
    # No POST to /awapi/sign should have happened.
    assert not any("POST " in m and m.endswith("/awapi/sign") for m in seen_methods)
    assert "甲硬币" in result.output  # reward pool printed


def test_nte_sign_raw_dumps_json(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed(isolated_storage)
    install_scripted_client(monkeypatch, _full_responder())
    result = CliRunner().invoke(app, ["nte", "sign", "--preview", "--raw"])
    assert result.exit_code == 0, result.output
    parsed = json.loads(result.output)
    assert "state" in parsed and "rewards" in parsed
