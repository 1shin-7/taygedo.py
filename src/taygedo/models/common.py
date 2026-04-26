"""Shared atomic value objects: media, links, banners, columns.

These are the smallest reusable shapes. Composite models in ``community.py``,
``post.py`` etc. import from here.
"""

from __future__ import annotations

from pydantic import Field

from taygedo.models._base import BbsBase

__all__ = [
    "Ann",
    "Banner",
    "Column",
    "Image",
    "NavigatorEntry",
    "Vod",
    "VodItem",
]


class Image(BbsBase):
    url: str
    width: int = 0
    height: int = 0


class VodItem(BbsBase):
    """A single playable transcoding of a video."""

    url: str
    size: int = 0
    width: int = 0
    height: int = 0


class Vod(BbsBase):
    """Video on demand: cover + transcodings."""

    url: str
    cover: str = ""
    duration: int = 0
    items: list[VodItem] = Field(default_factory=list)


class Ann(BbsBase):
    """Announcement card shown above a community / column home."""

    title: str
    url: str
    app_path: str = Field(alias="appPath", default="")
    web_path: str = Field(alias="webPath", default="")


class Banner(BbsBase):
    """Banner carousel entry."""

    url: str
    app_path: str = Field(alias="appPath", default="")
    web_path: str = Field(alias="webPath", default="")


class Column(BbsBase):
    """A sub-section ("column") of a community."""

    id: int
    community_id: int = Field(alias="communityId")
    game_id: int = Field(alias="gameId")
    column_name: str = Field(alias="columnName")
    column_icon: str = Field(alias="columnIcon", default="")
    show_type: int = Field(alias="showType")
    """1=normal, 2=guide, 3=announcement, 4=fan/selection."""
    create_time: int = Field(alias="createTime")


class NavigatorEntry(BbsBase):
    """One tile in a community's "navigator" (tools strip)."""

    name: str
    icon: str
    community_id: int = Field(alias="communityId")
    sort: int
    app_path: str = Field(alias="appPath", default="")
    web_path: str = Field(alias="webPath", default="")
    redpoint_time: int = Field(alias="redpointTime", default=0)
