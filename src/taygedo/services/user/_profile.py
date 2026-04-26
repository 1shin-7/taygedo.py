"""Profile read/write — full info, system avatars, profile updates."""

from __future__ import annotations

from typing import Annotated, ClassVar

from taygedo.core import BearerAuthService, Body, endpoint
from taygedo.models import BbsResponse, SysAvatar, UserFullInfo
from taygedo.models._base import BbsBase
from taygedo.signers import SignDs

__all__ = ["UpdateUserInfoRequest"]


class UpdateUserInfoRequest(BbsBase):
    """``POST /usercenter/api/updateUserInfo`` form body.

    Server treats each call as partial update — fields default to ``None``
    and are excluded from the wire payload when unset.
    """

    nickname: str | None = None
    avatar: str | None = None
    introduce: str | None = None
    gender: int | None = None


class _Profile(BearerAuthService):
    signer: ClassVar[SignDs] = SignDs()

    @endpoint.get("/usercenter/api/getUserFullInfo")
    async def get_user_full_info(self) -> BbsResponse[UserFullInfo]: ...

    @endpoint.get("/apihub/api/assets/getUserSysAvatars")
    async def list_sys_avatars(self) -> BbsResponse[list[SysAvatar]]: ...

    @endpoint.post("/usercenter/api/updateUserInfo")
    async def update_info(
        self, body: Annotated[UpdateUserInfoRequest, Body(form=True)],
    ) -> BbsResponse[bool]: ...
