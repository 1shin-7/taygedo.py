"""LaohuSDK login endpoints — captcha + SMS login.

These three POSTs all hit ``user.laohu.com`` and require the LaohuSDK MD5
signature (computed by :class:`SignLaohu`). Two distinct signers are needed
because ``/openApi/sms/new/login`` AES-encrypts ``cellphone`` and ``captcha``
before the sign computation, while the captcha-send/verify endpoints leave
those fields plain.

The signers are constructed lazily per call from the host client's
:class:`DeviceProfile`, so a custom device (different ``versionCode``,
``deviceModel``, etc.) flows through naturally.
"""

from __future__ import annotations

from typing import Annotated, Any, ClassVar

from taygedo.core import Body, Service, endpoint
from taygedo.models import (
    CaptchaRequest,
    CheckCaptchaRequest,
    LaohuResponse,
    SmsLoginRequest,
    SmsLoginResult,
)
from taygedo.signers import LOGIN_SENSITIVE_FIELDS, LaohuConfig, SignLaohu

__all__ = ["LoginService"]


def _captcha_signer(svc: Any) -> SignLaohu:
    return SignLaohu(LaohuConfig(), svc.client.device)


def _login_signer(svc: Any) -> SignLaohu:
    return SignLaohu(
        LaohuConfig(
            sensitive_fields=LOGIN_SENSITIVE_FIELDS,
            timestamp_unit="ms",
        ),
        svc.client.device,
    )


class LoginService(Service):
    """Wraps the LaohuSDK pre-login surface."""

    base_url: ClassVar[str] = "https://user.laohu.com"
    auth_required: ClassVar[bool] = False

    @endpoint.post(
        "/m/newApi/sendPhoneCaptchaWithOutLogin",
        sign=_captcha_signer,
    )
    async def send_captcha(
        self, body: Annotated[CaptchaRequest, Body(form=True)],
    ) -> LaohuResponse[None]: ...

    @endpoint.post(
        "/m/newApi/checkPhoneCaptchaWithOutLogin",
        sign=_captcha_signer,
    )
    async def check_captcha(
        self, body: Annotated[CheckCaptchaRequest, Body(form=True)],
    ) -> LaohuResponse[None]: ...

    @endpoint.post(
        "/openApi/sms/new/login",
        sign=_login_signer,
    )
    async def sms_login(
        self, body: Annotated[SmsLoginRequest, Body(form=True)],
    ) -> LaohuResponse[SmsLoginResult]: ...
