"""URL builders for NTE static assets on ``webstatic.tajiduo.com``.

Pure string composition — no network, no auth, no dependencies. Use these
when a downstream pipeline (PIL / Playwright / browser) needs the canonical
URL for a character portrait, area map, furniture icon, etc.

Path templates are derived from the SPA bundle paths observed in HAR.
"""

from __future__ import annotations

CDN = "https://webstatic.tajiduo.com"
_CHAR_BASE = f"{CDN}/bbs/yh-game-records-web-source"

__all__ = [
    "CDN",
    "area_small",
    "area_type",
    "area_wide",
    "character_city_skill",
    "character_detail",
    "character_element",
    "character_group",
    "character_property",
    "character_skill",
    "character_tall",
    "realestate_detail",
    "realestate_furniture",
    "vehicle_wide",
]


def character_tall(character_id: str) -> str:
    """Full-body portrait — ``character.id`` (e.g. ``1051``)."""
    return f"{_CHAR_BASE}/character/tall/{character_id}.PNG"


def character_detail(character_id: str) -> str:
    return f"{_CHAR_BASE}/character/detail/{character_id}.png"


def character_element(element_type: str) -> str:
    """``element_type`` is a ``CHARACTER_ELEMENT_TYPE_*`` literal."""
    return f"{_CHAR_BASE}/character/element/{element_type}.PNG"


def character_group(group_type: str) -> str:
    """``group_type`` is a ``CHARACTER_GROUP_TYPE_*`` literal."""
    return f"{_CHAR_BASE}/character/group/{group_type}.PNG"


def character_property(property_id: str) -> str:
    """E.g. ``hpmax``, ``atk``, ``crit``, ``damageupcosmos``."""
    return f"{_CHAR_BASE}/character/property/{property_id}.png"


def character_skill(skill_id: str) -> str:
    """E.g. ``ga_female051_melee``."""
    return f"{_CHAR_BASE}/character/skill/{skill_id}.png"


def character_city_skill(city_skill_id: str) -> str:
    """E.g. ``city_ability_palyer_01``."""
    return f"{_CHAR_BASE}/character/city_skill/{city_skill_id}.png"


def realestate_detail(house_id: str) -> str:
    """E.g. ``bigword_l_1``."""
    return f"{_CHAR_BASE}/realestate/detail/{house_id}.png"


def realestate_furniture(furniture_id: str) -> str:
    """E.g. ``SF_0001``."""
    return f"{_CHAR_BASE}/realestate/fdetail/{furniture_id}.png"


def vehicle_wide(vehicle_id: str) -> str:
    """E.g. ``vehicle008``. NOTE: upstream directory is ``verhicle`` (typo)."""
    return f"{_CHAR_BASE}/verhicle/wide/{vehicle_id}.png"


def area_wide(area_id: str) -> str:
    """E.g. ``001`` (桥间地). Wide cover image."""
    return f"{_CHAR_BASE}/area/wide/{area_id}.png"


def area_small(area_id: str) -> str:
    return f"{_CHAR_BASE}/area/small/{area_id}.png"


def area_type(type_id: str) -> str:
    """E.g. ``callbox``, ``yushi``, ``branch``."""
    return f"{_CHAR_BASE}/area/type/{type_id}.PNG"
