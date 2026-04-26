"""Request signing protocol and a no-op default implementation.

A Signer is a pure transformation over a PreparedRequest: it may add headers,
mutate the body, append query parameters, etc. Signers are intentionally
ignorant of the transport layer — they receive a framework-internal value
object, not a curl_cffi request.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from taygedo.core.types import JsonObject

__all__ = ["NullSigner", "PreparedRequest", "Signer", "resolve_signer"]


@dataclass(slots=True)
class PreparedRequest:
    """Transport-agnostic representation of an outgoing HTTP request.

    ``form`` indicates that ``params`` should be sent as a form-urlencoded
    request body (POST/PUT/PATCH) rather than a URL query string. Signers
    that operate on ``params`` still see the same dict regardless.
    """

    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    params: dict[str, str | int | float | bool] = field(default_factory=dict)
    json_body: JsonObject | list[JsonObject] | None = None
    data: bytes | str | None = None
    form: bool = False

    def copy(self) -> PreparedRequest:
        """Return a deep copy so signers can mutate freely without aliasing."""
        return deepcopy(self)


@runtime_checkable
class Signer(Protocol):
    """A signing strategy applied to outgoing requests."""

    def sign(self, req: PreparedRequest) -> PreparedRequest: ...


class NullSigner:
    """A signer that performs no transformation (default when none is set)."""

    def sign(self, req: PreparedRequest) -> PreparedRequest:
        return req


def resolve_signer(spec: Signer | type[Signer] | None) -> Signer:
    """Normalise the various 'signer' declarations into a Signer instance.

    Accepts an instance, a zero-argument class, or None (meaning NullSigner).
    """
    if spec is None:
        return NullSigner()
    if isinstance(spec, type):
        return spec()
    return spec
