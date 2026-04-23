"""Validate services/ht.py shapes by re-parsing HAR1 ground-truth payloads."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from taygedo.models import BbsResponse, BindRole, HtRoleGameRecord

HAR1 = (
    Path(__file__).parent.parent
    / "_dev_data"
    / "bbs-api.tajiduo.com_2026_04_21_11_10_31.har"
)


def _entries() -> list[dict[str, Any]]:
    with HAR1.open(encoding="utf-8") as f:
        return json.load(f)["log"]["entries"]


def _payload(idx: int) -> Any:
    return json.loads(_entries()[idx]["response"]["content"]["text"])


def test_get_game_bind_role_idx38_parses_as_bindrole() -> None:
    env = BbsResponse[BindRole].model_validate(_payload(38))
    assert env.is_ok
    assert env.data is not None
    assert env.data.game_id == 1256
    assert env.data.role_id > 0
    assert env.data.role_name != ""


def test_get_role_game_record_idx36_parses_as_htrolegamerecord() -> None:
    env = BbsResponse[HtRoleGameRecord].model_validate(_payload(36))
    assert env.is_ok
    rec = env.data
    assert rec is not None
    assert rec.lev > 0
    assert rec.maxgs > 0
    assert rec.imitation_count > 0
    # Schema sanity: weapons + lists are populated.
    assert rec.weaponinfo and rec.weaponinfo[0].matrix_info_list
    assert rec.imitationlist and rec.mountlist
