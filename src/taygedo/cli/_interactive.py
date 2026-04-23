"""Interactive prompts used by ``taygedo auth login``.

These are *async* because they're invoked from inside an asyncio loop
(via ``@async_command``); calling the sync ``prompt_toolkit.prompt`` from
inside a running loop raises ``RuntimeError: asyncio.run() cannot be
called from a running event loop``. ``PromptSession.prompt_async`` cooperates
with the existing loop instead.
"""

from __future__ import annotations

import re

from prompt_toolkit import PromptSession
from prompt_toolkit.validation import ValidationError, Validator

__all__ = ["mask_cellphone", "prompt_captcha", "prompt_cellphone"]


_CELLPHONE_RE = re.compile(r"^1\d{10}$")
_CAPTCHA_RE = re.compile(r"^\d{6}$")


class _CellphoneValidator(Validator):
    def validate(self, document: object) -> None:
        text = getattr(document, "text", "")
        if not _CELLPHONE_RE.fullmatch(text):
            raise ValidationError(
                message="手机号必须是 11 位、以 1 开头的数字",
                cursor_position=len(text),
            )


class _CaptchaValidator(Validator):
    def validate(self, document: object) -> None:
        text = getattr(document, "text", "")
        if not _CAPTCHA_RE.fullmatch(text):
            raise ValidationError(
                message="验证码必须是 6 位数字",
                cursor_position=len(text),
            )


async def prompt_cellphone() -> str:
    """Prompt for an 11-digit Chinese cellphone number."""
    session: PromptSession[str] = PromptSession()
    return await session.prompt_async(
        "请输入手机号: ",
        validator=_CellphoneValidator(),
        validate_while_typing=False,
    )


async def prompt_captcha() -> str:
    """Prompt for a 6-digit SMS captcha."""
    session: PromptSession[str] = PromptSession()
    return await session.prompt_async(
        "请输入验证码 (6 位数字): ",
        validator=_CaptchaValidator(),
        validate_while_typing=False,
    )


def mask_cellphone(cellphone: str) -> str:
    """``13800138000`` → ``138****8000`` for display + storage."""
    if len(cellphone) != 11:
        return cellphone
    return f"{cellphone[:3]}****{cellphone[7:]}"
