"""Signing strategy V2 — placeholder.

Will compose a ``DeviceIdProvider`` and a ``crypto`` primitive once the real
algorithm is wired in.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..core.signing import PreparedRequest

__all__ = ["SignV2"]


@dataclass(slots=True)
class SignV2:
    """Placeholder for the V2 signature algorithm."""

    marker: str = "v2"

    def sign(self, req: PreparedRequest) -> PreparedRequest:
        out = req.copy()
        out.headers.setdefault("X-Sign-Version", self.marker)
        return out
