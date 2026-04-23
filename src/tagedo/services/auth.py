"""Token exchange + refresh — bridges LaohuSDK login to bbs-api access tokens.

Flow::

    LoginService.sms_login(...) -> SmsLoginResult (laohu token)
        ↓
    AuthService.login_with_laohu(sms_result)
        → POST /usercenter/api/login {token, userIdentity, appId=10551}
        → BbsLoginResult (access_token + refresh_token)
        → writes session_state in place

    AuthService.refresh()  ← invoked by the 401 middleware
        → POST /usercenter/api/refreshToken (Authorization: <refresh_token>)
        → rewrites session_state.access_token / refresh_token
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, ClassVar, cast

from ..core import ApiError, Body, Header, Service, SignError, endpoint
from ..models import BbsLoginResult, BbsResponse, ExchangeTokenRequest
from ..signers import SignDs

if TYPE_CHECKING:
    from ..client import TajiduoClient
    from ..models import SmsLoginResult

__all__ = ["AuthService"]


class AuthService(Service):
    """Exchange laohu tokens for bbs tokens, and refresh bbs tokens in place."""

    auth_required: ClassVar[bool] = False
    signer: ClassVar[SignDs] = SignDs()

    # The bbs-api server inspects ``platform`` + ``User-Agent`` to gate access
    # to ``/usercenter/api/*``. ``uid: 0`` + an empty ``authorization`` mirror
    # the captured app request — the real values are filled in by per-endpoint
    # Header params.
    default_headers: ClassVar[dict[str, str]] = {
        "platform": "android",
        "uid": "0",
        "authorization": "",
        "User-Agent": "okhttp/4.12.0",
        "Accept": "application/json, text/plain, */*",
    }

    @endpoint.post("/usercenter/api/login")
    async def _exchange_raw(
        self,
        body: Annotated[ExchangeTokenRequest, Body(form=True)],
        device_id: Annotated[str, Header(alias="deviceid")],
        app_version: Annotated[str, Header(alias="appversion")] = "1.2.2",
    ) -> BbsResponse[BbsLoginResult]: ...

    @endpoint.post("/usercenter/api/refreshToken")
    async def _refresh_raw(
        self,
        refresh_token: Annotated[str, Header(alias="authorization")],
        device_id: Annotated[str, Header(alias="deviceid")],
        app_version: Annotated[str, Header(alias="appversion")] = "1.2.2",
    ) -> BbsResponse[BbsLoginResult]: ...

    async def login_with_laohu(self, sms_result: SmsLoginResult) -> BbsLoginResult:
        """Exchange a fresh ``SmsLoginResult`` for a bbs access token.

        Writes ``laohu_token`` / ``laohu_user_id`` immediately so a subsequent
        refresh failure can still recover via re-login by the caller, and on
        success populates ``access_token`` / ``refresh_token`` / ``uid``.
        """
        client = cast("TajiduoClient", self.client)
        client.session_state.laohu_token = sms_result.token
        client.session_state.laohu_user_id = sms_result.user_id
        env = await self._exchange_raw(
            body=ExchangeTokenRequest.model_validate(
                {
                    "token": sms_result.token,
                    "userIdentity": str(sms_result.user_id),
                    "appId": "10551",
                },
            ),
            device_id=client.device.device_id,
        )
        if env.data is None:
            raise ApiError(
                env.code,
                env.msg or "exchange returned no data",
                message=f"token exchange failed (code={env.code}): {env.msg or 'no msg'}",
            )
        client.session_state.access_token = env.data.access_token
        client.session_state.refresh_token = env.data.refresh_token
        client.session_state.uid = env.data.uid
        return env.data

    async def refresh(self) -> bool:
        """Rotate the access_token using the stored refresh_token.

        Returns ``True`` on success (session_state is mutated in place);
        ``False`` if no refresh_token is held or the server rejects it.
        """
        client = cast("TajiduoClient", self.client)
        if not client.session_state.refresh_token:
            return False
        try:
            env = await self._refresh_raw(
                refresh_token=client.session_state.refresh_token,
                device_id=client.device.device_id,
            )
        except (ApiError, SignError):
            return False
        if env.data is None:
            return False
        client.session_state.access_token = env.data.access_token
        client.session_state.refresh_token = env.data.refresh_token
        return True

    async def on_unauthorized(self) -> bool:
        """Hook called by ``BearerAuthService`` siblings on HTTP 401."""
        return await self.refresh()
