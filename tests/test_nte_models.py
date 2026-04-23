"""Validate every NTE model against real HAR2 payloads.

HAR2 = ``_dev_data/webstatic.tajiduo.com_2026_04_23_08_25_44.har`` — the
异环 (gameId=1289) capture taken on 2026-04-23. Indices are pinned to the
specific entries we care about.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

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

HAR_PATH = (
    Path(__file__).parent.parent
    / "_dev_data"
    / "webstatic.tajiduo.com_2026_04_23_08_25_44.har"
)


@lru_cache(maxsize=1)
def _entries() -> list[dict[str, Any]]:
    with HAR_PATH.open(encoding="utf-8") as f:
        return json.load(f)["log"]["entries"]


def _payload(idx: int) -> Any:
    return json.loads(_entries()[idx]["response"]["content"]["text"])


def test_role_home_idx63() -> None:
    env = BbsResponse[NteRoleHome].model_validate(_payload(63))
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


def test_characters_idx54_full_schema() -> None:
    env = BbsResponse[list[NteCharacter]].model_validate(_payload(54))
    assert env.is_ok
    chars = env.data
    assert chars is not None and len(chars) >= 1
    c = chars[0]
    assert c.id and c.name
    assert c.element_type.startswith("CHARACTER_ELEMENT_TYPE_")
    assert c.group_type.startswith("CHARACTER_GROUP_TYPE_")
    # Full property block is 25 entries — at least the basics must be present.
    prop_ids = {p.id for p in c.properties}
    assert {"hpmax", "atk", "def", "crit"} <= prop_ids
    # First skill is "鉴痕" (id ends in _melee) with rich-text items kept verbatim.
    assert c.skills, "no skills decoded"
    melee = c.skills[0]
    assert melee.type == "Proactive"
    assert melee.items and "<Title>" in (melee.items[0].title or melee.items[0].desc)
    # citySkills + suit + (empty) fork
    assert c.city_skills and c.city_skills[0].type == "City"
    assert c.suit.suit_activate_num >= 0
    assert c.fork.id == "" and c.fork.properties == []


def test_realestate_idx27() -> None:
    env = BbsResponse[NteRealestateData].model_validate(_payload(27))
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


def test_vehicles_idx29() -> None:
    env = BbsResponse[NteVehicleData].model_validate(_payload(29))
    assert env.is_ok
    data = env.data
    assert data is not None
    assert data.total >= 1
    assert data.show_id.startswith("vehicle")
    assert data.detail and data.detail[0].id.startswith("vehicle")


def test_area_progress_idx52() -> None:
    env = BbsResponse[list[NteArea]].model_validate(_payload(52))
    assert env.is_ok
    areas = env.data
    assert areas is not None and len(areas) >= 1
    a = areas[0]
    assert a.id == "001" and a.name == "桥间地"
    assert a.detail and {d.id for d in a.detail} >= {"yushi"}


def test_sign_rewards_idx114() -> None:
    env = BbsResponse[list[NteSignReward]].model_validate(_payload(114))
    assert env.is_ok
    rewards = env.data
    assert rewards is not None and len(rewards) >= 1
    r0 = rewards[0]
    assert r0.icon.startswith("https://webstatic.tajiduo.com/")
    assert r0.num > 0


def test_signin_state_idx118() -> None:
    env = BbsResponse[NteSignState].model_validate(_payload(118))
    assert env.is_ok
    s = env.data
    assert s is not None
    assert 1 <= s.month <= 12
    assert 1 <= s.day <= 31
    assert s.days >= 0
    assert s.today_sign is True


def test_unread_cnt_idx160() -> None:
    env = BbsResponse[UnreadCount].model_validate(_payload(160))
    assert env.is_ok
    nu = env.data.notification_unread
    assert nu.id > 0
    assert nu.uid > 0
    assert nu.create_time > 0
