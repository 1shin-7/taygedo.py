"""NTE (异环, gameId=1289) game-record models.

Field names mirror the wire format because the upstream game backend passes
them through verbatim. Enum-like fields (``elementType`` / ``groupType`` /
``quality`` / skill ``type``) are typed as ``str`` rather than ``Literal``
because pydantic rejects unknown literal values, which would break clients
the moment a new element/quality is introduced.

Rich-text strings inside skills (``<Title>``, ``<NumGreen>``, ``<Guang>``,
``<Italic>``, ``<Green2>``, …) are kept verbatim — clients can render or
strip them as they wish.
"""

from __future__ import annotations

from pydantic import Field

from taygedo.models._base import BbsBase

__all__ = [
    "NteAchieveProgress",
    "NteArea",
    "NteAreaDetail",
    "NteAreaSummary",
    "NteCharacter",
    "NteCharacterSummary",
    "NteCitySkill",
    "NteFork",
    "NteFurniture",
    "NteHouse",
    "NteProperty",
    "NteRealestateData",
    "NteRealestateShow",
    "NteRoleHome",
    "NteSignReward",
    "NteSignState",
    "NteSkill",
    "NteSkillItem",
    "NteSuit",
    "NteTeamRecommend",
    "NteVehicle",
    "NteVehicleData",
    "NteVehicleShow",
]


# ---------- shared atomic value objects --------------------------------------


class NteCharacterSummary(BbsBase):
    """Compact character entry shown on the role-home avatar list."""

    id: str
    name: str
    quality: str = ""
    element_type: str = Field(alias="elementType", default="")
    group_type: str = Field(alias="groupType", default="")
    awaken_lev: int = Field(alias="awakenLev", default=0)
    awaken_effect: list[object] = Field(alias="awakenEffect", default_factory=list)


class NteRealestateShow(BbsBase):
    """``roleHome.realestate`` — currently displayed house slot."""

    show_id: str = Field(alias="showId", default="")
    show_name: str = Field(alias="showName", default="")
    total: int = 0


class NteVehicleShow(BbsBase):
    """``roleHome.vehicle`` — currently displayed vehicle slot."""

    show_id: str = Field(alias="showId", default="")
    show_name: str = Field(alias="showName", default="")
    total: int = 0


class NteAreaSummary(BbsBase):
    """``roleHome.areaProgress[*]`` — coarse total per area."""

    id: str
    name: str
    total: int = 0


class NteAchieveProgress(BbsBase):
    total: int = 0


class NteRoleHome(BbsBase):
    """``GET /apihub/awapi/yh/roleHome`` payload."""

    roleid: str
    rolename: str
    userid: str
    serverid: str = ""
    servername: str = ""
    avatar: str = ""
    lev: int = 0
    tycoon_level: int = Field(alias="tycoonLevel", default=0)
    worldlevel: int = 0
    rolelogin_days: int = Field(alias="roleloginDays", default=0)
    charid_cnt: int = Field(alias="charidCnt", default=0)
    achieve_progress: NteAchieveProgress = Field(
        alias="achieveProgress", default_factory=NteAchieveProgress,
    )
    area_progress: list[NteAreaSummary] = Field(
        alias="areaProgress", default_factory=list,
    )
    characters: list[NteCharacterSummary] = Field(default_factory=list)
    realestate: NteRealestateShow = Field(default_factory=NteRealestateShow)
    vehicle: NteVehicleShow = Field(default_factory=NteVehicleShow)


# ---------- characters (full) ------------------------------------------------


class NteProperty(BbsBase):
    """One property entry (HP / ATK / DEF / element resists / …).

    ``value`` is wire-string (may include ``%`` suffix); preserve as-is.
    """

    id: str
    name: str
    value: str = ""


class NteSkillItem(BbsBase):
    """A descriptive bullet within a skill — title is optional flavor text."""

    title: str = ""
    desc: str = ""


class NteSkill(BbsBase):
    """A character skill (``Proactive`` / ``Passive`` / ``City``)."""

    id: str
    name: str
    level: int = 0
    type: str = ""
    items: list[NteSkillItem] = Field(default_factory=list)


class NteCitySkill(BbsBase):
    """A city/social ability — same shape as NteSkill but typed separately."""

    id: str
    name: str
    level: int = 0
    type: str = ""
    items: list[NteSkillItem] = Field(default_factory=list)


class NteFork(BbsBase):
    """Resonance branch (second weapon line); fields are blank when unlocked."""

    id: str = ""
    alev: str = ""
    blev: str = ""
    slev: str = ""
    properties: list[NteProperty] = Field(default_factory=list)


class NteSuit(BbsBase):
    """Equipment-set activation summary."""

    suit_activate_num: int = Field(alias="suitActivateNum", default=0)


class NteCharacter(BbsBase):
    """Full character record from ``GET /apihub/awapi/yh/characters``."""

    id: str
    name: str
    quality: str = ""
    element_type: str = Field(alias="elementType", default="")
    group_type: str = Field(alias="groupType", default="")
    awaken_lev: int = Field(alias="awakenLev", default=0)
    awaken_effect: list[object] = Field(alias="awakenEffect", default_factory=list)
    properties: list[NteProperty] = Field(default_factory=list)
    skills: list[NteSkill] = Field(default_factory=list)
    city_skills: list[NteCitySkill] = Field(alias="citySkills", default_factory=list)
    fork: NteFork = Field(default_factory=NteFork)
    suit: NteSuit = Field(default_factory=NteSuit)


# ---------- realestate ------------------------------------------------------


class NteFurniture(BbsBase):
    id: str
    name: str
    own: bool = False


class NteHouse(BbsBase):
    id: str
    name: str
    own: bool = False
    fdetail: list[NteFurniture] = Field(default_factory=list)


class NteRealestateData(BbsBase):
    """``GET /apihub/awapi/yh/realestate`` payload."""

    total: int = 0
    detail: list[NteHouse] = Field(default_factory=list)


# ---------- vehicles --------------------------------------------------------


class NteVehicle(BbsBase):
    id: str
    name: str
    own: bool = False


class NteVehicleData(BbsBase):
    """``GET /apihub/awapi/yh/vehicles`` payload."""

    total: int = 0
    show_id: str = Field(alias="showId", default="")
    show_name: str = Field(alias="showName", default="")
    detail: list[NteVehicle] = Field(default_factory=list)


# ---------- area progress (full) --------------------------------------------


class NteAreaDetail(BbsBase):
    """One sub-task type within an area (e.g. callbox / yushi / branch)."""

    id: str
    name: str
    total: int = 0


class NteArea(BbsBase):
    """One area in ``GET /apihub/awapi/yh/areaProgress``."""

    id: str
    name: str
    total: int = 0
    detail: list[NteAreaDetail] = Field(default_factory=list)


# ---------- monthly sign-in -------------------------------------------------


class NteSignReward(BbsBase):
    """One day's reward in ``GET /apihub/awapi/sign/rewards``."""

    icon: str = ""
    name: str = ""
    num: int = 0


class NteSignState(BbsBase):
    """``GET /apihub/awapi/signin/state`` payload."""

    month: int = 0
    day: int = 0
    days: int = 0
    today_sign: bool = Field(alias="todaySign", default=False)
    re_sign_cnt: int = Field(alias="reSignCnt", default=0)


# ---------- team recommendations -------------------------------------------


class NteTeamRecommend(BbsBase):
    """One row in ``GET /apihub/awapi/yh/team`` — a recommended team build."""

    id: str
    name: str
    icon: str = ""
    desc: str = ""
    imgs: list[str] = Field(default_factory=list)
