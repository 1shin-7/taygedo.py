"""Engagement actions on posts — like, collect, comment."""

from __future__ import annotations

import click
from rich.console import Console

from taygedo.cli._options import json_option, uid_option
from taygedo.cli._render import render
from taygedo.cli._shared import async_command, flush_session, load_client
from taygedo.models import AddCommentRequest


@click.command()
@click.argument("post_id", type=int)
@uid_option
@json_option
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


@click.command()
@click.argument("post_id", type=int)
@uid_option
@json_option
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


@click.command()
@click.argument("post_id", type=int)
@click.argument("content")
@click.option("--parent", "parent_id", type=int, default=0, help="Reply to a comment.")
@click.option("--reply-uid", type=int, default=0, help="Target uid (when --parent set).")
@uid_option
@json_option
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
