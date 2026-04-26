"""App-side BBS community sign-in (NOT the in-game sign-in)."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from taygedo.core import BearerAuthService, Body, Query, endpoint
from taygedo.models import BbsResponse, SignInResult
from taygedo.models._base import BbsBase

__all__ = ["SigninRequest"]


class SigninRequest(BbsBase):
    """``POST /apihub/api/signin`` form body."""

    community_id: int = Field(alias="communityId")


class _Signin(BearerAuthService):
    @endpoint.get("/apihub/api/getSignState")
    async def get_sign_state(
        self, community_id: Annotated[int, Query(alias="communityId")],
    ) -> BbsResponse[bool]: ...

    @endpoint.post("/apihub/api/signin")
    async def signin(
        self, body: Annotated[SigninRequest, Body(form=True)],
    ) -> BbsResponse[SignInResult]: ...
