"""Cross-cutting NTE meta endpoints — team recommendations + game-scoped post feed."""

from __future__ import annotations

from typing import Annotated

from taygedo.core import BearerAuthService, Query, endpoint
from taygedo.models import BbsResponse, CursorPage, NteTeamRecommend, Post

NTE_GAME_ID = 1289


class _Meta(BearerAuthService):
    @endpoint.get("/apihub/awapi/yh/team")
    async def get_team_recommends(self) -> BbsResponse[list[NteTeamRecommend]]: ...

    @endpoint.get("/bbs/awapi/recommendPosts")
    async def _recommend_raw(
        self, game_id: Annotated[int, Query(alias="gameId")],
    ) -> BbsResponse[CursorPage[Post]]: ...

    async def recommend_posts(self) -> BbsResponse[CursorPage[Post]]:
        return await self._recommend_raw(game_id=NTE_GAME_ID)
