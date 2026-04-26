"""Tasks, sign-in, exp / coin records."""

from __future__ import annotations

from pydantic import Field

from taygedo.models._base import BbsBase

__all__ = [
    "CoinTaskState",
    "ExpLevel",
    "ExpRecord",
    "SignInResult",
    "Task",
    "UserTasks",
]


class Task(BbsBase):
    """Daily task entry under ``getUserTasks.task_list3``."""

    task_key: str = Field(alias="taskKey")
    title: str
    exp: int = 0
    coin: int = 0
    complete_times: int = Field(alias="completeTimes", default=0)
    target_times: int = Field(alias="targetTimes", default=1)
    limit_times: int = Field(alias="limitTimes", default=1)
    cont_times: int = Field(alias="contTimes", default=0)
    period: int = 0
    """Date stamp YYYYMMDD."""
    uid: int


class UserTasks(BbsBase):
    """``/apihub/api/getUserTasks`` payload."""

    task_list3: list[Task] = Field(default_factory=list)


class CoinTaskState(BbsBase):
    """``/apihub/api/getUserCoinTaskState`` payload."""

    today_get: int = Field(alias="todayGet", default=0)
    today_total: int = Field(alias="todayTotal", default=0)
    total: int = 0


class ExpLevel(BbsBase):
    """``/apihub/api/getUserExpLevel`` payload."""

    exp: int = 0
    level: int = 1
    level_exp: int = Field(alias="levelExp", default=0)
    next_level: int = Field(alias="nextLevel", default=2)
    next_level_exp: int = Field(alias="nextLevelExp", default=0)
    today_exp: int = Field(alias="todayExp", default=0)


class ExpRecord(BbsBase):
    """One entry in ``/usercenter/api/getUserExpRecords``."""

    id: int
    uid: int
    community_id: int = Field(alias="communityId")
    type: int
    """3 = sign-in (other types not yet sampled)."""
    title: str
    num: int
    source_id: str = Field(alias="sourceId", default="")
    create_time: int = Field(alias="createTime", default=0)
    update_time: int = Field(alias="updateTime", default=0)


class SignInResult(BbsBase):
    """``/apihub/api/signin`` payload."""

    exp: int = 0
    gold_coin: int = Field(alias="goldCoin", default=0)
