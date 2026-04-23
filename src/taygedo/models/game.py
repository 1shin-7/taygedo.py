"""Game / role / record models.

Two flavours coexist:

* "Lite" role info (returned in user / game-record-card endpoints): :class:`BindRole`.
* "Heavy" full-role record from the WebView ``awapi``: :class:`HtRoleGameRecord`
  (Huan Ta-specific). Field names mirror the wire format because they are
  passed through verbatim from the game backend.
"""

from __future__ import annotations

from pydantic import Field, field_validator

from ._base import BbsBase

__all__ = [
    "BindRole",
    "GameRecordCard",
    "GameRolesData",
    "HtMatrixInfo",
    "HtNamedId",
    "HtRoleGameRecord",
    "HtWeaponInfo",
]


class BindRole(BbsBase):
    """A user's bound game role — minimal version embedded in many responses."""

    game_id: int = Field(alias="gameId")
    role_id: int = Field(alias="roleId")
    role_name: str = Field(alias="roleName")
    account: str = ""
    lev: int = 0
    gender: int = -1
    server_id: int = Field(alias="serverId", default=0)
    server_name: str = Field(alias="serverName", default="")


class GameRecordCard(BbsBase):
    """Card shown on the home screen aggregating bound role + game branding."""

    game_id: int = Field(alias="gameId")
    game_name: str = Field(alias="gameName")
    game_icon: str = Field(alias="gameIcon", default="")
    background_image: str = Field(alias="backgroundImage", default="")
    link: str = ""
    bind_role_info: BindRole = Field(alias="bindRoleInfo")


class GameRolesData(BbsBase):
    """``/usercenter/api/v2/getGameRoles`` payload — list of bound roles for a game."""

    bind_role: int = Field(alias="bindRole", default=0)
    roles: list[BindRole] = Field(default_factory=list)


# --- Huan Ta WebView /apihub/awapi/ht/getRoleGameRecord ---------------------
# These keep the wire field names (mostly lowercase / mixed) for fidelity.


class HtNamedId(BbsBase):
    """Generic ``{name, ID}`` pair used by imitations / dress fashions / mounts.

    The wire ``name`` field is mostly a string but the upstream service
    occasionally sends an integer for mounts (e.g. ``2613``); we coerce.
    """

    name: str
    id: str = Field(alias="ID")

    @field_validator("name", mode="before")
    @classmethod
    def _coerce_name(cls, v: object) -> object:
        return str(v) if isinstance(v, (int, float)) else v


class HtMatrixInfo(BbsBase):
    id: int = Field(alias="ID")
    id_str: str = Field(alias="IDStr")
    star: int = Field(alias="Star")
    color: int = Field(alias="Color")
    pos: int = Field(alias="Pos")
    lev: int = Field(alias="Lev")


class HtWeaponInfo(BbsBase):
    id: int = Field(alias="ID")
    id_str: str = Field(alias="IDStr")
    name: str
    star: int = Field(alias="Star")
    color: int = Field(alias="Color")
    lev: int = Field(alias="Lev")
    matrix_info_list: list[HtMatrixInfo] = Field(
        alias="MatrixInfoList", default_factory=list,
    )


class HtRoleGameRecord(BbsBase):
    """Huan Ta full-role record. Field names mirror the wire format verbatim."""

    roleid: str
    rolename: str
    userid: str
    groupname: str = ""
    createrole_time: str = ""
    par_dt: str = ""
    online_version: int = 0

    lev: int = 0
    shengelev: str = ""
    maxgs: int = 0

    imitation_count: int = Field(alias="imitationCount", default=0)
    achievementpointall: str = ""
    endlessidolumtotalscore: str = ""
    bigsecretround: str = ""
    artifactcount: int = 0
    equipslottypelevel: str = ""
    sololeaguestageinfo: str = ""
    """JSON string ``{"Stage", "Grade", "Stars", "ProtectScore"}`` — decode lazily."""

    imitationlist: list[HtNamedId] = Field(default_factory=list)
    dressfashionlist: list[HtNamedId] = Field(default_factory=list)
    mountlist: list[HtNamedId] = Field(default_factory=list)
    weaponinfo: list[HtWeaponInfo] = Field(default_factory=list)
