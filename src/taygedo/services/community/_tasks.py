"""Daily task / exp / coin progress."""

from __future__ import annotations

from typing import Annotated

from taygedo.core import BearerAuthService, Query, endpoint
from taygedo.models import BbsResponse, CoinTaskState, ExpLevel, UserTasks


class _Tasks(BearerAuthService):
    @endpoint.get("/apihub/api/getUserTasks")
    async def get_user_tasks(
        self,
        community_id: Annotated[int, Query(alias="communityId")],
        gid: Annotated[int, Query()] = 2,
    ) -> BbsResponse[UserTasks]: ...

    @endpoint.get("/apihub/api/getUserCoinTaskState")
    async def get_coin_task_state(self) -> BbsResponse[CoinTaskState]: ...

    @endpoint.get("/apihub/api/getUserExpLevel")
    async def get_exp_level(
        self, community_id: Annotated[int, Query(alias="communityId")],
    ) -> BbsResponse[ExpLevel]: ...
