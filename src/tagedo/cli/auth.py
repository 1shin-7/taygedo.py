"""``tagedo auth`` — login / logout / info / switch / list.

The login command supports two modes via the same flag set: pass
``--cellphone`` and ``--captcha`` for fully non-interactive use, or omit
either to drop into a prompt_toolkit interactive flow.
"""

from __future__ import annotations

from typing import Any

import click
from rich.console import Console

from ..client import TajiduoClient
from ..core import ApiError, ResponseValidationError
from ..device import AndroidDeviceProfile
from ..models import (
    CaptchaRequest,
    CheckCaptchaRequest,
    SmsLoginRequest,
)
from ._interactive import mask_cellphone, prompt_captcha, prompt_cellphone
from ._render import render
from ._shared import (
    async_command,
    flush_session,
    load_client,
    now_iso,
    require_account,
    storage,
)
from ._storage import StoredAccount

__all__ = ["auth_group"]


@click.group(name="auth")
def auth_group() -> None:
    """Account login and management."""


@auth_group.command()
@click.option("--cellphone", help="11-digit cellphone number; omit to prompt.")
@click.option("--captcha", help="6-digit SMS captcha; omit to prompt after sending.")
@click.option("--area-code-id", type=int, default=1, show_default=True)
@click.option("--json", "json_out", is_flag=True, help="Output as JSON.")
@async_command
async def login(
    cellphone: str | None,
    captcha: str | None,
    area_code_id: int,
    json_out: bool,
) -> None:
    """Send a captcha and complete an SMS login."""
    if captcha and not cellphone:
        raise click.UsageError("--captcha requires --cellphone")

    if not cellphone:
        cellphone = await prompt_cellphone()

    device = AndroidDeviceProfile.for_htassistant()
    client = TajiduoClient(device=device)
    console = Console()

    async with client:
        if not captcha:
            await client.login.send_captcha(
                body=CaptchaRequest.model_validate(
                    {"cellphone": cellphone, "areaCodeId": str(area_code_id)},
                ),
            )
            console.print(f"✓ 验证码已发送到 [cyan]{mask_cellphone(cellphone)}[/cyan]")
            captcha = await prompt_captcha()

        try:
            # The LaohuSDK App always calls /checkPhoneCaptchaWithOutLogin
            # before /sms/new/login. The check call marks the captcha as
            # verified server-side; without it the laohu token comes back
            # as a "soft" token and bbs-api refuses the exchange (code=22).
            await client.login.check_captcha(
                body=CheckCaptchaRequest(cellphone=cellphone, captcha=captcha),
            )
            sms_env = await client.login.sms_login(
                body=SmsLoginRequest.model_validate(
                    {
                        "cellphone": cellphone,
                        "captcha": captcha,
                        "areaCodeId": str(area_code_id),
                    },
                ),
            )
        except ApiError as exc:
            raise click.ClickException(f"登录失败: {exc.body}") from exc
        if sms_env.result is None:
            raise click.ClickException(f"登录失败: {sms_env.message or 'no result'}")

        bbs = await client.auth.login_with_laohu(sms_env.result)
        nickname = sms_env.result.nickname or sms_env.result.username or ""
        try:
            user_env = await client.user.get_user_full_info()
            if user_env.data is not None:
                nickname = user_env.data.user.nickname or nickname
        except (ApiError, ResponseValidationError):
            # Optional enrichment — keep going if the bbs profile call fails.
            pass

    account = StoredAccount(
        uid=bbs.uid,
        nickname=nickname,
        cellphone_masked=mask_cellphone(cellphone),
        access_token=bbs.access_token,
        refresh_token=bbs.refresh_token,
        laohu_token=sms_env.result.token,
        laohu_user_id=sms_env.result.user_id,
        device_id=device.device_id,
        logged_in_at=now_iso(),
        last_used_at=now_iso(),
    )
    storage().upsert_account(account, set_active=True)

    if json_out:
        render(account, json_out=True)
        return
    console.print(
        f"✓ 登录成功 — uid=[bold]{account.uid}[/bold] nickname=[bold]{account.nickname}[/bold] "
        f"phone=[cyan]{account.cellphone_masked}[/cyan]",
    )


@auth_group.command()
@click.option("--all", "all_", is_flag=True, help="Forget every stored account.")
@click.option("--uid", type=int, help="Forget the account with this uid.")
@click.option("--json", "json_out", is_flag=True)
def logout(all_: bool, uid: int | None, json_out: bool) -> None:
    """Forget a stored account."""
    if all_ and uid is not None:
        raise click.UsageError("--all and --uid are mutually exclusive")
    s = storage()

    removed: list[int]
    if all_:
        removed = [a.uid for a in s.list_accounts()]
        s.clear_accounts()
    else:
        target = uid if uid is not None else s.active_uid()
        if target is None:
            raise click.UsageError("no active account to log out")
        if s.get_account(target) is None:
            raise click.UsageError(f"no stored account with uid={target}")
        s.remove_account(target)
        removed = [target]

    if json_out:
        render({"removed": removed, "active_uid": s.active_uid()}, json_out=True)
        return
    console = Console()
    if not removed:
        console.print("没有可登出的账号")
    else:
        console.print(f"✓ 已登出: {', '.join(str(u) for u in removed)}")


@auth_group.command()
@click.option("--uid", type=int, help="Show this uid; default: active.")
@click.option("--json", "json_out", is_flag=True)
@async_command
async def info(uid: int | None, json_out: bool) -> None:
    """Show stored account + live UserFullInfo."""
    client, account = load_client(uid=uid)
    async with client:
        try:
            user_env = await client.user.get_user_full_info()
        except ApiError as exc:
            raise click.ClickException(f"获取用户信息失败: {exc.body}") from exc
        flush_session(client, account)
    if json_out:
        payload: dict[str, Any] = {
            "stored": account.to_dict(),
            "user": user_env.data.model_dump(mode="json") if user_env.data else None,
        }
        render(payload, json_out=True)
        return
    Console().print(
        f"[bold]uid[/bold]      : {account.uid}\n"
        f"[bold]nickname[/bold] : {account.nickname or '—'}\n"
        f"[bold]phone[/bold]    : {account.cellphone_masked or '—'}\n"
        f"[bold]device[/bold]   : {account.device_id}\n"
        f"[bold]logged in[/bold]: {account.logged_in_at}\n"
        f"[bold]last used[/bold]: {account.last_used_at}",
    )
    if user_env.data is not None:
        render(user_env.data, json_out=False)


@auth_group.command()
@click.argument("uid", type=int)
def switch(uid: int) -> None:
    """Set the active account."""
    s = storage()
    if s.get_account(uid) is None:
        raise click.UsageError(f"no stored account with uid={uid}")
    s.set_active(uid)
    Console().print(f"✓ active = {uid}")


@auth_group.command(name="list")
@click.option("--json", "json_out", is_flag=True)
def list_(json_out: bool) -> None:
    """List all stored accounts."""
    accounts = storage().list_accounts()
    if json_out:
        render([a.to_dict() for a in accounts], json_out=True)
        return
    if not accounts:
        Console().print("尚未登录任何账号 — `tagedo auth login`")
        return
    render(accounts, json_out=False)


# Required so that prompt_toolkit + lru_cache + flush_session round-trip
# play nicely with mypy strict — only used to keep the import non-redundant.
require_account  # noqa: B018  (referenced for re-export semantics in tests)
