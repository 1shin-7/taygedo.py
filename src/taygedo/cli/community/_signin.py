"""App-side BBS community sign-in (NOT the in-game sign-in)."""

from __future__ import annotations

import click
from rich.console import Console

from taygedo.cli._options import cid_option, json_option, uid_option
from taygedo.cli._render import render
from taygedo.cli._shared import async_command, flush_session, load_client
from taygedo.services import SigninRequest


@click.command()
@cid_option
@uid_option
@json_option
@async_command
async def signin(community_id: int, uid: int | None, json_out: bool) -> None:
    """Check in to a community today (rewards: exp + goldCoin)."""
    client, account = load_client(uid=uid)
    console = Console()
    async with client:
        state_env = await client.community.get_sign_state(community_id=community_id)
        already = bool(state_env.data)
        if already:
            flush_session(client, account)
            if json_out:
                render({"already_signed": True}, json_out=True)
                return
            console.print("✓ 今日已签到")
            return
        env = await client.community.signin(
            body=SigninRequest.model_validate({"communityId": community_id}),
        )
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "signin failed")
    if json_out:
        render(env.data, json_out=True)
        return
    console.print(
        f"✓ 社区签到成功 — exp +[bold]{env.data.exp}[/bold] "
        f"coin +[bold]{env.data.gold_coin}[/bold]",
    )


@click.command(name="sign-state")
@cid_option
@uid_option
@json_option
@async_command
async def sign_state(community_id: int, uid: int | None, json_out: bool) -> None:
    """Check whether today's community signin has already been claimed."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.community.get_sign_state(community_id=community_id)
        flush_session(client, account)
    render({"signed_today": bool(env.data)}, json_out=bool(json_out))
    if not json_out:
        Console().print("✓ 已签到" if env.data else "✗ 未签到")
