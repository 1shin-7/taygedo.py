"""User identity, statistics, audit state, permissions and full profile."""

from __future__ import annotations

from pydantic import Field

from taygedo.models._base import BbsBase

__all__ = [
    "AuditState",
    "ColumnAuth",
    "CommunityAuth",
    "FollowEntry",
    "FollowsPage",
    "PrivacySetting",
    "PublishElementPerm",
    "SysAvatar",
    "User",
    "UserFullInfo",
    "UserStat",
]


class User(BbsBase):
    """Public user identity (the field used inside posts, lists, profile, ...)."""

    uid: int
    nickname: str = ""
    account: str = ""
    avatar: str = ""
    gender: int = -1
    """-1 = unknown, 0 = female, 1 = male."""
    ip_region: str = Field(alias="ipRegion", default="")
    is_realname: bool = Field(alias="isRealname", default=False)
    official_master: bool = Field(alias="officialMaster", default=False)
    user_master: bool = Field(alias="userMaster", default=False)
    device_id: str = Field(alias="deviceId", default="")
    forbid_end_time: int = Field(alias="forbidEndTime", default=0)
    silent_end_time: int = Field(alias="silentEndTime", default=0)
    create_time: int = Field(alias="createTime", default=0)
    update_time: int = Field(alias="updateTime", default=0)
    certification: dict[str, object] = Field(default_factory=dict)


class UserStat(BbsBase):
    uid: int
    fans_cnt: int = Field(alias="fansCnt", default=0)
    follow_cnt: int = Field(alias="followCnt", default=0)
    post_num: int = Field(alias="postNum", default=0)
    beliked_num: int = Field(alias="belikedNum", default=0)
    create_time: int = Field(alias="createTime", default=0)
    update_time: int = Field(alias="updateTime", default=0)


class AuditState(BbsBase):
    """Per-field moderation status returned by ``getUserFullInfo``."""

    nickname_in_audit: bool = Field(alias="nicknameInAudit", default=False)
    nickname_state: int = Field(alias="nicknameState", default=0)
    avatar_in_audit: bool = Field(alias="avatarInAudit", default=False)
    avatar_state: int = Field(alias="avatarState", default=0)
    introduce_in_audit: bool = Field(alias="introduceInAudit", default=False)
    introduce_state: int = Field(alias="introduceState", default=0)


class ColumnAuth(BbsBase):
    column_id: int = Field(alias="columnId")
    supper: bool = False


class CommunityAuth(BbsBase):
    community_id: int = Field(alias="communityId")
    supper: bool = False
    column_auths: list[ColumnAuth] = Field(alias="columnAuths", default_factory=list)


class PrivacySetting(BbsBase):
    uid: int
    privacy_collect: bool = Field(alias="privacyCollect", default=True)
    privacy_post: bool = Field(alias="privacyPost", default=True)
    privacy_reply: bool = Field(alias="privacyReply", default=True)
    privacy_user_center: bool = Field(alias="privacyUserCenter", default=True)
    create_time: int = Field(alias="createTime", default=0)
    update_time: int = Field(alias="updateTime", default=0)


class UserFullInfo(BbsBase):
    """Response payload of ``/usercenter/api/getUserFullInfo``."""

    user: User
    user_stat: UserStat = Field(alias="userStat")
    audit: AuditState
    auths: list[CommunityAuth] = Field(default_factory=list)
    privacy_setting: PrivacySetting = Field(alias="privacySetting")
    certification: dict[str, object] = Field(default_factory=dict)
    in_black_list: bool = Field(alias="inBlackList", default=False)


# ---------- system-provided avatar pool ------------------------------------


class SysAvatar(BbsBase):
    """One row in ``GET /apihub/api/assets/getUserSysAvatars`` — official avatar."""

    id: int
    name: str = ""
    icon: str = ""


# ---------- follow listings ------------------------------------------------


class FollowEntry(BbsBase):
    """``queryFollows.follows[*]`` — a User plus the relation flags."""

    user: User
    fr: dict[str, bool] = Field(default_factory=dict)


class FollowsPage(BbsBase):
    """``GET /usercenter/api/queryFollows`` payload (cursor-paginated)."""

    follows: list[FollowEntry] = Field(default_factory=list)
    last_id: int = Field(alias="lastId", default=0)
    more: bool = False


# ---------- post-publishing permission check -------------------------------


class PublishElementPerm(BbsBase):
    """``GET /bbs/api/publishElementPerm`` — can the current user insert X?"""

    can_publish: bool = Field(alias="canPublish", default=False)
    prompt: str = ""
