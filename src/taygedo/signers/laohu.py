"""Laohu (user.laohu.com) request signing — MD5 over sorted values + AES-ECB.

Algorithm (reverse-engineered from LaohuSDK 4.273.0 dex,
``com.laohu.sdk.{e.c,e.k,util.e,util.r}``):

1. AES-ECB-PKCS5 encrypt sensitive fields (cellphone/captcha/username/
   password/unlockCode) with key = ``app_key[-16:]``, base64 NO_WRAP.
2. ``"".join(v for k, v in sorted(params.items()))`` over the (encrypted)
   param map plus device base + ``t``.
3. Append ``app_key``, MD5; hex digest → ``params["sign"]``.

Default ``app_key`` ``89155cc4e8634ec5b1b6364013b23e3e`` is the htassistant
LaohuSDK registration extracted from ``com.pwrd.htassistant.MainActivity:35``.
Other host apps override via constructor; the key is host-app-public.
"""

from __future__ import annotations

import hashlib
import time
from base64 import b64encode
from dataclasses import dataclass, field
from typing import Literal

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7

from ..core.exceptions import SignError
from ..core.signing import PreparedRequest
from ..device import DeviceProfile

__all__ = ["LaohuConfig", "SignLaohu"]


HTASSISTANT_APP_KEY = "89155cc4e8634ec5b1b6364013b23e3e"
"""Default app_key for the com.pwrd.htassistant Android client."""

DEFAULT_SENSITIVE_FIELDS: frozenset[str] = frozenset()
"""Empty default — sensitive fields are decided per-endpoint, not per-app.

``send|checkPhoneCaptchaWithOutLogin`` send cellphone in plain text and feed
plain text into the sign; ``/openApi/sms/new/login`` AES-encrypts cellphone
+ captcha and feeds the ciphertexts. Pick the right set per endpoint.
"""

LOGIN_SENSITIVE_FIELDS = frozenset({"cellphone", "captcha", "username", "password", "unlockCode"})
"""Field set used by the ``/openApi/sms/...login`` endpoints."""


@dataclass(slots=True, frozen=True)
class LaohuConfig:
    """Static signing parameters for one host-app + device combination."""

    app_key: str = HTASSISTANT_APP_KEY
    sensitive_fields: frozenset[str] = DEFAULT_SENSITIVE_FIELDS
    timestamp_unit: Literal["s", "ms"] = "s"


@dataclass(slots=True)
class SignLaohu:
    """A ``Signer`` implementing LaohuSDK's MD5-over-sorted-values scheme.

    The instance owns the AES key derived from ``config.app_key`` so that
    encryption is a single ``Cipher.encryptor()`` call per request.
    """

    config: LaohuConfig
    device: DeviceProfile
    _aes_key: bytes = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if len(self.config.app_key) < 16:
            raise SignError("app_key must be at least 16 characters")
        object.__setattr__(self, "_aes_key", self.config.app_key[-16:].encode("ascii"))

    def sign(self, req: PreparedRequest) -> PreparedRequest:
        out = req.copy()
        params = {k: str(v) for k, v in out.params.items()}
        for field_name in self.config.sensitive_fields & params.keys():
            params[field_name] = self._encrypt(params[field_name])
        params.update(self.device.base_params())
        params.setdefault("t", self._timestamp())
        params["sign"] = self._compute_sign(params)
        out.params = dict(params.items())
        return out

    def _timestamp(self) -> str:
        now = time.time()
        return str(int(now * 1000)) if self.config.timestamp_unit == "ms" else str(int(now))

    def _encrypt(self, plaintext: str) -> str:
        padder = PKCS7(128).padder()
        block = padder.update(plaintext.encode("utf-8")) + padder.finalize()
        encryptor = Cipher(algorithms.AES(self._aes_key), modes.ECB()).encryptor()
        ciphertext = encryptor.update(block) + encryptor.finalize()
        return b64encode(ciphertext).decode("ascii")

    def _compute_sign(self, params: dict[str, str]) -> str:
        joined = "".join(value for _, value in sorted(params.items()))
        return hashlib.md5((joined + self.config.app_key).encode("utf-8")).hexdigest()
