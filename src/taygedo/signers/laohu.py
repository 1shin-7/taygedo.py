"""Laohu (user.laohu.com) request signing — MD5 over sorted values + AES-ECB.

Algorithm reverse-engineered from the LaohuSDK 4.273.0 dex (see
``com.laohu.sdk.e.c::a(Map, boolean)``, ``com.laohu.sdk.e.k::a``,
``com.laohu.sdk.util.e::a``, ``com.laohu.sdk.util.r::a``):

1. Sensitive fields (``cellphone``, ``captcha``, ``username``, ``password``,
   ``unlockCode``) are AES-ECB-PKCS5 encrypted with a key derived from the
   last 16 bytes of the host-app key, then base64-encoded (NO_WRAP).
2. The full param map (encrypted-where-applicable, plus device base + ``t``)
   is reduced to ``"".join(value for key, value in sorted(params.items()))``.
3. The host-app key is appended and the result MD5-hashed; the hex digest
   is written back as ``params["sign"]``.

The default ``LaohuConfig`` carries the htassistant-specific app_key extracted
from ``com.pwrd.htassistant.MainActivity:35``::

    LaohuPlatform.getInstance().initAppInfo(
        mainActivity, 10550, "89155cc4e8634ec5b1b6364013b23e3e", ...);

This key is host-app-public (any reverse engineer obtains it); host apps using
a different LaohuSDK registration override it via the constructor.
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
"""Empty by default — sensitive fields are decided per-endpoint, not per-app.

Reverse-engineered from ``com.laohu.sdk.e.c`` vs ``com.laohu.sdk.e.k``:

* ``sendPhoneCaptchaWithOutLogin`` / ``checkPhoneCaptchaWithOutLogin`` send
  ``cellphone`` in plain text and feed plain text into the sign computation.
* ``/openApi/sms/new/login`` AES-encrypts both ``cellphone`` and ``captcha``,
  and the ENCRYPTED ciphertexts are what enters the sign.

So the encryption decision is endpoint-level. Construct ``SignLaohu`` instances
with the appropriate ``sensitive_fields`` per endpoint group::

    SignLaohu(LaohuConfig(sensitive_fields=frozenset({"cellphone","captcha"})), ...)
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
