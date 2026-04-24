"""Search endpoints for posts / topics / users / hot words."""

from __future__ import annotations

from typing import Annotated, ClassVar

from ..core import BearerAuthService, Query, endpoint
from ..models import (
    BbsResponse,
    CursorPage,
    HotWord,
    Post,
    SearchTopicResult,
    SearchUsersPage,
)
from ..signers import SignDs

__all__ = ["SearchService"]


class SearchService(BearerAuthService):
    """Cross-cutting search across posts / topics / users / hot keywords."""

    signer: ClassVar[SignDs] = SignDs()

    @endpoint.get("/bbs/api/searchPost")
    async def search_posts(
        self,
        keyword: Annotated[str, Query()],
        community_id: Annotated[int, Query(alias="communityId")] = 2,
        page: Annotated[int, Query()] = 1,
        size: Annotated[int, Query()] = 20,
        order_type: Annotated[int, Query(alias="orderType")] = 1,
    ) -> BbsResponse[CursorPage[Post]]: ...

    @endpoint.get("/bbs/api/searchTopic")
    async def search_topics(
        self,
        keyword: Annotated[str, Query()],
        size: Annotated[int, Query()] = 20,
    ) -> BbsResponse[SearchTopicResult]: ...

    @endpoint.get("/usercenter/api/searchUser")
    async def search_users(
        self,
        keyword: Annotated[str, Query()],
        page: Annotated[int, Query()] = 1,
        size: Annotated[int, Query()] = 20,
    ) -> BbsResponse[SearchUsersPage]: ...

    @endpoint.get("/bbs/api/searchHotWords")
    async def hot_words(
        self, community_id: Annotated[int, Query(alias="communityId")] = 2,
    ) -> BbsResponse[list[HotWord]]: ...
