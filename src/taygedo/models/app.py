"""App-level configuration / startup payloads."""

from __future__ import annotations

import json

from pydantic import Field

from ._base import BbsBase

__all__ = [
    "AppConfig",
    "AppConfigs",
    "AppStartupData",
    "Emoticon",
    "EmoticonGroup",
    "ImConfigEntry",
]


class AppConfig(BbsBase):
    """``/apihub/api/getAppConfig`` payload."""

    env_id: str
    version: str


class ImConfigEntry(BbsBase):
    """One game's IM customer-service entry inside ``AppConfigs.im_config``."""

    game_id: str
    name: str
    path: str
    icon: str = ""


class AppConfigs(BbsBase):
    """The ``appConfigs`` block inside the startup payload."""

    min_version: str
    last_version: str
    customer_service: str = ""
    down_url: str = ""
    version_notice: str = ""
    im_config: str = ""
    """JSON-encoded list of :class:`ImConfigEntry`. Use :meth:`im_config_parsed`."""

    def im_config_parsed(self) -> list[ImConfigEntry]:
        if not self.im_config:
            return []
        try:
            raw = json.loads(self.im_config)
        except json.JSONDecodeError:
            return []
        if not isinstance(raw, list):
            return []
        return [ImConfigEntry.model_validate(d) for d in raw if isinstance(d, dict)]


class Emoticon(BbsBase):
    id: int
    icon: str
    static_icon: str = Field(alias="staticIcon", default="")
    name: str = ""
    state: int = 0


class EmoticonGroup(BbsBase):
    """Top-level entry of ``getAppStartupData.emoticons``."""

    id: int
    icon: str
    items: list[Emoticon] = Field(alias="list", default_factory=list)


class AppStartupData(BbsBase):
    """``/apihub/api/getAppStartupData`` payload."""

    app_configs: AppConfigs = Field(alias="appConfigs")
    emoticons: list[EmoticonGroup] = Field(default_factory=list)
