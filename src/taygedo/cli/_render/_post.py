"""Post / comment / cursor-page renderers."""

from __future__ import annotations

from collections.abc import Callable

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from taygedo.cli._render._helpers import kv_table, truncate
from taygedo.models import (
    Comment,
    CommentPage,
    CursorPage,
    Post,
    PostFull,
    Reply,
    ReplyFeedPage,
)


def _render_post(post: Post, console: Console) -> None:
    console.print(
        kv_table(
            f"Post #{post.post_id}",
            [
                ("subject", post.subject),
                ("uid", post.uid),
                ("community", post.community_id),
                ("column", post.column_id),
                ("type", post.type),
                ("likes", post.post_stat.like_num),
                ("comments", post.post_stat.comment_num),
                ("collects", post.post_stat.collect_num),
                ("region", post.region or "—"),
                ("created", post.create_time),
            ],
        ),
    )
    if post.content:
        console.print(Panel(Text(truncate(post.content, 400)), title="content"))


def _render_post_full(value: PostFull, console: Console) -> None:
    _render_post(value.post, console)
    if value.users:
        author = value.users[0]
        console.print(
            kv_table(
                "author",
                [
                    ("uid", author.uid),
                    ("nickname", author.nickname),
                    ("ipRegion", author.ip_region),
                ],
            ),
        )


def _render_cursor_page_of_posts(page: CursorPage[Post], console: Console) -> None:
    t = Table(title=f"Posts (page={page.page} hasMore={page.has_more})")
    t.add_column("id", style="cyan")
    t.add_column("subject")
    t.add_column("uid")
    t.add_column("likes")
    t.add_column("comments")
    for p in page.items:
        t.add_row(
            str(p.post_id),
            truncate(p.subject, 50),
            str(p.uid),
            str(p.post_stat.like_num),
            str(p.post_stat.comment_num),
        )
    console.print(t)


def _render_reply_feed_page(page: ReplyFeedPage[Reply], console: Console) -> None:
    t = Table(title=f"Reply feed (more={page.more})")
    t.add_column("reply_id")
    t.add_column("post_id")
    t.add_column("uid")
    t.add_column("content")
    for r in page.items:
        t.add_row(
            str(r.reply_id or "—"),
            str(r.post_id or "—"),
            str(r.uid or "—"),
            truncate(r.content, 50),
        )
    console.print(t)


def _render_comment_page(page: CommentPage, console: Console) -> None:
    names = {u.uid: u.nickname for u in page.users}
    t = Table(title=f"Comments (page={page.page} hasMore={page.has_more})")
    t.add_column("id", style="cyan")
    t.add_column("uid")
    t.add_column("author")
    t.add_column("likes")
    t.add_column("content")
    for c in page.comments:
        likes = c.comment_stat.like_num if c.comment_stat else 0
        t.add_row(
            str(c.id),
            str(c.uid),
            names.get(c.uid, "—"),
            str(likes),
            truncate(c.content, 50),
        )
    console.print(t)


def _render_comments(items: list[Comment], console: Console) -> None:
    t = Table(title="Comments")
    t.add_column("id", style="cyan")
    t.add_column("uid")
    t.add_column("content")
    for c in items:
        t.add_row(str(c.id), str(c.uid), truncate(c.content, 60))
    console.print(t)


def register(
    single: dict[type, Callable[..., None]],
    listed: dict[type, Callable[..., None]],
) -> None:
    single[PostFull] = _render_post_full
    single[Post] = _render_post
    single[CommentPage] = _render_comment_page
    single[CursorPage] = _render_cursor_page_of_posts
    single[ReplyFeedPage] = _render_reply_feed_page
    listed[Comment] = _render_comments
