"""Generic bound-role lookup — used to resolve a player's role for any game."""

from __future__ import annotations

from typing import Annotated, ClassVar

from taygedo.core import BearerAuthService, Query, endpoint
from taygedo.models import BbsResponse, BindRole
from taygedo.signers import SignDs


class BindRoleService(BearerAuthService):
    """``GET /apihub/api/getGameBindRole`` — same shape across NTE/HT/etc."""

    signer: ClassVar[SignDs] = SignDs()

    @endpoint.get("/apihub/api/getGameBindRole")
    async def get_game_bind_role(
        self,
        uid: Annotated[int, Query()],
        game_id: Annotated[int, Query(alias="gameId")],
    ) -> BbsResponse[BindRole]: ...
