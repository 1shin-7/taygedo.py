"""Search payloads — ``/bbs/api/search*`` and ``/usercenter/api/searchUser``."""

from __future__ import annotations

from pydantic import Field

from taygedo.models._base import BbsBase
from taygedo.models.user import User

__all__ = [
    "HotWord",
    "SearchTopicResult",
    "SearchUsersPage",
    "Topic",
]


class Topic(BbsBase):
    """One row in ``/bbs/api/searchTopic.list``."""

    id: int
    topic: str
    cover: str = ""
    icon: str = ""
    introduce: str = ""
    read_num: int = Field(alias="readNum", default=0)
    related_num: int = Field(alias="relatedNum", default=0)
    recommend_time: int = Field(alias="recommendTime", default=0)
    state: int = 0
    type: int = 0
    create_time: int = Field(alias="createTime", default=0)
    update_time: int = Field(alias="updateTime", default=0)


class SearchTopicResult(BbsBase):
    """``GET /bbs/api/searchTopic`` payload."""

    items: list[Topic] = Field(alias="list", default_factory=list)
    more: bool = False
    page: int = 0


class SearchUsersPage(BbsBase):
    """``GET /usercenter/api/searchUser`` payload — User list with pagination."""

    items: list[User] = Field(alias="list", default_factory=list)
    more: bool = False
    page: int = 0


class HotWord(BbsBase):
    """One entry in ``/bbs/api/searchHotWords``."""

    keyword: str
    count: int = 0
