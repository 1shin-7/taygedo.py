"""Post + topic discovery feeds — recommend / official / topics."""

from __future__ import annotations

from typing import Annotated

from taygedo.core import BearerAuthService, Query, endpoint
from taygedo.models import BbsResponse, CursorPage, Post, Topic


class _Feeds(BearerAuthService):
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

    @endpoint.get("/bbs/api/getRecommendTopic")
    async def recommend_topics(
        self, community_id: Annotated[int, Query(alias="communityId")],
    ) -> BbsResponse[list[Topic]]: ...
