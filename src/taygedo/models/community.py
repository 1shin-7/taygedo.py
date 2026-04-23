"""Community / game / column aggregates.

A ``Community`` *is* a forum-section dedicated to one game; the API uses both
``communityId`` and ``gameId`` interchangeably depending on the endpoint.
"""

from __future__ import annotations

from pydantic import Field

from ._base import BbsBase
from .common import Ann, Banner, Column, NavigatorEntry

__all__ = ["ColumnHome", "Community", "CommunityHome", "NotificationUnread", "UnreadCount"]


class Community(BbsBase):
    """A game-specific forum section, with its columns and visual assets."""

    id: int
    name: str
    game_id: int = Field(alias="gameId")
    state: int = 0
    icon: str = ""
    home_bg_img: str = Field(alias="homeBgImg", default="")
    card_bg_img: str = Field(alias="cardBgImg", default="")
    card_link: str | None = Field(alias="cardLink", default=None)
    create_time: int = Field(alias="createTime")
    columns: list[Column] = Field(default_factory=list)


class CommunityHome(BbsBase):
    """Response payload of ``/apihub/api/getCommunityHome``."""

    community: Community
    anns: list[Ann] = Field(default_factory=list)
    banners: list[Banner] = Field(default_factory=list)
    navigator: list[NavigatorEntry] = Field(default_factory=list)


class NotificationUnread(BbsBase):
    """``getUserUnreadCnt.notificationUnread`` — per-channel unread tallies."""

    id: int = 0
    uid: int = 0
    at: int = 0
    comment: int = 0
    like: int = 0
    follow: int = 0
    system: int = 0
    channel_unread: int = Field(alias="channelUnread", default=0)
    create_time: int = Field(alias="createTime", default=0)
    update_time: int = Field(alias="updateTime", default=0)


class UnreadCount(BbsBase):
    """``GET /apihub/api/getUserUnreadCnt`` payload."""

    notification_unread: NotificationUnread = Field(
        alias="notificationUnread", default_factory=NotificationUnread,
    )


class ColumnHome(BbsBase):
    """Response payload of ``/apihub/api/getColumnHome``.

    ``top_posts`` is intentionally typed as ``list[object]`` here to avoid a
    forward-import cycle into ``post.py``; consumers should re-validate it as
    ``list[Post]`` when they need typed posts.
    """

    column: Column
    anns: list[Ann] = Field(default_factory=list)
    top_posts: list[object] = Field(alias="topPosts", default_factory=list)
