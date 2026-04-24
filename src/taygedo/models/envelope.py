"""Generic response envelopes for bbs-api and laohu APIs.

Both APIs wrap their actual payload in a uniform shell::

    bbs:    {"code": 0, "data": <payload>, "msg": "ok", "ok": true}
    laohu:  {"code": 0, "result": <payload>, "message": "..."}
"""

from __future__ import annotations

from typing import Generic, TypeVar

from ._base import BbsBase, LaohuBase

__all__ = ["BbsResponse", "LaohuResponse"]

T = TypeVar("T")


class BbsResponse(BbsBase, Generic[T]):
    """Standard ``bbs-api.tajiduo.com`` response envelope."""

    code: int
    data: T | None = None
    msg: str = ""
    ok: bool = True

    @property
    def is_ok(self) -> bool:
        return self.code == 0 and self.ok


class LaohuResponse(LaohuBase, Generic[T]):
    """Standard ``user.laohu.com`` response envelope."""

    code: int
    message: str = ""
    result: T | None = None

    @property
    def is_ok(self) -> bool:
        return self.code == 0
