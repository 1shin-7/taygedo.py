"""Renderer dispatches the right table for each known model."""

from __future__ import annotations

from io import StringIO

from rich.console import Console

from taygedo.cli._render import render
from taygedo.cli._storage import StoredAccount
from taygedo.models import (
    BindRole,
    HtNamedId,
    HtRoleGameRecord,
    HtWeaponInfo,
    NteArea,
    NteAreaDetail,
    NteCharacter,
    NteRealestateData,
    NteRoleHome,
    NteSignReward,
    NteSignState,
    NteVehicle,
    NteVehicleData,
)


def _capture(value: object, *, json_out: bool = False) -> str:
    buf = StringIO()
    console = Console(file=buf, width=120, force_terminal=False, no_color=True)
    render(value, json_out=json_out, console=console)
    return buf.getvalue()


# ---------- JSON fallback ---------------------------------------------------


def test_json_output_for_pydantic_model() -> None:
    state = NteSignState.model_validate(
        {"month": 4, "day": 23, "days": 1, "todaySign": True, "reSignCnt": 0},
    )
    out = _capture(state, json_out=True)
    assert '"month": 4' in out
    assert '"todaySign": true' in out


def test_json_output_for_pydantic_list() -> None:
    rewards = [NteSignReward(icon="https://x", name="甲硬币", num=10000)]
    out = _capture(rewards, json_out=True)
    assert "甲硬币" in out
    assert "10000" in out


def test_json_output_for_stored_account_list() -> None:
    a = StoredAccount(uid=1, nickname="z", cellphone_masked="138****8000")
    out = _capture([a], json_out=True)
    assert '"uid": 1' in out


# ---------- table renderers -------------------------------------------------


def test_role_home_renders_overview_table() -> None:
    home = NteRoleHome.model_validate(
        {
            "roleid": "12345",
            "rolename": "Tester",
            "userid": "u1",
            "lev": 5,
            "tycoonLevel": 2,
            "worldlevel": 1,
            "roleloginDays": 7,
            "charidCnt": 3,
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
    )
    out = _capture(home)
    assert "Tester" in out
    assert "12345" in out
    assert "维纳公寓" in out
    assert "M1000" in out
    assert "桥间地" in out
    assert "零" in out


def test_characters_table_lists_by_id() -> None:
    chars = [
        NteCharacter.model_validate(
            {
                "id": "1051",
                "name": "零",
                "quality": "ITEM_QUALITY_ORANGE",
                "elementType": "CHARACTER_ELEMENT_TYPE_COSMOS",
                "groupType": "CHARACTER_GROUP_TYPE_ONE",
                "awakenLev": 0,
                "awakenEffect": [],
                "properties": [],
                "skills": [],
                "citySkills": [],
                "fork": {"id": "", "alev": "", "blev": "", "slev": "", "properties": []},
                "suit": {"suitActivateNum": 0},
            },
        ),
    ]
    out = _capture(chars)
    assert "1051" in out
    assert "零" in out
    assert "ITEM_QUALITY_ORANGE" in out


def test_realestate_renders_owned_furniture_count() -> None:
    data = NteRealestateData.model_validate(
        {
            "total": 1,
            "detail": [
                {
                    "id": "h1",
                    "name": "维纳公寓",
                    "own": False,
                    "fdetail": [
                        {"id": "f1", "name": "x", "own": True},
                        {"id": "f2", "name": "y", "own": False},
                    ],
                },
            ],
        },
    )
    out = _capture(data)
    assert "维纳公寓" in out
    assert "1/2" in out


def test_vehicles_renders_show_name() -> None:
    data = NteVehicleData(
        total=1,
        show_id="v1",
        show_name="M1000",
        detail=[NteVehicle(id="v1", name="M1000", own=False)],
    )
    out = _capture(data)
    assert "M1000" in out


def test_areas_renders_per_area_subtask_total() -> None:
    areas = [
        NteArea(
            id="001", name="桥间地", total=1500,
            detail=[
                NteAreaDetail(id="callbox", name="电话亭", total=2),
                NteAreaDetail(id="yushi", name="谕石", total=37),
            ],
        ),
    ]
    out = _capture(areas)
    assert "桥间地" in out
    assert "1500" in out
    # Sub-task total = 2+37
    assert "39" in out


def test_sign_state_renders_signed_state() -> None:
    state = NteSignState(month=4, day=23, days=1, today_sign=True, re_sign_cnt=0)
    out = _capture(state)
    assert "已签到" in out
    assert "累计 1" in out


def test_ht_record_renders_overview_and_subtables() -> None:
    rec = HtRoleGameRecord.model_validate(
        {
            "roleid": "1000000000001",
            "rolename": "TesterHT",
            "userid": "9_111111",
            "groupname": "10001",
            "lev": 100,
            "shengelev": "11_3",
            "maxgs": 269447,
            "imitationCount": 86,
            "achievementpointall": "7201",
            "weaponinfo": [
                {
                    "ID": 6960,
                    "IDStr": "Paradox_fire",
                    "name": "EP-7000",
                    "Star": 6,
                    "Color": 4,
                    "Lev": 200,
                    "MatrixInfoList": [],
                },
            ],
            "imitationlist": [{"name": "TestImitation", "ID": "imitation_4"}],
        },
    )
    out = _capture(rec)
    assert "TesterHT" in out
    assert "EP-7000" in out
    assert "TestImitation" in out


def test_ht_weapons_table() -> None:
    out = _capture(
        [
            HtWeaponInfo.model_validate(
                {
                    "ID": 1,
                    "IDStr": "x",
                    "name": "Sword",
                    "Star": 6,
                    "Color": 4,
                    "Lev": 100,
                    "MatrixInfoList": [],
                },
            ),
        ],
    )
    assert "Sword" in out


def test_named_id_list_renders() -> None:
    out = _capture([HtNamedId(name="TestImitation", **{"ID": "imitation_4"})])  # type: ignore[arg-type]
    assert "TestImitation" in out
    assert "imitation_4" in out


def test_bind_role_renders() -> None:
    b = BindRole.model_validate(
        {
            "gameId": 1256,
            "roleId": 1000000000001,
            "roleName": "TesterHT",
            "serverId": 14508,
            "serverName": "TestServer",
            "account": "9_x",
            "lev": 100,
        },
    )
    out = _capture(b)
    assert "1256" in out
    assert "TesterHT" in out
