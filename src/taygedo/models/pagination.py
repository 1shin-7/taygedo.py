"""Pagination helpers shared by ``/bbs/api/*`` list endpoints.

Two distinct shapes appear in the wild:

* **Cursor-style** — ``{hasMore, page, posts, users, version}``: ``getUserPostList``,
  ``getUserBrowseRecords``, ``getUserCollectPosts``, ``getRecommendPostList``,
  ``getOfficialPostList``.
* **Reply-feed-style** — ``{more, replys, version}``: ``getUserReplyFeeds``.

Both are made generic in ``T`` so the same shell hosts ``Post``, ``Reply``, etc.
"""

from __future__ import annotations

from pydantic import Field

from ._base import BbsBase
from .user import User

__all__ = ["CursorPage", "ReplyFeedPage"]


class CursorPage[T](BbsBase):
    """``{hasMore, page, posts, users, version}`` shape.

    The list field is named differently across endpoints (``posts`` is the most
    common). Use ``items`` (alias ``posts``) here so callers see a uniform name.
    """

    has_more: bool = Field(alias="hasMore", default=False)
    page: int = 0
    items: list[T] = Field(alias="posts", default_factory=list)
    users: list[User] = Field(default_factory=list)
    version: int = 0


class ReplyFeedPage[T](BbsBase):
    """``{more, replys, version}`` shape used by ``getUserReplyFeeds``."""

    more: bool = False
    items: list[T] = Field(alias="replys", default_factory=list)
    version: int = 0
