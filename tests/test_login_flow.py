"""Login → token-exchange flow updates SessionState in place."""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import parse_qs

from taygedo.client import TaygedoClient
from taygedo.core import PreparedRequest, Response


def _ok(payload: dict[str, Any]) -> Response:
    return Response(
        status_code=200,
        headers={"content-type": "application/json"},
        content=json.dumps(payload).encode("utf-8"),
    )


class _MockTaygedo(TaygedoClient):
    """TaygedoClient with a stubbed transport that asserts on URLs."""

    def __init__(self, scripts: list[Response]) -> None:
        super().__init__()
        self.sent: list[PreparedRequest] = []
        self._scripts = scripts

    async def __aenter__(self) -> _MockTaygedo:  # type: ignore[override]
        return self

    async def __aexit__(self, *exc: object) -> None:
        return None

    async def send(  # type: ignore[override]
        self,
        prepared: PreparedRequest,
        *,
        service: object | None = None,
    ) -> Response:
        # Honour auth injection so authed endpoints get their token.
        if (
            service is not None
            and getattr(type(service), "auth_required", False)
            and self._auth_provider is not None
        ):
            prepared = self._auth_provider.apply(prepared)
        self.sent.append(prepared)
        return self._scripts.pop(0)


async def test_login_with_laohu_writes_session_state() -> None:
    from taygedo.models import SmsLoginResult

    sms = SmsLoginResult.model_validate(
        {
            "userId": 999,
            "username": "u",
            "token": "laohu-tok-xyz",
        },
    )
    client = _MockTaygedo(
        scripts=[
            _ok(
                {
                    "code": 0,
                    "ok": True,
                    "data": {
                        "accessToken": "bbs-access",
                        "refreshToken": "bbs-refresh",
                        "uid": 5555,
                    },
                },
            ),
        ],
    )

    result = await client.auth.login_with_laohu(sms)
    assert result.access_token == "bbs-access"
    assert result.refresh_token == "bbs-refresh"
    assert result.uid == 5555
    # SessionState mutated in place.
    assert client.session_state.access_token == "bbs-access"
    assert client.session_state.refresh_token == "bbs-refresh"
    assert client.session_state.uid == 5555
    assert client.session_state.laohu_token == "laohu-tok-xyz"
    assert client.session_state.laohu_user_id == 999
    # Outgoing exchange request: form-urlencoded, contains token + userIdentity.
    sent = client.sent[0]
    assert sent.method == "POST"
    assert sent.url == "/usercenter/api/login"
    assert sent.form is True
    body = parse_qs((sent.params and "&".join(f"{k}={v}" for k, v in sent.params.items())) or "")
    assert body.get("token") == ["laohu-tok-xyz"]
    assert body.get("userIdentity") == ["999"]
    assert body.get("appId") == ["10551"]


async def test_send_captcha_uses_user_laohu_base_url() -> None:
    from taygedo.models import CaptchaRequest

    client = _MockTaygedo(scripts=[_ok({"code": 0, "message": "OK"})])
    await client.login.send_captcha(
        body=CaptchaRequest(cellphone="13800138000"),
    )
    sent = client.sent[0]
    assert sent.method == "POST"
    assert sent.url == "/m/newApi/sendPhoneCaptchaWithOutLogin"
    assert sent.form is True
    # SignLaohu adds a `sign` field after sorting+md5.
    assert "sign" in sent.params
    assert "cellphone" in sent.params and sent.params["cellphone"] == "13800138000"
