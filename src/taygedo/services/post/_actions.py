"""Engagement actions on posts — like, collect, comment."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from taygedo.core import BearerAuthService, Body, endpoint
from taygedo.models import AddCommentRequest, BbsResponse, CommentSubmitResult
from taygedo.models._base import BbsBase

__all__ = ["PostIdRequest"]


class PostIdRequest(BbsBase):
    """Form body shared by ``/bbs/api/post/like`` and ``/bbs/api/post/collect``."""

    post_id: int = Field(alias="postId")


class _Actions(BearerAuthService):
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
