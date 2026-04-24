"""Pagination helpers shared by ``/bbs/api/*`` list endpoints.

Two distinct shapes appear in the wild:

* ``{hasMore, page, posts, users, version}``
* ``{more, replys, version}`` — used by ``getUserReplyFeeds``
"""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import Field

from ._base import BbsBase
from .user import User

__all__ = ["CursorPage", "ReplyFeedPage"]

T = TypeVar("T")


class CursorPage(BbsBase, Generic[T]):
    has_more: bool = Field(alias="hasMore", default=False)
    page: int = 0
    items: list[T] = Field(alias="posts", default_factory=list)
    users: list[User] = Field(default_factory=list)
    version: int = 0


class ReplyFeedPage(BbsBase, Generic[T]):
    """``{more, replys, version}`` shape used by ``getUserReplyFeeds``."""

    more: bool = False
    items: list[T] = Field(alias="replys", default_factory=list)
    version: int = 0
