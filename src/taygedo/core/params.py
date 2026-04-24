"""Annotated parameter markers — FastAPI-style explicit parameter classification.

Use as the second argument of ``typing.Annotated`` to override the endpoint
engine's default inference::

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
    alias: str | None = None


@dataclass(frozen=True, slots=True)
class Path(ParamMarker):
    pass


@dataclass(frozen=True, slots=True)
class Query(ParamMarker):
    pass


@dataclass(frozen=True, slots=True)
class Header(ParamMarker):
    pass


@dataclass(frozen=True, slots=True)
class Body(ParamMarker):
    """At most one Body per endpoint.

    ``form=True`` → ``application/x-www-form-urlencoded`` (dict/BaseModel
    fields are urlencoded; Signers see the dict). Default is JSON.
    """

    form: bool = False
