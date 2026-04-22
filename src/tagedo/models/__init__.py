"""Public re-exports for ``tagedo.models``.

Models are organised by business domain (``community``, ``post``, ``user``,
``task``, ``game``, ``auth``, ``app``) and share two infrastructure modules:

* :mod:`tagedo.models._base` — pydantic ``ConfigDict`` bases.
* :mod:`tagedo.models.envelope` — generic response envelopes.
* :mod:`tagedo.models.pagination` — generic ``CursorPage`` / ``ReplyFeedPage``.
* :mod:`tagedo.models.common` — atomic value objects (``Image``, ``Vod``, ...).
"""

from ._base import BbsBase, LaohuBase
from .app import (
    AppConfig,
    AppConfigs,
    AppStartupData,
    Emoticon,
    EmoticonGroup,
    ImConfigEntry,
)
from .auth import (
    AreaCode,
    BbsLoginResult,
    GdtAdConfig,
    InitConfig,
    OneKeySmsLogin,
    SmsLoginResult,
    UserIdentify,
    WebViewUrls,
)
from .common import Ann, Banner, Column, Image, NavigatorEntry, Vod, VodItem
from .community import ColumnHome, Community, CommunityHome
from .envelope import BbsResponse, LaohuResponse
from .game import (
    BindRole,
    GameRecordCard,
    GameRolesData,
    HtMatrixInfo,
    HtNamedId,
    HtRoleGameRecord,
    HtWeaponInfo,
)
from .pagination import CursorPage, ReplyFeedPage
from .post import Post, PostCover, PostStat, PostType, Reply, SelfOperation
from .task import CoinTaskState, ExpLevel, ExpRecord, SignInResult, Task, UserTasks
from .user import (
    AuditState,
    ColumnAuth,
    CommunityAuth,
    PrivacySetting,
    User,
    UserFullInfo,
    UserStat,
)

__all__ = [
    "Ann",
    "AppConfig",
    "AppConfigs",
    "AppStartupData",
    "AreaCode",
    "AuditState",
    "Banner",
    "BbsBase",
    "BbsLoginResult",
    "BbsResponse",
    "BindRole",
    "CoinTaskState",
    "Column",
    "ColumnAuth",
    "ColumnHome",
    "Community",
    "CommunityAuth",
    "CommunityHome",
    "CursorPage",
    "Emoticon",
    "EmoticonGroup",
    "ExpLevel",
    "ExpRecord",
    "GameRecordCard",
    "GameRolesData",
    "GdtAdConfig",
    "HtMatrixInfo",
    "HtNamedId",
    "HtRoleGameRecord",
    "HtWeaponInfo",
    "ImConfigEntry",
    "Image",
    "InitConfig",
    "LaohuBase",
    "LaohuResponse",
    "NavigatorEntry",
    "OneKeySmsLogin",
    "Post",
    "PostCover",
    "PostStat",
    "PostType",
    "PrivacySetting",
    "Reply",
    "ReplyFeedPage",
    "SelfOperation",
    "SignInResult",
    "SmsLoginResult",
    "Task",
    "User",
    "UserFullInfo",
    "UserIdentify",
    "UserStat",
    "UserTasks",
    "Vod",
    "VodItem",
    "WebViewUrls",
]
