"""异环 (NTE, gameId=1289) game-data queries.

All endpoints under ``/apihub/awapi/yh/`` are server-side authenticated by a
single ``Authorization`` Bearer header — there is no DS or per-request sign,
and ``roleId`` is freely queryable (the upstream service does not bind the
caller's uid to the requested roleId). This service therefore inherits
:class:`BearerAuthService` and lets the Client's ``AuthProvider`` inject the
token automatically.

The static identity headers (``Origin``, ``Referer``, ``X-Requested-With``)
mirror what the in-app WebView sends; the server does not strictly validate
them but the cost of carrying them is zero and it shields us against any
future tightening.
"""

from __future__ import annotations

from typing import Annotated, ClassVar

from ..core import BearerAuthService, Query, endpoint
from ..models import (
    BbsResponse,
    NteArea,
    NteCharacter,
    NteRealestateData,
    NteRoleHome,
    NteTeamRecommend,
    NteVehicleData,
)
from ..signers import SignDs

__all__ = ["NteService"]


class NteService(BearerAuthService):
    """Read-only queries against the NTE WebView API."""

    signer: ClassVar[SignDs] = SignDs()

    default_headers: ClassVar[dict[str, str]] = {
        "Origin": "https://webstatic.tajiduo.com",
        "Referer": "https://webstatic.tajiduo.com/",
        "X-Requested-With": "com.pwrd.htassistant",
    }

    @endpoint.get("/apihub/awapi/yh/roleHome")
    async def get_role_home(self) -> BbsResponse[NteRoleHome]: ...

    @endpoint.get("/apihub/awapi/yh/characters")
    async def get_characters(
        self, role_id: Annotated[int, Query(alias="roleId")],
    ) -> BbsResponse[list[NteCharacter]]: ...

    @endpoint.get("/apihub/awapi/yh/realestate")
    async def get_realestate(
        self, role_id: Annotated[int, Query(alias="roleId")],
    ) -> BbsResponse[NteRealestateData]: ...

    @endpoint.get("/apihub/awapi/yh/vehicles")
    async def get_vehicles(
        self, role_id: Annotated[int, Query(alias="roleId")],
    ) -> BbsResponse[NteVehicleData]: ...

    @endpoint.get("/apihub/awapi/yh/areaProgress")
    async def get_area_progress(
        self, role_id: Annotated[int, Query(alias="roleId")],
    ) -> BbsResponse[list[NteArea]]: ...

    @endpoint.get("/apihub/awapi/yh/team")
    async def get_team_recommends(self) -> BbsResponse[list[NteTeamRecommend]]: ...
