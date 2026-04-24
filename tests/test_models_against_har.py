"""Validate every model against fixture payloads.

These fixtures are committed JSON snapshots produced from real captures
(sanitized to remove all PII). The test suite has no external-file
dependency beyond the repo.
"""

from __future__ import annotations

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

from ._fixtures import load_fixture

# --- envelopes ---------------------------------------------------------------


def test_bbs_envelope_with_signin_result() -> None:
    env = BbsResponse[SignInResult].model_validate(load_fixture("har1_idx64_signin_result"))
    assert env.is_ok
    assert env.code == 0
    assert env.data is not None
    assert env.data.exp == 5
    assert env.data.gold_coin == 40


def test_laohu_envelope_with_sms_login_result() -> None:
    env = LaohuResponse[SmsLoginResult].model_validate(load_fixture("har1_idx100_sms_login"))
    assert env.is_ok
    assert env.result is not None
    assert env.result.user_id > 0
    assert len(env.result.token) == 32  # 32-hex MD5-like token
    assert env.result.user_identify is not None
    assert env.result.user_identify.user_id == env.result.user_id


# --- bbs payloads ------------------------------------------------------------


def test_app_config() -> None:
    env = BbsResponse[AppConfig].model_validate(load_fixture("har1_idx125_app_config"))
    assert env.data == AppConfig(env_id="10", version="1.0.0")


def test_app_startup_data() -> None:
    env = BbsResponse[AppStartupData].model_validate(
        load_fixture("har1_idx122_app_startup_data"),
    )
    assert env.data is not None
    cfg = env.data.app_configs
    assert cfg.min_version == "1.1.8"
    assert cfg.last_version == "1.2.0"
    parsed = cfg.im_config_parsed()
    assert {e.game_id for e in parsed} == {"1256", "1289"}
    assert env.data.emoticons[0].items[0].name


def test_get_all_community_returns_list_of_community() -> None:
    env = BbsResponse[list[Community]].model_validate(
        load_fixture("har1_idx123_get_all_community"),
    )
    assert env.data is not None
    by_game = {c.game_id: c for c in env.data}
    assert {1256, 1289} <= set(by_game.keys())
    g1289 = by_game[1289]
    assert g1289.id == 2


def test_get_community_home() -> None:
    env = BbsResponse[CommunityHome].model_validate(load_fixture("har1_idx121_community_home"))
    assert env.data is not None
    assert env.data.community.id == 2
    assert len(env.data.banners) >= 1
    assert env.data.navigator and env.data.navigator[0].name


def test_user_full_info() -> None:
    env = BbsResponse[UserFullInfo].model_validate(load_fixture("har1_idx4_get_user_full_info"))
    assert env.data is not None
    assert env.data.user.uid > 0
    assert isinstance(env.data.user.nickname, str)
    assert env.data.user_stat.uid == env.data.user.uid
    assert env.data.privacy_setting.privacy_collect is True
    assert {a.community_id for a in env.data.auths} == {1, 2}


def test_game_record_card() -> None:
    env = BbsResponse[list[GameRecordCard]].model_validate(
        load_fixture("har1_idx5_game_record_card"),
    )
    assert env.data is not None
    card = env.data[0]
    assert card.game_id == 1256
    assert card.bind_role_info.role_id > 0
    assert isinstance(card.bind_role_info.role_name, str)


def test_game_bind_role() -> None:
    env = BbsResponse[BindRole].model_validate(load_fixture("har1_idx38_get_game_bind_role_ht"))
    assert env.data is not None
    assert env.data.role_id > 0
    assert env.data.server_name != ""


def test_game_roles_v2_empty() -> None:
    env = BbsResponse[GameRolesData].model_validate(
        load_fixture("har1_idx0_get_game_roles_v2_empty"),
    )
    assert env.data is not None
    assert env.data.bind_role == 0
    assert env.data.roles == []


def test_ht_role_game_record() -> None:
    env = BbsResponse[HtRoleGameRecord].model_validate(load_fixture("har1_idx36_ht_role_record"))
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
    env = BbsResponse[CursorPage[Post]].model_validate(
        load_fixture("har1_idx120_recommend_post_list"),
    )
    assert env.data is not None
    assert env.data.has_more is True
    assert env.data.page == 2
    assert len(env.data.items) > 0
    first = env.data.items[0]
    assert first.post_id > 0
    assert first.uid > 0
    assert first.post_stat.like_num >= 0


def test_official_post_list_video_post_with_cover() -> None:
    env = BbsResponse[CursorPage[Post]].model_validate(
        load_fixture("har1_idx119_official_post_list"),
    )
    assert env.data is not None
    # First post in the official list is the video PV.
    video_post = env.data.items[0]
    assert video_post.type == 3
    assert video_post.cover is not None
    assert video_post.cover.url.endswith(".png")
    assert len(video_post.vods) == 1
    assert video_post.vods[0].duration == 254


def test_user_tasks() -> None:
    env = BbsResponse[UserTasks].model_validate(load_fixture("har1_idx61_user_tasks"))
    assert env.data is not None
    keys = {t.task_key for t in env.data.task_list3}
    assert "signin_exp" in keys
    signin = next(t for t in env.data.task_list3 if t.task_key == "signin_exp")
    assert signin.complete_times == 1
    assert signin.exp == 5


def test_coin_task_state() -> None:
    env = BbsResponse[CoinTaskState].model_validate(load_fixture("har1_idx94_coin_task_state"))
    assert env.data == CoinTaskState(today_get=0, today_total=150, total=130)


def test_exp_level() -> None:
    env = BbsResponse[ExpLevel].model_validate(load_fixture("har1_idx62_exp_level"))
    assert env.data is not None
    assert env.data.level == 1
    assert env.data.next_level_exp == 40


def test_exp_records_list() -> None:
    env = BbsResponse[list[ExpRecord]].model_validate(load_fixture("har1_idx63_exp_records"))
    assert env.data is not None
    assert len(env.data) == 1
    rec = env.data[0]
    assert rec.num == 5
    assert rec.type == 3


def test_sign_state_is_bool() -> None:
    env = BbsResponse[bool].model_validate(load_fixture("har1_idx96_sign_state_bool"))
    assert env.data is False


def test_bbs_login() -> None:
    env = BbsResponse[BbsLoginResult].model_validate(load_fixture("har1_idx99_bbs_login"))
    assert env.data is not None
    assert env.data.uid > 0
    assert env.data.access_token != ""
    assert env.data.refresh_token != ""


# --- laohu payloads ----------------------------------------------------------


def test_init_config() -> None:
    env = LaohuResponse[InitConfig].model_validate(load_fixture("har1_idx129_init_config"))
    assert env.result is not None
    assert env.result.one_key_sms_login.app_key.startswith("977207056B082")
    assert env.result.real_name_status == 2
    assert env.result.login_option_config == [15]


def test_area_code_list() -> None:
    env = LaohuResponse[list[AreaCode]].model_validate(load_fixture("har1_idx128_area_code_list"))
    assert env.result is not None
    china = next(a for a in env.result if a.area_code_id == 1)
    assert china.area_code == 86


def test_web_view_url() -> None:
    env = LaohuResponse[WebViewUrls].model_validate(load_fixture("har1_idx130_web_view_urls"))
    assert env.result is not None
    assert env.result.qq_url.startswith("https://graph.qq.com")
    assert env.result.pw_url.startswith("https://passport.wanmei.com")


# --- defensive: every fixture at least produces a top-level dict + 'code' ---


@pytest.mark.parametrize(
    "name",
    [
        "har1_idx0_get_game_roles_v2_empty",
        "har1_idx1_get_all_games",
        "har1_idx2_user_browse_records",
        "har1_idx3_user_post_list",
        "har1_idx4_get_user_full_info",
        "har1_idx5_game_record_card",
        "har1_idx36_ht_role_record",
        "har1_idx38_get_game_bind_role_ht",
        "har1_idx55_user_collect_posts",
        "har1_idx57_user_reply_feeds",
        "har1_idx61_user_tasks",
        "har1_idx62_exp_level",
        "har1_idx63_exp_records",
        "har1_idx64_signin_result",
        "har1_idx94_coin_task_state",
        "har1_idx96_sign_state_bool",
        "har1_idx99_bbs_login",
        "har1_idx100_sms_login",
        "har1_idx101_check_captcha",
        "har1_idx102_send_captcha",
        "har1_idx118_column_home",
        "har1_idx119_official_post_list",
        "har1_idx120_recommend_post_list",
        "har1_idx121_community_home",
        "har1_idx122_app_startup_data",
        "har1_idx123_get_all_community",
        "har1_idx125_app_config",
        "har1_idx128_area_code_list",
        "har1_idx129_init_config",
        "har1_idx130_web_view_urls",
    ],
)
def test_fixture_is_valid_json(name: str) -> None:
    """Every targeted endpoint must produce a parseable JSON envelope."""
    payload = load_fixture(name)
    assert isinstance(payload, dict)
    # Both envelopes share the 'code' key.
    assert "code" in payload
