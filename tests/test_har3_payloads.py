"""HAR3 fixture replay — every new endpoint's response shape must parse.

Fixtures under ``tests/fixtures/har3_*.json`` are sanitized snapshots of
real captured payloads.
"""

from __future__ import annotations

from taygedo.models import (
    AppConfig,
    AppStartupData,
    BbsResponse,
    CoinTaskState,
    ColumnHome,
    CommentPage,
    CommentSubmitResult,
    Community,
    CommunityHome,
    CursorPage,
    ExpLevel,
    ExpRecord,
    GameRecordCard,
    GoodsPage,
    HotWord,
    NteTeamRecommend,
    Post,
    PostFull,
    Reply,
    ReplyFeedPage,
    SearchTopicResult,
    SearchUsersPage,
    SignInResult,
    UserTasks,
)

from ._fixtures import load_fixture

# --- App-level / community listings ----------------------------------------


def test_app_config() -> None:
    env = BbsResponse[AppConfig].model_validate(load_fixture("har3_idx298_app_config"))
    assert env.is_ok and env.data is not None
    assert env.data.env_id != ""
    assert env.data.version != ""


def test_app_startup_data() -> None:
    env = BbsResponse[AppStartupData].model_validate(
        load_fixture("har3_idx300_app_startup_data"),
    )
    assert env.is_ok and env.data is not None


def test_get_all_community() -> None:
    env = BbsResponse[list[Community]].model_validate(
        load_fixture("har3_idx299_get_all_community"),
    )
    assert env.is_ok and env.data
    assert {c.game_id for c in env.data} >= {1256, 1289}


def test_get_community_home() -> None:
    env = BbsResponse[CommunityHome].model_validate(load_fixture("har3_idx301_community_home"))
    assert env.is_ok and env.data is not None
    assert env.data.community.id > 0


def test_get_column_home() -> None:
    env = BbsResponse[ColumnHome].model_validate(load_fixture("har3_idx289_column_home"))
    assert env.is_ok and env.data is not None
    assert env.data.column.id > 0


def test_get_game_record_card() -> None:
    env = BbsResponse[list[GameRecordCard]].model_validate(
        load_fixture("har3_idx138_game_record_card"),
    )
    assert env.is_ok and env.data
    card = env.data[0]
    assert card.game_id in {1256, 1289}
    assert card.bind_role_info.role_id > 0


# --- App signin + tasks + exp + coin ---------------------------------------


def test_get_sign_state_returns_bool() -> None:
    env = BbsResponse[bool].model_validate(load_fixture("har3_idx268_sign_state_bool"))
    assert env.is_ok
    assert isinstance(env.data, bool)


def test_signin() -> None:
    env = BbsResponse[SignInResult].model_validate(load_fixture("har3_idx91_app_signin"))
    assert env.is_ok and env.data is not None
    assert env.data.exp >= 0
    assert env.data.gold_coin >= 0


def test_get_user_tasks() -> None:
    env = BbsResponse[UserTasks].model_validate(load_fixture("har3_idx2_user_tasks"))
    assert env.is_ok and env.data is not None
    assert any(t.task_key == "signin_exp" for t in env.data.task_list3)


def test_get_user_coin_task_state() -> None:
    env = BbsResponse[CoinTaskState].model_validate(load_fixture("har3_idx261_coin_task_state"))
    assert env.is_ok and env.data is not None
    assert env.data.today_total >= 0


def test_get_user_exp_level() -> None:
    env = BbsResponse[ExpLevel].model_validate(load_fixture("har3_idx1_exp_level"))
    assert env.is_ok and env.data is not None
    assert env.data.level >= 1
    assert env.data.next_level_exp > 0


def test_get_user_exp_records_empty() -> None:
    env = BbsResponse[list[ExpRecord]].model_validate(load_fixture("har3_idx3_exp_records"))
    assert env.is_ok
    assert env.data == [] or all(isinstance(r, ExpRecord) for r in env.data or [])


def test_shop_list_goods() -> None:
    env = BbsResponse[GoodsPage].model_validate(load_fixture("har3_idx265_shop_list_goods"))
    assert env.is_ok and env.data is not None
    assert env.data.goods
    g0 = env.data.goods[0]
    assert g0.id > 0 and g0.price > 0


# --- post feeds / details / comments / actions ------------------------------


def test_recommend_posts() -> None:
    env = BbsResponse[CursorPage[Post]].model_validate(load_fixture("har3_idx290_recommend_posts"))
    assert env.is_ok and env.data is not None
    assert env.data.items
    p = env.data.items[0]
    assert p.post_id > 0


def test_official_posts() -> None:
    env = BbsResponse[CursorPage[Post]].model_validate(load_fixture("har3_idx291_official_posts"))
    assert env.is_ok and env.data is not None
    assert env.data.items


def test_get_post_full() -> None:
    env = BbsResponse[PostFull].model_validate(load_fixture("har3_idx173_get_post_full"))
    assert env.is_ok and env.data is not None
    assert env.data.post.post_id > 0
    assert env.data.users


def test_get_comments() -> None:
    env = BbsResponse[CommentPage].model_validate(load_fixture("har3_idx166_get_comments"))
    assert env.is_ok and env.data is not None
    assert env.data.comments
    c = env.data.comments[0]
    assert c.id > 0 and c.post_id > 0


def test_post_like() -> None:
    env = BbsResponse[bool].model_validate(load_fixture("har3_idx176_post_like"))
    assert env.is_ok and env.data is True


def test_post_collect() -> None:
    env = BbsResponse[bool].model_validate(load_fixture("har3_idx175_post_collect"))
    assert env.is_ok and env.data is True


def test_add_comment() -> None:
    env = BbsResponse[CommentSubmitResult].model_validate(
        load_fixture("har3_idx178_add_comment"),
    )
    assert env.is_ok and env.data is not None
    assert env.data.comment.id > 0
    assert env.data.users


# --- user feeds + follow ---------------------------------------------------


def test_get_user_browse_records() -> None:
    env = BbsResponse[CursorPage[Post]].model_validate(
        load_fixture("har3_idx145_user_browse_records"),
    )
    assert env.is_ok


def test_get_user_collect_posts() -> None:
    env = BbsResponse[CursorPage[Post]].model_validate(
        load_fixture("har3_idx146_user_collect_posts"),
    )
    assert env.is_ok


def test_get_user_post_list() -> None:
    env = BbsResponse[CursorPage[Post]].model_validate(
        load_fixture("har3_idx148_user_post_list"),
    )
    assert env.is_ok


def test_get_user_reply_feeds() -> None:
    env = BbsResponse[ReplyFeedPage[Reply]].model_validate(
        load_fixture("har3_idx147_user_reply_feeds"),
    )
    assert env.is_ok and env.data is not None
    assert env.data.items


def test_follow() -> None:
    env = BbsResponse[None].model_validate(load_fixture("har3_idx199_follow"))
    assert env.is_ok


# --- search ----------------------------------------------------------------


def test_search_post() -> None:
    env = BbsResponse[CursorPage[Post]].model_validate(load_fixture("har3_idx155_search_post"))
    assert env.is_ok and env.data is not None
    assert env.data.items


def test_search_topic() -> None:
    env = BbsResponse[SearchTopicResult].model_validate(
        load_fixture("har3_idx159_search_topic"),
    )
    assert env.is_ok and env.data is not None
    assert env.data.items


def test_search_user() -> None:
    env = BbsResponse[SearchUsersPage].model_validate(load_fixture("har3_idx160_search_user"))
    assert env.is_ok and env.data is not None
    assert env.data.items


def test_search_hot_words() -> None:
    env = BbsResponse[list[HotWord]].model_validate(load_fixture("har3_idx162_search_hot_words"))
    assert env.is_ok
    assert env.data and env.data[0].keyword


# --- NTE team --------------------------------------------------------------


def test_nte_team() -> None:
    env = BbsResponse[list[NteTeamRecommend]].model_validate(load_fixture("har3_idx353_nte_team"))
    assert env.is_ok and env.data
    t = env.data[0]
    assert t.id and t.name and t.imgs
