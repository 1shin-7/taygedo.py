"""Read-side post commands — show, comments, perm check."""

from __future__ import annotations

import click

from taygedo.cli._options import json_option, uid_option
from taygedo.cli._render import render
from taygedo.cli._shared import async_command, flush_session, load_client


@click.command()
@click.argument("post_id", type=int)
@uid_option
@json_option
@async_command
async def show(post_id: int, uid: int | None, json_out: bool) -> None:
    """Fetch a post (full content + author + counters)."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.post.get_post(post_id=post_id)
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "post not found")
    render(env.data, json_out=json_out)


@click.command()
@click.argument("post_id", type=int)
@click.option(
    "--sort", "sort_type", type=int, default=2, show_default=True,
    help="1 = oldest first, 2 = hot.",
)
@click.option("--owner", is_flag=True, help="Owner-side view.")
@click.option("--count", type=int, default=20, show_default=True)
@uid_option
@json_option
@async_command
async def comments(
    post_id: int,
    sort_type: int,
    owner: bool,
    count: int,
    uid: int | None,
    json_out: bool,
) -> None:
    """List comments on a post."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.post.get_comments(
            post_id=post_id, sort_type=sort_type, owner=owner, count=count,
        )
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no comments")
    render(env.data, json_out=json_out)


@click.command()
@click.argument("element")
@uid_option
@json_option
@async_command
async def perm(element: str, uid: int | None, json_out: bool) -> None:
    """Check whether the user can publish a given content element (e.g. ``tp-video``)."""
    from rich.console import Console

    client, account = load_client(uid=uid)
    async with client:
        env = await client.post.publish_element_perm(element=element)
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "no permission data")
    if json_out:
        render(env.data, json_out=True)
        return
    p = env.data
    mark = "✓" if p.can_publish else "✗"
    Console().print(f"{mark} element=[bold]{element}[/bold]: {p.prompt or 'allowed'}")
