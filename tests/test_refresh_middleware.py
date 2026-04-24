"""401 on a NTE call → AuthService.refresh → request retried with new token."""

from __future__ import annotations

from typing import Any

import orjson

from taygedo.client import TaygedoClient
from taygedo.core import PreparedRequest, Response


def _resp(status: int, payload: dict[str, Any]) -> Response:
    return Response(
        status_code=status,
        headers={"content-type": "application/json"},
        content=orjson.dumps(payload),
    )


class _ScriptedClient(TaygedoClient):
    def __init__(self, scripts: list[Response]) -> None:
        super().__init__()
        self.sent: list[PreparedRequest] = []
        self._scripts = scripts

    async def __aenter__(self) -> _ScriptedClient:  # type: ignore[override]
        return self

    async def __aexit__(self, *exc: object) -> None:
        return None

    async def send(  # type: ignore[override]
        self,
        prepared: PreparedRequest,
        *,
        service: object | None = None,
    ) -> Response:
        if (
            service is not None
            and getattr(type(service), "auth_required", False)
            and self._auth_provider is not None
        ):
            prepared = self._auth_provider.apply(prepared)
        self.sent.append(prepared)
        return self._scripts.pop(0)


async def test_nte_401_triggers_refresh_then_retry() -> None:
    role_home_payload = {
        "code": 0,
        "ok": True,
        "data": {
            "roleid": "1",
            "rolename": "n",
            "userid": "1",
        },
    }

    client = _ScriptedClient(
        scripts=[
            _resp(401, {"code": 401}),
            _resp(
                200,
                {
                    "code": 0,
                    "ok": True,
                    "data": {
                        "accessToken": "rotated",
                        "refreshToken": "new-refresh",
                        "uid": 1,
                    },
                },
            ),
            _resp(200, role_home_payload),
        ],
    )
    client.session_state.access_token = "stale"
    client.session_state.refresh_token = "valid-refresh"

    result = await client.nte.get_role_home()
    assert result.is_ok
    assert result.data is not None and result.data.roleid == "1"

    # Three transport calls: original 401, refresh, retried request.
    assert len(client.sent) == 3
    # 1st call carried the stale token
    assert client.sent[0].headers["Authorization"] == "stale"
    # 2nd call is the refresh hitting /usercenter/api/refreshToken
    assert client.sent[1].url == "/usercenter/api/refreshToken"
    # 3rd call (the retry) carried the rotated token
    assert client.sent[2].headers["Authorization"] == "rotated"
    # SessionState was mutated by AuthService.refresh
    assert client.session_state.access_token == "rotated"
    assert client.session_state.refresh_token == "new-refresh"


async def test_refresh_failure_does_not_retry() -> None:
    import pytest

    from taygedo.core import ApiError

    client = _ScriptedClient(
        scripts=[
            _resp(401, {"code": 401}),
            # refresh returns 4xx → AuthService.refresh swallows and returns False
            _resp(400, {"code": 1, "msg": "bad refresh token"}),
        ],
    )
    client.session_state.access_token = "stale"
    client.session_state.refresh_token = "doomed"

    with pytest.raises(ApiError) as exc:
        await client.nte.get_role_home()
    assert exc.value.status_code == 401
    assert len(client.sent) == 2
