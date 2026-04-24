"""Validate every NTE model against fixture payloads (sanitized HAR2 snapshots)."""

from __future__ import annotations

from taygedo.models import (
    BbsResponse,
    NteArea,
    NteCharacter,
    NteRealestateData,
    NteRoleHome,
    NteSignReward,
    NteSignState,
    NteVehicleData,
    UnreadCount,
)

from ._fixtures import load_fixture


def test_role_home() -> None:
    env = BbsResponse[NteRoleHome].model_validate(load_fixture("har2_idx63_role_home"))
    assert env.is_ok
    data = env.data
    assert data is not None
    assert data.roleid.isdigit()
    assert data.lev >= 0
    assert data.charid_cnt >= 1
    assert data.area_progress and data.area_progress[0].id == "001"
    assert data.characters and data.characters[0].quality.startswith("ITEM_QUALITY_")
    assert data.realestate.total >= 0
    assert data.vehicle.total >= 0
    assert data.achieve_progress.total > 0


def test_characters_full_schema() -> None:
    env = BbsResponse[list[NteCharacter]].model_validate(load_fixture("har2_idx54_characters"))
    assert env.is_ok
    chars = env.data
    assert chars is not None and len(chars) >= 1
    c = chars[0]
    assert c.id and c.name
    assert c.element_type.startswith("CHARACTER_ELEMENT_TYPE_")
    assert c.group_type.startswith("CHARACTER_GROUP_TYPE_")
    prop_ids = {p.id for p in c.properties}
    assert {"hpmax", "atk", "def", "crit"} <= prop_ids
    assert c.skills, "no skills decoded"
    melee = c.skills[0]
    assert melee.type == "Proactive"
    assert melee.items
    assert c.city_skills and c.city_skills[0].type == "City"
    assert c.suit.suit_activate_num >= 0
    assert c.fork.id == "" and c.fork.properties == []


def test_realestate() -> None:
    env = BbsResponse[NteRealestateData].model_validate(load_fixture("har2_idx27_realestate"))
    assert env.is_ok
    data = env.data
    assert data is not None
    assert data.detail
    house = data.detail[0]
    assert house.id.startswith("bigword_")
    assert house.fdetail
    f0 = house.fdetail[0]
    assert f0.id.startswith("SF_")
    assert isinstance(f0.own, bool)


def test_vehicles() -> None:
    env = BbsResponse[NteVehicleData].model_validate(load_fixture("har2_idx29_vehicles"))
    assert env.is_ok
    data = env.data
    assert data is not None
    assert data.total >= 1
    assert data.show_id.startswith("vehicle")
    assert data.detail and data.detail[0].id.startswith("vehicle")


def test_area_progress() -> None:
    env = BbsResponse[list[NteArea]].model_validate(load_fixture("har2_idx52_area_progress"))
    assert env.is_ok
    areas = env.data
    assert areas is not None and len(areas) >= 1
    a = areas[0]
    assert a.id == "001"
    assert a.detail and {d.id for d in a.detail} >= {"yushi"}


def test_sign_rewards() -> None:
    env = BbsResponse[list[NteSignReward]].model_validate(load_fixture("har2_idx114_sign_rewards"))
    assert env.is_ok
    rewards = env.data
    assert rewards is not None and len(rewards) >= 1
    r0 = rewards[0]
    assert r0.icon.startswith("https://webstatic.tajiduo.com/")
    assert r0.num > 0


def test_signin_state() -> None:
    env = BbsResponse[NteSignState].model_validate(load_fixture("har2_idx118_signin_state"))
    assert env.is_ok
    s = env.data
    assert s is not None
    assert 1 <= s.month <= 12
    assert 1 <= s.day <= 31
    assert s.days >= 0
    assert s.today_sign is True


def test_unread_cnt() -> None:
    env = BbsResponse[UnreadCount].model_validate(load_fixture("har2_idx160_unread_cnt"))
    assert env.is_ok
    nu = env.data.notification_unread
    assert nu.id > 0
    assert nu.uid > 0
    assert nu.create_time > 0
