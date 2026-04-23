"""BBS community endpoints (non-game)."""

from __future__ import annotations

from typing import ClassVar

from ..core import BearerAuthService, endpoint
from ..models import BbsResponse, UnreadCount
from ..signers import SignDs

__all__ = ["CommunityService"]


class CommunityService(BearerAuthService):
    signer: ClassVar[SignDs] = SignDs()

    @endpoint.get("/apihub/api/getUserUnreadCnt")
    async def get_user_unread_cnt(self) -> BbsResponse[UnreadCount]: ...
