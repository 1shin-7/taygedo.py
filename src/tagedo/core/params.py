"""Annotated parameter markers — FastAPI-style explicit parameter classification.

These are used as the second argument of ``typing.Annotated`` to override the
endpoint engine's default parameter inference. Example::

    @endpoint("GET", "/api/posts")
    async def list_posts(
        self,
        page: Annotated[int, Query()] = 1,
        token: Annotated[str, Header("X-Token")] = "",
    ) -> list[Post]: ...
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["Body", "Header", "ParamMarker", "Path", "Query"]


@dataclass(frozen=True, slots=True)
class ParamMarker:
    """Base class — never used directly, only via subclasses."""

    alias: str | None = None


@dataclass(frozen=True, slots=True)
class Path(ParamMarker):
    """Mark a parameter as a URL path variable."""


@dataclass(frozen=True, slots=True)
class Query(ParamMarker):
    """Mark a parameter as a URL query string entry."""


@dataclass(frozen=True, slots=True)
class Header(ParamMarker):
    """Mark a parameter as an HTTP header. ``alias`` overrides the header name."""


@dataclass(frozen=True, slots=True)
class Body(ParamMarker):
    """Mark a parameter as the request body. At most one Body per endpoint.

    ``form=True`` sends the body as ``application/x-www-form-urlencoded``
    (the value should be a dict or BaseModel — its fields are urlencoded
    and the params dict is what Signers see). Default is JSON.
    """

    form: bool = False
