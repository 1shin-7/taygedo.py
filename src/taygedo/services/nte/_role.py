"""Character + role-home read endpoints."""

from __future__ import annotations

from typing import Annotated

from taygedo.core import BearerAuthService, Query, endpoint
from taygedo.models import BbsResponse, NteCharacter, NteRoleHome


class _Role(BearerAuthService):
    @endpoint.get("/apihub/awapi/yh/roleHome")
    async def get_role_home(self) -> BbsResponse[NteRoleHome]: ...

    @endpoint.get("/apihub/awapi/yh/characters")
    async def get_characters(
        self, role_id: Annotated[int, Query(alias="roleId")],
    ) -> BbsResponse[list[NteCharacter]]: ...
