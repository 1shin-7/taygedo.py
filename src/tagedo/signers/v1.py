"""Signing strategy V1 — placeholder.

Real algorithm is filled in once the wire protocol is reverse-engineered. The
class still implements the ``Signer`` protocol so the rest of the framework
can compose against it today.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..core.signing import PreparedRequest

__all__ = ["SignV1"]


@dataclass(slots=True)
class SignV1:
    """Placeholder for the V1 signature algorithm."""

    marker: str = "v1"

    def sign(self, req: PreparedRequest) -> PreparedRequest:
        out = req.copy()
        out.headers.setdefault("X-Sign-Version", self.marker)
        return out
