"""Point-shop / merchandise listing."""

from __future__ import annotations

from typing import Annotated

from taygedo.core import BearerAuthService, Query, endpoint
from taygedo.models import BbsResponse, GoodsPage


class _Shop(BearerAuthService):
    @endpoint.get("/apihub/api/shop/listGoods")
    async def list_goods(
        self,
        tab: Annotated[str, Query()] = "all",
        version: Annotated[int, Query()] = 0,
        count: Annotated[int, Query()] = 20,
    ) -> BbsResponse[GoodsPage]: ...
