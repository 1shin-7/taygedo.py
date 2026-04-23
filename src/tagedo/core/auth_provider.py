"""Authorization injection — orthogonal to Signer.

A ``Signer`` performs *computational* request mutation (DS, MD5, AES) with
fixed inputs declared at decoration time. Authentication, by contrast, is
*stateful*: its inputs (access tokens) live on the Client and change at
runtime when the user logs in or refreshes a session.

Mixing the two would force every service to know about token plumbing. This
module separates them: an :class:`AuthProvider` is owned by the Client and
applied automatically to outgoing requests for any Service that opts in via
``auth_required = True``.

Built-in implementations:

* :class:`BearerProvider` — reads ``access_token`` from a ``SessionState``
  on every call (so a refresh transparently propagates).

A future ``CookieProvider`` / ``OAuth2Provider`` would slot in here without
touching Service or endpoint code.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from .signing import PreparedRequest

__all__ = ["AuthProvider", "BearerProvider"]


@runtime_checkable
class AuthProvider(Protocol):
    """Strategy that injects authentication into a prepared request."""

    def apply(self, req: PreparedRequest) -> PreparedRequest: ...


@dataclass(slots=True)
class BearerProvider:
    """Reads ``access_token`` from a session holder at call time.

    The session holder is any object exposing a string attribute (default
    ``access_token``); typically :class:`tagedo.client.SessionState`. We
    intentionally do **not** raise when the token is empty — instead the
    request goes out unauthenticated and the server's 401 triggers the
    framework's refresh middleware.
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
