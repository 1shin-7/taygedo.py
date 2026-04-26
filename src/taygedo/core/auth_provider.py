"""Authorization injection — orthogonal to Signer.

Signers are *computational* (DS/MD5/AES) with inputs fixed at decoration
time. Authentication is *stateful* — tokens live on the Client and rotate on
login / refresh. Keeping them separate means services never touch tokens:
the Client owns an ``AuthProvider`` and applies it to every request of any
Service with ``auth_required = True``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from taygedo.core.signing import PreparedRequest

__all__ = ["AuthProvider", "BearerProvider"]


@runtime_checkable
class AuthProvider(Protocol):
    def apply(self, req: PreparedRequest) -> PreparedRequest: ...


@dataclass(slots=True)
class BearerProvider:
    """Reads ``access_token`` from the session holder at call time.

    Empty token → request goes out unauthenticated and the server's 401
    triggers the framework's refresh middleware (not an exception here).
    """

    session: object
    header_name: str = "Authorization"
    field_name: str = "access_token"

    def apply(self, req: PreparedRequest) -> PreparedRequest:
        token = getattr(self.session, self.field_name, "") or ""
        if not token:
            return req
        out = req.copy()
        out.headers.setdefault(self.header_name, token)
        return out
