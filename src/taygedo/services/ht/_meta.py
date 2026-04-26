"""Cross-cutting HT meta — game-scoped recommended-post feed."""

from __future__ import annotations

from typing import Annotated

from taygedo.core import BearerAuthService, Query, endpoint
from taygedo.models import BbsResponse, CursorPage, Post

HT_GAME_ID = 1256


class _Meta(BearerAuthService):
    @endpoint.get("/bbs/awapi/recommendPosts")
    async def _recommend_raw(
        self, game_id: Annotated[int, Query(alias="gameId")],
    ) -> BbsResponse[CursorPage[Post]]: ...

    async def recommend_posts(self) -> BbsResponse[CursorPage[Post]]:
        return await self._recommend_raw(game_id=HT_GAME_ID)
