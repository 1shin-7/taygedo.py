"""BBS community / app-startup / shop / tasks endpoints (non-game)."""

from __future__ import annotations

from typing import Annotated, ClassVar

from pydantic import Field

from ..core import BearerAuthService, Body, Query, endpoint
from ..models import (
    AppConfig,
    AppStartupData,
    BbsResponse,
    CoinTaskState,
    ColumnHome,
    Community,
    CommunityHome,
    CursorPage,
    ExpLevel,
    GameRecordCard,
    GoodsPage,
    Post,
    SignInResult,
    UnreadCount,
    UserTasks,
)
from ..models._base import BbsBase
from ..signers import SignDs

__all__ = ["CommunityService", "SigninRequest"]


class SigninRequest(BbsBase):
    """``POST /apihub/api/signin`` form body."""

    community_id: int = Field(alias="communityId")


class CommunityService(BearerAuthService):
    signer: ClassVar[SignDs] = SignDs()

    # --- app-level configuration --------------------------------------------

    @endpoint.get("/apihub/api/getAppConfig")
    async def get_app_config(self) -> BbsResponse[AppConfig]: ...

    @endpoint.get("/apihub/api/getAppStartupData")
    async def get_app_startup_data(self) -> BbsResponse[AppStartupData]: ...

    # --- community / column listings ----------------------------------------

    @endpoint.get("/apihub/api/getAllCommunity")
    async def list_all(self) -> BbsResponse[list[Community]]: ...

    @endpoint.get("/apihub/api/getCommunityHome")
    async def get_home(
        self, community_id: Annotated[int, Query(alias="communityId")],
    ) -> BbsResponse[CommunityHome]: ...

    @endpoint.get("/apihub/api/getColumnHome")
    async def get_column_home(
        self, column_id: Annotated[int, Query(alias="columnId")],
    ) -> BbsResponse[ColumnHome]: ...

    # --- post feeds ---------------------------------------------------------

    @endpoint.get("/bbs/api/getRecommendPostList")
    async def recommend_posts(
        self,
        community_id: Annotated[int, Query(alias="communityId")],
        page: Annotated[int, Query()] = 1,
        count: Annotated[int, Query()] = 20,
    ) -> BbsResponse[CursorPage[Post]]: ...

    @endpoint.get("/bbs/api/getOfficialPostList")
    async def official_posts(
        self,
        community_id: Annotated[int, Query(alias="communityId")],
        column_id: Annotated[int, Query(alias="columnId")],
        official_type: Annotated[int, Query(alias="officialType")] = 1,
        page: Annotated[int, Query()] = 1,
        count: Annotated[int, Query()] = 20,
        sort_type: Annotated[int, Query(alias="sortType")] = 1,
        version: Annotated[int, Query()] = 0,
    ) -> BbsResponse[CursorPage[Post]]: ...

    # --- game record cards (mounted on user.community page) -----------------

    @endpoint.get("/apihub/api/getGameRecordCard")
    async def get_game_record_cards(
        self, uid: Annotated[int, Query()],
    ) -> BbsResponse[list[GameRecordCard]]: ...

    # --- App-side community signin (NOT the in-game sign-in) ---------------

    @endpoint.get("/apihub/api/getSignState")
    async def get_sign_state(
        self, community_id: Annotated[int, Query(alias="communityId")],
    ) -> BbsResponse[bool]: ...

    @endpoint.post("/apihub/api/signin")
    async def signin(
        self, body: Annotated[SigninRequest, Body(form=True)],
    ) -> BbsResponse[SignInResult]: ...

    # --- task / exp / coin system ------------------------------------------

    @endpoint.get("/apihub/api/getUserTasks")
    async def get_user_tasks(
        self,
        community_id: Annotated[int, Query(alias="communityId")],
        gid: Annotated[int, Query()] = 2,
    ) -> BbsResponse[UserTasks]: ...

    @endpoint.get("/apihub/api/getUserCoinTaskState")
    async def get_coin_task_state(self) -> BbsResponse[CoinTaskState]: ...

    @endpoint.get("/apihub/api/getUserExpLevel")
    async def get_exp_level(
        self, community_id: Annotated[int, Query(alias="communityId")],
    ) -> BbsResponse[ExpLevel]: ...

    # --- shop ---------------------------------------------------------------

    @endpoint.get("/apihub/api/shop/listGoods")
    async def list_goods(
        self,
        tab: Annotated[str, Query()] = "all",
        version: Annotated[int, Query()] = 0,
        count: Annotated[int, Query()] = 20,
    ) -> BbsResponse[GoodsPage]: ...

    # --- existing -----------------------------------------------------------

    @endpoint.get("/apihub/api/getUserUnreadCnt")
    async def get_user_unread_cnt(self) -> BbsResponse[UnreadCount]: ...
