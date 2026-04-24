"""``taygedo post`` — view, comment, like, collect a post."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import click
from rich.console import Console

from ..models import AddCommentRequest
from ._render import render
from ._shared import async_command, flush_session, load_client

__all__ = ["post_group"]


def _uid_option(f: Callable[..., Any]) -> Callable[..., Any]:
    return click.option(
        "--uid", type=int, help="Use this account instead of the active one.",
    )(f)


def _json_option(f: Callable[..., Any]) -> Callable[..., Any]:
    return click.option("--json", "json_out", is_flag=True, help="Output as JSON.")(f)


@click.group(name="post")
def post_group() -> None:
    """Post detail / comments / like / collect / comment."""


@post_group.command()
@click.argument("post_id", type=int)
@_uid_option
@_json_option
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


@post_group.command()
@click.argument("post_id", type=int)
@click.option(
    "--sort", "sort_type", type=int, default=2, show_default=True,
    help="1 = oldest first, 2 = hot.",
)
@click.option("--owner", is_flag=True, help="Owner-side view.")
@click.option("--count", type=int, default=20, show_default=True)
@_uid_option
@_json_option
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


@post_group.command()
@click.argument("post_id", type=int)
@_uid_option
@_json_option
@async_command
async def like(post_id: int, uid: int | None, json_out: bool) -> None:
    """Like a post."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.post.like(post_id=post_id)
        flush_session(client, account)
    if json_out:
        render({"ok": env.is_ok, "post_id": post_id}, json_out=True)
        return
    Console().print(f"✓ liked post {post_id}" if env.is_ok else f"✗ failed: {env.msg}")


@post_group.command()
@click.argument("post_id", type=int)
@_uid_option
@_json_option
@async_command
async def collect(post_id: int, uid: int | None, json_out: bool) -> None:
    """Collect (bookmark) a post."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.post.collect(post_id=post_id)
        flush_session(client, account)
    if json_out:
        render({"ok": env.is_ok, "post_id": post_id}, json_out=True)
        return
    Console().print(
        f"✓ collected post {post_id}" if env.is_ok else f"✗ failed: {env.msg}",
    )


@post_group.command()
@click.argument("post_id", type=int)
@click.argument("content")
@click.option("--parent", "parent_id", type=int, default=0, help="Reply to a comment.")
@click.option("--reply-uid", type=int, default=0, help="Target uid (when --parent set).")
@_uid_option
@_json_option
@async_command
async def comment(
    post_id: int,
    content: str,
    parent_id: int,
    reply_uid: int,
    uid: int | None,
    json_out: bool,
) -> None:
    """Post a comment (or a reply via --parent)."""
    client, account = load_client(uid=uid)
    async with client:
        env = await client.post.add_comment(
            body=AddCommentRequest.model_validate(
                {
                    "postId": post_id,
                    "content": content,
                    "parentId": parent_id,
                    "replyUid": reply_uid,
                },
            ),
        )
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "comment failed")
    if json_out:
        render(env.data, json_out=True)
        return
    Console().print(
        f"✓ comment posted (id=[bold]{env.data.comment.id}[/bold])",
    )
