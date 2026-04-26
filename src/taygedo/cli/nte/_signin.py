"""异环 monthly sign-in command."""

from __future__ import annotations

import click
from rich.console import Console

from taygedo.cli._options import json_option, role_id_option, uid_option
from taygedo.cli._render import render
from taygedo.cli._shared import async_command, flush_session, load_client
from taygedo.cli.nte._helpers import resolve_role_id
from taygedo.core import ApiError


@click.command()
@uid_option
@role_id_option
@click.option(
    "--preview", is_flag=True,
    help="Show this month's reward pool + state without signing.",
)
@click.option(
    "--raw", is_flag=True,
    help="Dump the underlying server JSON instead of the formatted result.",
)
@json_option
@async_command
async def sign(
    uid: int | None,
    role_id: int | None,
    preview: bool,
    raw: bool,
    json_out: bool,
) -> None:
    """Submit today's monthly sign-in for the active role."""
    client, account = load_client(uid=uid)
    console = Console()
    async with client:
        rid = await resolve_role_id(client, role_id)
        state_env = await client.nte_sign.get_state()
        if state_env.data is None:
            raise click.ClickException(state_env.msg or "no signin state")
        state = state_env.data

        if preview:
            rewards_env = await client.nte_sign.get_rewards(role_id=rid)
            flush_session(client, account)
            if raw:
                render(
                    {
                        "state": state.model_dump(mode="json"),
                        "rewards": (
                            [r.model_dump(mode="json") for r in rewards_env.data]
                            if rewards_env.data
                            else []
                        ),
                    },
                    json_out=json_out,
                )
                return
            render(state, json_out=json_out)
            if rewards_env.data:
                render(rewards_env.data, json_out=json_out)
            return

        if state.today_sign:
            flush_session(client, account)
            if json_out or raw:
                render(
                    {"already_signed": True, "state": state.model_dump(mode="json")},
                    json_out=True,
                )
                return
            console.print(f"已签到 (累计 [bold]{state.days}[/bold] 天)")
            return

        try:
            sign_env = await client.nte_sign.sign_role(role_id=rid)
        except ApiError as exc:
            raise click.ClickException(f"签到失败: {exc.body}") from exc
        new_state_env = await client.nte_sign.get_state()
        new_state = new_state_env.data or state
        rewards_env = await client.nte_sign.get_rewards(role_id=rid)
        flush_session(client, account)

        today_idx = max(new_state.day - 1, 0)
        reward = (
            rewards_env.data[today_idx]
            if rewards_env.data and today_idx < len(rewards_env.data)
            else None
        )

        if raw:
            render(
                {
                    "sign": sign_env.model_dump(mode="json"),
                    "state": new_state.model_dump(mode="json"),
                    "today_reward": reward.model_dump(mode="json") if reward else None,
                },
                json_out=json_out or True,
            )
            return
        if json_out:
            render(
                {
                    "ok": sign_env.is_ok,
                    "days": new_state.days,
                    "today_reward": reward.model_dump(mode="json") if reward else None,
                },
                json_out=True,
            )
            return
        console.print(f"✓ 今日签到成功 (累计 [bold]{new_state.days}[/bold] 天)")
        if reward:
            console.print(f"🎁 [bold]{reward.name}[/bold] x{reward.num}")
