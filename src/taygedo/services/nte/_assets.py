"""Collectibles + open-world progress: realestate / vehicles / area progress."""

from __future__ import annotations

from typing import Annotated

from taygedo.core import BearerAuthService, Query, endpoint
from taygedo.models import (
    BbsResponse,
    NteArea,
    NteRealestateData,
    NteVehicleData,
)


class _Assets(BearerAuthService):
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
