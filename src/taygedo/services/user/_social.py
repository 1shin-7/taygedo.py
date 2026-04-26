"""Social actions — follow / unfollow / list-follows."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from taygedo.core import BearerAuthService, Body, Query, endpoint
from taygedo.models import BbsResponse, FollowsPage
from taygedo.models._base import BbsBase

__all__ = ["FollowRequest"]


class FollowRequest(BbsBase):
    """``POST /usercenter/api/{follow,unfollow}`` form body."""

    follow_ids: str = Field(alias="followIds")


class _Social(BearerAuthService):
    @endpoint.get("/usercenter/api/queryFollows")
    async def query_follows(
        self,
        uid: Annotated[int, Query()],
        count: Annotated[int, Query()] = 20,
        last_id: Annotated[int, Query(alias="lastId")] = 0,
    ) -> BbsResponse[FollowsPage]: ...

    @endpoint.post("/usercenter/api/follow")
    async def _follow_raw(
        self, body: Annotated[FollowRequest, Body(form=True)],
    ) -> BbsResponse[None]: ...

    @endpoint.post("/usercenter/api/unfollow")
    async def _unfollow_raw(
        self, body: Annotated[FollowRequest, Body(form=True)],
    ) -> BbsResponse[None]: ...

    async def follow(self, uid: int) -> BbsResponse[None]:
        return await self._follow_raw(
            body=FollowRequest.model_validate({"followIds": str(uid)}),
        )

    async def unfollow(self, uid: int) -> BbsResponse[None]:
        return await self._unfollow_raw(
            body=FollowRequest.model_validate({"followIds": str(uid)}),
        )
