"""Per-community exp records (``getUserExpRecords``)."""

from __future__ import annotations

from typing import Annotated

from taygedo.core import BearerAuthService, Query, endpoint
from taygedo.models import BbsResponse, ExpRecord


class _Exp(BearerAuthService):
    @endpoint.get("/usercenter/api/getUserExpRecords")
    async def get_exp_records(
        self, community_id: Annotated[int, Query(alias="communityId")] = 2,
    ) -> BbsResponse[list[ExpRecord]]: ...
