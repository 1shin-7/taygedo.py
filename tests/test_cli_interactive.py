"""prompt_toolkit validators reject malformed input cleanly."""

from __future__ import annotations

import pytest
from prompt_toolkit.validation import ValidationError

from tagedo.cli._interactive import _CaptchaValidator, _CellphoneValidator, mask_cellphone


class _Doc:
    def __init__(self, text: str) -> None:
        self.text = text


def test_cellphone_valid_passes() -> None:
    _CellphoneValidator().validate(_Doc("13800138000"))


def test_cellphone_too_short_rejected() -> None:
    with pytest.raises(ValidationError):
        _CellphoneValidator().validate(_Doc("1380013800"))


def test_cellphone_doesnt_start_with_1_rejected() -> None:
    with pytest.raises(ValidationError):
        _CellphoneValidator().validate(_Doc("23800138000"))


def test_cellphone_non_digits_rejected() -> None:
    with pytest.raises(ValidationError):
        _CellphoneValidator().validate(_Doc("1380013800x"))


def test_captcha_six_digits_passes() -> None:
    _CaptchaValidator().validate(_Doc("123456"))


def test_captcha_five_digits_rejected() -> None:
    with pytest.raises(ValidationError):
        _CaptchaValidator().validate(_Doc("12345"))


def test_captcha_alpha_rejected() -> None:
    with pytest.raises(ValidationError):
        _CaptchaValidator().validate(_Doc("12345a"))


def test_mask_cellphone_keeps_first_three_and_last_four() -> None:
    assert mask_cellphone("13800138000") == "138****8000"


def test_mask_cellphone_leaves_short_strings_alone() -> None:
    assert mask_cellphone("123") == "123"
