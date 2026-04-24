"""Post viewing, comments, and engagement endpoints under ``/bbs/api/*``."""

from __future__ import annotations

from typing import Annotated, ClassVar

from pydantic import Field

from ..core import BearerAuthService, Body, Query, endpoint
from ..models import (
    AddCommentRequest,
    BbsResponse,
    CommentPage,
    CommentSubmitResult,
    PostFull,
)
from ..models._base import BbsBase
from ..signers import SignDs

__all__ = ["PostIdRequest", "PostService"]


class PostIdRequest(BbsBase):
    """Form body shared by ``/bbs/api/post/like`` and ``/bbs/api/post/collect``."""

    post_id: int = Field(alias="postId")


class PostService(BearerAuthService):
    """Post detail + comments + likes + collects + comment submission."""

    signer: ClassVar[SignDs] = SignDs()

    # --- read --------------------------------------------------------------

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

    # --- write -------------------------------------------------------------

    @endpoint.post("/bbs/api/post/like")
    async def _like_raw(
        self, body: Annotated[PostIdRequest, Body(form=True)],
    ) -> BbsResponse[bool]: ...

    @endpoint.post("/bbs/api/post/collect")
    async def _collect_raw(
        self, body: Annotated[PostIdRequest, Body(form=True)],
    ) -> BbsResponse[bool]: ...

    async def like(self, post_id: int) -> BbsResponse[bool]:
        return await self._like_raw(
            body=PostIdRequest.model_validate({"postId": post_id}),
        )

    async def collect(self, post_id: int) -> BbsResponse[bool]:
        return await self._collect_raw(
            body=PostIdRequest.model_validate({"postId": post_id}),
        )

    @endpoint.post("/bbs/api/comment")
    async def add_comment(
        self, body: Annotated[AddCommentRequest, Body()],
    ) -> BbsResponse[CommentSubmitResult]: ...
