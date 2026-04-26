"""Post creation — ``POST /bbs/api/post`` with a Quill HTML body."""

from __future__ import annotations

import click
from rich.console import Console

from taygedo.cli._options import json_option, uid_option
from taygedo.cli._render import render
from taygedo.cli._shared import async_command, flush_session, load_client
from taygedo.models import CreatePostRequest


@click.command()
@click.argument("subject")
@click.argument("content")
@click.option(
    "-c", "--community", "community_id", type=int, default=2, show_default=True,
    help="Community ID (1 = 幻塔, 2 = 异环).",
)
@click.option(
    "--column-id", type=int, default=10, show_default=True,
    help="Column to post under (varies per community).",
)
@click.option(
    "--type", "post_type", type=int, default=1, show_default=True,
    help="1 = text/image, 3 = video.",
)
@click.option(
    "--topic-ids", type=str, default="",
    help="Comma-separated topic IDs (optional).",
)
@uid_option
@json_option
@async_command
async def create(
    subject: str,
    content: str,
    community_id: int,
    column_id: int,
    post_type: int,
    topic_ids: str,
    uid: int | None,
    json_out: bool,
) -> None:
    """Publish a new post.

    ``CONTENT`` is a Quill-style HTML string (image / divider / mention nodes
    are pre-built blocks). For plain-text posts, just pass ``"<p>your text</p>"``.
    """
    parsed_topic_ids = [int(x) for x in topic_ids.split(",") if x.strip()]
    client, account = load_client(uid=uid)
    async with client:
        env = await client.post.create(
            body=CreatePostRequest.model_validate(
                {
                    "type": post_type,
                    "communityId": community_id,
                    "columnId": column_id,
                    "subject": subject,
                    "content": content,
                    "topicIds": parsed_topic_ids,
                },
            ),
        )
        flush_session(client, account)
    if env.data is None:
        raise click.ClickException(env.msg or "post creation failed")
    if json_out:
        render(env.data, json_out=True)
        return
    Console().print(f"✓ post created (id=[bold]{env.data.post_id}[/bold])")
