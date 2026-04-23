"""User-profile endpoints under ``/usercenter/api/`` and friends."""

from __future__ import annotations

from typing import ClassVar

from ..core import BearerAuthService, endpoint
from ..models import BbsResponse, UserFullInfo
from ..signers import SignDs

__all__ = ["UserService"]


class UserService(BearerAuthService):
    signer: ClassVar[SignDs] = SignDs()

    @endpoint.get("/usercenter/api/getUserFullInfo")
    async def get_user_full_info(self) -> BbsResponse[UserFullInfo]: ...
