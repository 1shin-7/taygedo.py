"""Validate services/ht.py shapes against fixture payloads."""

from __future__ import annotations

from taygedo.models import BbsResponse, BindRole, HtRoleGameRecord

from ._fixtures import load_fixture


def test_get_game_bind_role_parses_as_bindrole() -> None:
    env = BbsResponse[BindRole].model_validate(load_fixture("har1_idx38_get_game_bind_role_ht"))
    assert env.is_ok
    assert env.data is not None
    assert env.data.game_id == 1256
    assert env.data.role_id > 0
    assert env.data.role_name != ""


def test_get_role_game_record_parses_as_htrolegamerecord() -> None:
    env = BbsResponse[HtRoleGameRecord].model_validate(load_fixture("har1_idx36_ht_role_record"))
    assert env.is_ok
    rec = env.data
    assert rec is not None
    assert rec.lev > 0
    assert rec.maxgs > 0
    assert rec.imitation_count > 0
    # Schema sanity: weapons + lists are populated.
    assert rec.weaponinfo and rec.weaponinfo[0].matrix_info_list
    assert rec.imitationlist and rec.mountlist
