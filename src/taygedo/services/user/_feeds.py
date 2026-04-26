"""User-scoped post / collect / reply feeds."""

from __future__ import annotations

from typing import Annotated

from taygedo.core import BearerAuthService, Query, endpoint
from taygedo.models import BbsResponse, CursorPage, Post, Reply, ReplyFeedPage


class _Feeds(BearerAuthService):
    @endpoint.get("/bbs/api/getUserBrowseRecords")
    async def get_browse_records(
        self,
        uid: Annotated[int, Query()],
        count: Annotated[int, Query()] = 20,
        version: Annotated[int, Query()] = 0,
    ) -> BbsResponse[CursorPage[Post]]: ...

    @endpoint.get("/bbs/api/getUserCollectPosts")
    async def get_collect_posts(
        self,
        uid: Annotated[int, Query()],
        count: Annotated[int, Query()] = 20,
        version: Annotated[int, Query()] = 0,
    ) -> BbsResponse[CursorPage[Post]]: ...

    @endpoint.get("/bbs/api/getUserPostList")
    async def get_post_list(
        self,
        uid: Annotated[int, Query()],
        count: Annotated[int, Query()] = 10,
        version: Annotated[int, Query()] = 0,
    ) -> BbsResponse[CursorPage[Post]]: ...

    @endpoint.get("/bbs/api/getUserReplyFeeds")
    async def get_reply_feeds(
        self,
        uid: Annotated[int, Query()],
        count: Annotated[int, Query()] = 20,
        version: Annotated[int, Query()] = 0,
    ) -> BbsResponse[ReplyFeedPage[Reply]]: ...
