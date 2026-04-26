"""HAR4 fixture replay — every new endpoint's response shape must parse.

Fixtures under ``tests/fixtures/har4_*.json`` are sanitized snapshots of
real captured payloads.
"""

from __future__ import annotations

from taygedo.models import (
    BbsResponse,
    Community,
    CreatePostResult,
    CursorPage,
    FollowsPage,
    NteSignReward,
    NteSignState,
    Post,
    PublishElementPerm,
    SysAvatar,
    Topic,
)

from ._fixtures import load_fixture


def test_unfollow() -> None:
    env = BbsResponse[None].model_validate(load_fixture("har4_idx1_unfollow"))
    assert env.is_ok


def test_update_user_info_ok() -> None:
    env = BbsResponse[bool].model_validate(load_fixture("har4_idx14_update_user_info_ok"))
    assert env.is_ok and env.data is True


def test_update_user_info_err() -> None:
    env = BbsResponse[bool].model_validate(load_fixture("har4_idx54_update_user_info_err"))
    # Server rejection: code != 0 and ok=False (in HAR sample, code=113 for invalid nickname)
    assert not env.is_ok
    assert env.code != 0
    assert env.msg


def test_get_user_sys_avatars() -> None:
    env = BbsResponse[list[SysAvatar]].model_validate(
        load_fixture("har4_idx50_get_user_sys_avatars"),
    )
    assert env.is_ok and env.data
    a = env.data[0]
    assert a.id > 0 and a.name and a.icon


def test_post_create() -> None:
    env = BbsResponse[CreatePostResult].model_validate(load_fixture("har4_idx80_post_create"))
    assert env.is_ok and env.data is not None
    assert env.data.post_id > 0


def test_get_all_community_columns() -> None:
    env = BbsResponse[list[Community]].model_validate(
        load_fixture("har4_idx84_get_all_community_columns"),
    )
    assert env.is_ok and env.data
    # Both 幻塔 (1256) and 异环 (1289) must appear
    assert {c.game_id for c in env.data} >= {1256, 1289}


def test_publish_element_perm() -> None:
    env = BbsResponse[PublishElementPerm].model_validate(
        load_fixture("har4_idx98_publish_element_perm"),
    )
    assert env.is_ok and env.data is not None
    # The captured element=tp-video request was rejected for non-verified user.
    assert env.data.can_publish is False
    assert env.data.prompt


def test_query_follows() -> None:
    env = BbsResponse[FollowsPage].model_validate(load_fixture("har4_idx99_query_follows"))
    assert env.is_ok and env.data is not None
    assert env.data.follows
    entry = env.data.follows[0]
    assert entry.user.uid > 0
    assert entry.fr.get("following") is True


def test_get_recommend_topic() -> None:
    env = BbsResponse[list[Topic]].model_validate(
        load_fixture("har4_idx286_get_recommend_topic"),
    )
    assert env.is_ok and env.data
    t = env.data[0]
    assert t.id > 0 and t.topic


def test_ht_sign_rewards() -> None:
    env = BbsResponse[list[NteSignReward]].model_validate(
        load_fixture("har4_idx356_ht_sign_rewards"),
    )
    assert env.is_ok and env.data
    # HT rewards include game-currency icons under serverlist-hotta CDN.
    assert env.data[0].num > 0


def test_ht_signin_state() -> None:
    env = BbsResponse[NteSignState].model_validate(
        load_fixture("har4_idx360_ht_signin_state"),
    )
    assert env.is_ok and env.data is not None
    assert 1 <= env.data.month <= 12
    assert 1 <= env.data.day <= 31


def test_recommend_posts_by_game() -> None:
    env = BbsResponse[CursorPage[Post]].model_validate(
        load_fixture("har4_idx382_recommend_posts_by_game"),
    )
    assert env.is_ok and env.data is not None
    assert env.data.items
