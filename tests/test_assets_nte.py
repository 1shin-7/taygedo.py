"""URL builders are pure string composition; lock down the exact templates."""

from __future__ import annotations

from taygedo.assets import nte


def test_character_tall_uses_PNG_extension() -> None:
    assert nte.character_tall("1051") == (
        "https://webstatic.tajiduo.com/bbs/yh-game-records-web-source/character/tall/1051.PNG"
    )


def test_character_detail_uses_lower_png() -> None:
    assert nte.character_detail("1051").endswith("/character/detail/1051.png")


def test_character_element_path() -> None:
    assert nte.character_element("CHARACTER_ELEMENT_TYPE_COSMOS").endswith(
        "/character/element/CHARACTER_ELEMENT_TYPE_COSMOS.PNG",
    )


def test_character_group_path() -> None:
    assert nte.character_group("CHARACTER_GROUP_TYPE_ONE").endswith(
        "/character/group/CHARACTER_GROUP_TYPE_ONE.PNG",
    )


def test_character_property_path() -> None:
    assert nte.character_property("hpmax").endswith("/character/property/hpmax.png")


def test_character_skill_path() -> None:
    assert nte.character_skill("ga_female051_melee").endswith(
        "/character/skill/ga_female051_melee.png",
    )


def test_character_city_skill_path() -> None:
    assert nte.character_city_skill("city_ability_palyer_01").endswith(
        "/character/city_skill/city_ability_palyer_01.png",
    )


def test_realestate_detail_path() -> None:
    assert nte.realestate_detail("bigword_l_1").endswith(
        "/realestate/detail/bigword_l_1.png",
    )


def test_realestate_furniture_path() -> None:
    assert nte.realestate_furniture("SF_0001").endswith(
        "/realestate/fdetail/SF_0001.png",
    )


def test_vehicle_wide_uses_upstream_typo_directory() -> None:
    """``verhicle`` (not ``vehicle``) is intentional — upstream typo."""
    url = nte.vehicle_wide("vehicle008")
    assert "/verhicle/wide/vehicle008.png" in url
    assert "/vehicle/wide/" not in url


def test_area_wide_path() -> None:
    assert nte.area_wide("001").endswith("/area/wide/001.png")


def test_area_small_path() -> None:
    assert nte.area_small("001").endswith("/area/small/001.png")


def test_area_type_path() -> None:
    assert nte.area_type("callbox").endswith("/area/type/callbox.PNG")
