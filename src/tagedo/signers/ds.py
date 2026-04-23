"""DS header signer for ``bbs-api.tajiduo.com`` (App ≥ 1.2.2).

Algorithm reverse-engineered from the Hermes JS bundle (verified 26/26
against captured HAR samples)::

    ts = floor(now() / 1000)            # unix seconds
    r  = 8 random alphanumeric chars    # [A-Za-z0-9]{8}
    plaintext = str(ts) + r + appVersion + salt
    sign = md5(plaintext).hex()
    ds = f"{ts},{r},{sign}"

The salt and appVersion are wired into the host app at build time; for
``com.pwrd.htassistant`` 1.2.2 they are :data:`HTASSISTANT_DS_SALT`
and ``"1.2.2"``.

This Signer only sets the ``ds`` header and does NOT touch ``Authorization``
— that's :class:`tagedo.core.BearerProvider`'s job. They compose naturally:
the AuthProvider runs after the Signer in :meth:`BaseClient.send`.
"""

from __future__ import annotations

import hashlib
import secrets
import string
import time
from dataclasses import dataclass

from ..core.signing import PreparedRequest

__all__ = ["HTASSISTANT_DS_SALT", "DsConfig", "SignDs"]


HTASSISTANT_DS_SALT = "pUds3dfMkl"
"""DS salt extracted from the htassistant 1.2.2 Hermes bundle."""

_R_ALPHABET = string.ascii_letters + string.digits


@dataclass(slots=True, frozen=True)
class DsConfig:
    """Static parameters required to compute a DS header."""

    salt: str = HTASSISTANT_DS_SALT
    app_version: str = "1.2.2"


@dataclass(slots=True)
class SignDs:
    """Computes ``md5(ts + r + appVersion + salt)`` and writes the ``ds`` header."""

    config: DsConfig = DsConfig()

    def sign(self, req: PreparedRequest) -> PreparedRequest:
        ts = str(int(time.time()))
        r = "".join(secrets.choice(_R_ALPHABET) for _ in range(8))
        plaintext = ts + r + self.config.app_version + self.config.salt
        digest = hashlib.md5(plaintext.encode("utf-8")).hexdigest()
        out = req.copy()
        out.headers["ds"] = f"{ts},{r},{digest}"
        return out
