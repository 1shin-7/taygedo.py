"""Validate every model against real HAR payloads from _dev_data.

We pin specific HAR entry indices (cross-referenced with _dev_data/api-doc.md)
and assert the parsed model exposes the expected key fields. This is the
contract that protects against accidental schema drift in models/.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import pytest

from taygedo.models import (
    AppConfig,
    AppStartupData,
    AreaCode,
    BbsLoginResult,
    BbsResponse,
    BindRole,
    CoinTaskState,
    Community,
    CommunityHome,
    CursorPage,
    ExpLevel,
    ExpRecord,
    GameRecordCard,
    GameRolesData,
    HtRoleGameRecord,
    InitConfig,
    LaohuResponse,
    Post,
    SignInResult,
    SmsLoginResult,
    UserFullInfo,
    UserTasks,
    WebViewUrls,
)

HAR_PATH = (
    Path(__file__).parent.parent
    / "_dev_data"
    / "bbs-api.tajiduo.com_2026_04_21_11_10_31.har"
)


@lru_cache(maxsize=1)
def _load_entries() -> list[dict[str, Any]]:
    with HAR_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    return data["log"]["entries"]


def _payload(idx: int) -> Any:
    """Return the JSON body of the response at ``idx``."""
    entry = _load_entries()[idx]
    body = entry["response"]["content"]["text"]
    return json.loads(body)


# --- envelopes ---------------------------------------------------------------


def test_bbs_envelope_with_signin_result() -> None:
    env = BbsResponse[SignInResult].model_validate(_payload(64))
    assert env.is_ok
    assert env.code == 0
    assert env.data is not None
    assert env.data.exp == 5
    assert env.data.gold_coin == 40


def test_laohu_envelope_with_sms_login_result() -> None:
    env = LaohuResponse[SmsLoginResult].model_validate(_payload(100))
    assert env.is_ok
    assert env.result is not None
    assert env.result.user_id > 0
    assert len(env.result.token) == 32  # 32-hex MD5-like token
    assert env.result.user_identify is not None
    assert env.result.user_identify.user_id == env.result.user_id


# --- bbs payloads ------------------------------------------------------------


def test_app_config() -> None:
    env = BbsResponse[AppConfig].model_validate(_payload(125))
    assert env.data == AppConfig(env_id="10", version="1.0.0")


def test_app_startup_data() -> None:
    env = BbsResponse[AppStartupData].model_validate(_payload(122))
    assert env.data is not None
    cfg = env.data.app_configs
    assert cfg.min_version == "1.1.8"
    assert cfg.last_version == "1.2.0"
    parsed = cfg.im_config_parsed()
    assert {e.game_id for e in parsed} == {"1256", "1289"}
    assert env.data.emoticons[0].items[0].name.startswith("你好海特洛")


def test_get_all_community_returns_list_of_community() -> None:
    env = BbsResponse[list[Community]].model_validate(_payload(123))
    assert env.data is not None
    names = {c.name for c in env.data}
    assert names == {"异环", "幻塔"}
    yh = next(c for c in env.data if c.name == "异环")
    assert yh.id == 2
    assert yh.game_id == 1289
    assert {col.column_name for col in yh.columns} >= {"「袋先生」邮箱"}


def test_get_community_home() -> None:
    env = BbsResponse[CommunityHome].model_validate(_payload(121))
    assert env.data is not None
    assert env.data.community.id == 2
    assert len(env.data.banners) >= 1
    assert env.data.navigator[0].name == "任务中心"


def test_user_full_info() -> None:
    env = BbsResponse[UserFullInfo].model_validate(_payload(4))
    assert env.data is not None
    assert env.data.user.uid > 0
    assert isinstance(env.data.user.nickname, str)
    assert env.data.user_stat.uid == env.data.user.uid
    assert env.data.privacy_setting.privacy_collect is True
    assert {a.community_id for a in env.data.auths} == {1, 2}


def test_game_record_card() -> None:
    env = BbsResponse[list[GameRecordCard]].model_validate(_payload(5))
    assert env.data is not None
    card = env.data[0]
    assert card.game_id == 1256
    assert card.bind_role_info.role_id > 0
    assert isinstance(card.bind_role_info.role_name, str)


def test_game_bind_role() -> None:
    env = BbsResponse[BindRole].model_validate(_payload(38))
    assert env.data is not None
    assert env.data.role_id > 0
    assert env.data.server_name != ""


def test_game_roles_v2_empty() -> None:
    env = BbsResponse[GameRolesData].model_validate(_payload(0))
    assert env.data is not None
    assert env.data.bind_role == 0
    assert env.data.roles == []


def test_ht_role_game_record() -> None:
    env = BbsResponse[HtRoleGameRecord].model_validate(_payload(36))
    assert env.data is not None
    rec = env.data
    assert rec.roleid.isdigit()
    assert isinstance(rec.rolename, str) and rec.rolename != ""
    assert rec.lev > 0
    weapon = rec.weaponinfo[0]
    assert weapon.id > 0
    assert isinstance(weapon.name, str)
    assert len(weapon.matrix_info_list) == 4
    assert len(rec.imitationlist) > 0


def test_recommend_post_list_pagination() -> None:
    env = BbsResponse[CursorPage[Post]].model_validate(_payload(120))
    assert env.data is not None
    assert env.data.has_more is True
    assert env.data.page == 2
    assert len(env.data.items) > 0
    first = env.data.items[0]
    assert first.post_id > 0
    assert first.uid > 0
    assert first.post_stat.like_num >= 0


def test_official_post_list_video_post_with_cover() -> None:
    env = BbsResponse[CursorPage[Post]].model_validate(_payload(119))
    assert env.data is not None
    # First post in the official list is the video PV.
    video_post = env.data.items[0]
    assert video_post.type == 3
    assert video_post.cover is not None
    assert video_post.cover.url.endswith(".png")
    assert len(video_post.vods) == 1
    assert video_post.vods[0].duration == 254


def test_user_tasks() -> None:
    env = BbsResponse[UserTasks].model_validate(_payload(61))
    assert env.data is not None
    keys = {t.task_key for t in env.data.task_list3}
    assert "signin_exp" in keys
    signin = next(t for t in env.data.task_list3 if t.task_key == "signin_exp")
    assert signin.complete_times == 1
    assert signin.exp == 5


def test_coin_task_state() -> None:
    env = BbsResponse[CoinTaskState].model_validate(_payload(94))
    assert env.data == CoinTaskState(today_get=0, today_total=150, total=130)


def test_exp_level() -> None:
    env = BbsResponse[ExpLevel].model_validate(_payload(62))
    assert env.data is not None
    assert env.data.level == 1
    assert env.data.next_level_exp == 40


def test_exp_records_list() -> None:
    env = BbsResponse[list[ExpRecord]].model_validate(_payload(63))
    assert env.data is not None
    assert len(env.data) == 1
    rec = env.data[0]
    assert rec.title == "签到"
    assert rec.num == 5
    assert rec.type == 3


def test_sign_state_is_bool() -> None:
    env = BbsResponse[bool].model_validate(_payload(96))
    assert env.data is False


def test_bbs_login() -> None:
    env = BbsResponse[BbsLoginResult].model_validate(_payload(99))
    assert env.data is not None
    assert env.data.uid > 0
    assert env.data.access_token != ""
    assert env.data.refresh_token != ""


# --- laohu payloads ----------------------------------------------------------


def test_init_config() -> None:
    env = LaohuResponse[InitConfig].model_validate(_payload(129))
    assert env.result is not None
    assert env.result.one_key_sms_login.app_key.startswith("977207056B082")
    assert env.result.real_name_status == 2
    assert env.result.login_option_config == [15]


def test_area_code_list() -> None:
    env = LaohuResponse[list[AreaCode]].model_validate(_payload(128))
    assert env.result is not None
    china = next(a for a in env.result if a.area_code_id == 1)
    assert china.area_code == 86
    assert china.area_name == "中国内地"


def test_web_view_url() -> None:
    env = LaohuResponse[WebViewUrls].model_validate(_payload(130))
    assert env.result is not None
    assert env.result.qq_url.startswith("https://graph.qq.com")
    assert env.result.pw_url.startswith("https://passport.wanmei.com")


# --- defensive: every payload at least parses without ValidationError --------


@pytest.mark.parametrize(
    "idx",
    [
        0, 1, 2, 3, 4, 5, 36, 38, 55, 57, 61, 62, 63, 64,
        94, 96, 99, 100, 101, 102, 118, 119, 120, 121, 122, 123, 125,
        128, 129, 130,
    ],
)
def test_payload_is_valid_json(idx: int) -> None:
    """Every targeted endpoint must at least produce parseable JSON."""
    payload = _payload(idx)
    assert isinstance(payload, dict)
    # Both envelopes share the 'code' key.
    assert "code" in payload
