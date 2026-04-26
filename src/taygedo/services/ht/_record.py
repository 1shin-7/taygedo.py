"""TOF role-record query (``ht/getRoleGameRecord``)."""

from __future__ import annotations

from typing import Annotated

from taygedo.core import BearerAuthService, Query, endpoint
from taygedo.models import BbsResponse, HtRoleGameRecord


class _Record(BearerAuthService):
    @endpoint.get("/apihub/awapi/ht/getRoleGameRecord")
    async def get_role_game_record(
        self,
        role_id: Annotated[int, Query(alias="roleId")],
        game_id: Annotated[int, Query(alias="gameId")] = 1256,
        type_: Annotated[int, Query(alias="type")] = 0,
    ) -> BbsResponse[HtRoleGameRecord]: ...
