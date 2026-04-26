"""Read-side post endpoints — full content, comments, publish-permission check."""

from __future__ import annotations

from typing import Annotated, ClassVar

from taygedo.core import BearerAuthService, Query, endpoint
from taygedo.models import BbsResponse, CommentPage, PostFull, PublishElementPerm
from taygedo.signers import SignDs


class _Read(BearerAuthService):
    signer: ClassVar[SignDs] = SignDs()

    @endpoint.get("/bbs/api/getPostFull")
    async def get_post(
        self, post_id: Annotated[int, Query(alias="postId")],
    ) -> BbsResponse[PostFull]: ...

    @endpoint.get("/bbs/api/getComments")
    async def get_comments(
        self,
        post_id: Annotated[int, Query(alias="postId")],
        count: Annotated[int, Query()] = 20,
        sort_type: Annotated[int, Query(alias="sortType")] = 2,
        version: Annotated[int, Query()] = 0,
        owner: Annotated[bool, Query()] = False,
    ) -> BbsResponse[CommentPage]: ...

    @endpoint.get("/bbs/api/publishElementPerm")
    async def publish_element_perm(
        self, element: Annotated[str, Query()],
    ) -> BbsResponse[PublishElementPerm]: ...
