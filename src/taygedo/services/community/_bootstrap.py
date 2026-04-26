"""App-level configuration + community/column listings + game cards + unread."""

from __future__ import annotations

from typing import Annotated, ClassVar

from taygedo.core import BearerAuthService, Query, endpoint
from taygedo.models import (
    AppConfig,
    AppStartupData,
    BbsResponse,
    ColumnHome,
    Community,
    CommunityHome,
    GameRecordCard,
    UnreadCount,
)
from taygedo.signers import SignDs


class _Bootstrap(BearerAuthService):
    signer: ClassVar[SignDs] = SignDs()

    @endpoint.get("/apihub/api/getAppConfig")
    async def get_app_config(self) -> BbsResponse[AppConfig]: ...

    @endpoint.get("/apihub/api/getAppStartupData")
    async def get_app_startup_data(self) -> BbsResponse[AppStartupData]: ...

    @endpoint.get("/apihub/api/getAllCommunity")
    async def list_all(self) -> BbsResponse[list[Community]]: ...

    @endpoint.get("/apihub/api/getAllCommunityColumns")
    async def list_all_columns(self) -> BbsResponse[list[Community]]: ...

    @endpoint.get("/apihub/api/getCommunityHome")
    async def get_home(
        self, community_id: Annotated[int, Query(alias="communityId")],
    ) -> BbsResponse[CommunityHome]: ...

    @endpoint.get("/apihub/api/getColumnHome")
    async def get_column_home(
        self, column_id: Annotated[int, Query(alias="columnId")],
    ) -> BbsResponse[ColumnHome]: ...

    @endpoint.get("/apihub/api/getGameRecordCard")
    async def get_game_record_cards(
        self, uid: Annotated[int, Query()],
    ) -> BbsResponse[list[GameRecordCard]]: ...

    @endpoint.get("/apihub/api/getUserUnreadCnt")
    async def get_user_unread_cnt(self) -> BbsResponse[UnreadCount]: ...
