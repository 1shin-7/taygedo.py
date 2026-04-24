"""User-profile, feeds, follow endpoints."""

from __future__ import annotations

from typing import Annotated, ClassVar

from pydantic import Field

from ..core import BearerAuthService, Body, Query, endpoint
from ..models import (
    BbsResponse,
    CursorPage,
    ExpRecord,
    Post,
    Reply,
    ReplyFeedPage,
    UserFullInfo,
)
from ..models._base import BbsBase
from ..signers import SignDs

__all__ = ["FollowRequest", "UserService"]


class FollowRequest(BbsBase):
    """``POST /usercenter/api/follow`` form body.

    ``followIds`` is a single uid in the captured HAR; the wire name is
    plural because the server may accept comma-separated ids in bulk.
    """

    follow_ids: str = Field(alias="followIds")


class UserService(BearerAuthService):
    signer: ClassVar[SignDs] = SignDs()

    # --- profile ------------------------------------------------------------

    @endpoint.get("/usercenter/api/getUserFullInfo")
    async def get_user_full_info(self) -> BbsResponse[UserFullInfo]: ...

    # --- exp records --------------------------------------------------------

    @endpoint.get("/usercenter/api/getUserExpRecords")
    async def get_exp_records(
        self, community_id: Annotated[int, Query(alias="communityId")] = 2,
    ) -> BbsResponse[list[ExpRecord]]: ...

    # --- feeds scoped to a uid ---------------------------------------------

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

    # --- social actions -----------------------------------------------------

    @endpoint.post("/usercenter/api/follow")
    async def _follow_raw(
        self, body: Annotated[FollowRequest, Body(form=True)],
    ) -> BbsResponse[None]: ...

    async def follow(self, uid: int) -> BbsResponse[None]:
        """Follow a single user. Server returns ``{code: 0}`` on success."""
        return await self._follow_raw(
            body=FollowRequest.model_validate({"followIds": str(uid)}),
        )
