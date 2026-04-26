"""Post creation — ``POST /bbs/api/post`` with a full Quill HTML body."""

from __future__ import annotations

from typing import Annotated

from taygedo.core import BearerAuthService, Body, endpoint
from taygedo.models import BbsResponse, CreatePostRequest, CreatePostResult


class _Create(BearerAuthService):
    @endpoint.post("/bbs/api/post")
    async def create(
        self, body: Annotated[CreatePostRequest, Body()],
    ) -> BbsResponse[CreatePostResult]: ...
