"""Generic response envelopes for bbs-api and laohu APIs.

Both APIs wrap their actual payload in a uniform shell::

    bbs:    {"code": 0, "data": <payload>, "msg": "ok", "ok": true}
    laohu:  {"code": 0, "result": <payload>, "message": "..."}

By making the envelope generic in ``T`` we avoid declaring one envelope class
per endpoint::

    BbsResponse[Post]                # GET /posts/123
    BbsResponse[list[Community]]     # GET /apihub/api/getAllCommunity
    LaohuResponse[SmsLoginResult]    # POST /openApi/sms/new/login
"""

from __future__ import annotations

from ._base import BbsBase, LaohuBase

__all__ = ["BbsResponse", "LaohuResponse"]


class BbsResponse[T](BbsBase):
    """Standard ``bbs-api.tajiduo.com`` response envelope."""

    code: int
    data: T | None = None
    msg: str = ""
    ok: bool = True

    @property
    def is_ok(self) -> bool:
        return self.code == 0 and self.ok


class LaohuResponse[T](LaohuBase):
    """Standard ``user.laohu.com`` response envelope."""

    code: int
    message: str = ""
    result: T | None = None

    @property
    def is_ok(self) -> bool:
        return self.code == 0
