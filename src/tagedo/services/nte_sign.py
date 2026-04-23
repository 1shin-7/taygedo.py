"""异环 monthly sign-in API.

Distinct from the BBS community daily sign-in (``/apihub/api/signin``): this
is the in-game monthly sign-in shown inside the NTE WebView.

The POST sign endpoint is form-urlencoded; we expose a typed wrapper
:meth:`sign_role` so callers don't have to construct the body themselves.
"""

from __future__ import annotations

from typing import Annotated, ClassVar

from pydantic import BaseModel, Field

from ..core import BearerAuthService, Body, Query, endpoint
from ..models import BbsResponse, NteSignReward, NteSignState
from ..signers import SignDs

__all__ = ["NteSignRequest", "NteSignService"]


class NteSignRequest(BaseModel):
    """``POST /apihub/awapi/sign`` form body."""

    role_id: int = Field(serialization_alias="roleId")
    game_id: int = Field(default=1289, serialization_alias="gameId")


class NteSignService(BearerAuthService):
    signer: ClassVar[SignDs] = SignDs()
    default_headers: ClassVar[dict[str, str]] = {
        "Origin": "https://webstatic.tajiduo.com",
        "Referer": "https://webstatic.tajiduo.com/",
        "X-Requested-With": "com.pwrd.htassistant",
    }

    @endpoint.get("/apihub/awapi/sign/rewards")
    async def get_rewards(
        self,
        game_id: Annotated[int, Query(alias="gameId")] = 1289,
        role_id: Annotated[int | None, Query(alias="roleId")] = None,
    ) -> BbsResponse[list[NteSignReward]]: ...

    @endpoint.get("/apihub/awapi/signin/state")
    async def get_state(
        self,
        game_id: Annotated[int, Query(alias="gameId")] = 1289,
    ) -> BbsResponse[NteSignState]: ...

    @endpoint.post("/apihub/awapi/sign")
    async def _sign_raw(
        self,
        body: Annotated[NteSignRequest, Body(form=True)],
    ) -> BbsResponse[None]: ...

    async def sign_role(self, role_id: int, game_id: int = 1289) -> BbsResponse[None]:
        """Submit today's sign-in for ``role_id``."""
        return await self._sign_raw(
            body=NteSignRequest(role_id=role_id, game_id=game_id),
        )
