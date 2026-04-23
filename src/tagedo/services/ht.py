"""Tower of Fantasy (HT, gameId=1256) game-record + bound-role lookup.

Two services live here because the bound-role endpoint is generic across
games (the same ``getGameBindRole`` shape is used to resolve the player's
role for NTE, TOF, and any future title), while the actual record query
is HT-specific.

Usage::

    bind = (await client.bind_role.get_game_bind_role(uid=user_uid, game_id=1256)).data
    record = (await client.ht.get_role_game_record(role_id=bind.role_id)).data
"""

from __future__ import annotations

from typing import Annotated, ClassVar

from ..core import BearerAuthService, Query, endpoint
from ..models import BbsResponse, BindRole, HtRoleGameRecord
from ..signers import SignDs

__all__ = ["BindRoleService", "HtService"]


class BindRoleService(BearerAuthService):
    """Cross-game bound-role lookup."""

    signer: ClassVar[SignDs] = SignDs()

    @endpoint.get("/apihub/api/getGameBindRole")
    async def get_game_bind_role(
        self,
        uid: Annotated[int, Query()],
        game_id: Annotated[int, Query(alias="gameId")],
    ) -> BbsResponse[BindRole]: ...


class HtService(BearerAuthService):
    """Tower of Fantasy game-record query (gameId=1256)."""

    signer: ClassVar[SignDs] = SignDs()

    default_headers: ClassVar[dict[str, str]] = {
        "Origin": "https://webstatic.tajiduo.com",
        "Referer": "https://webstatic.tajiduo.com/",
        "X-Requested-With": "com.pwrd.htassistant",
    }

    @endpoint.get("/apihub/awapi/ht/getRoleGameRecord")
    async def get_role_game_record(
        self,
        role_id: Annotated[int, Query(alias="roleId")],
        game_id: Annotated[int, Query(alias="gameId")] = 1256,
        type_: Annotated[int, Query(alias="type")] = 0,
    ) -> BbsResponse[HtRoleGameRecord]: ...
