"""Search renderers — topics, hot keywords, user search."""

from __future__ import annotations

from collections.abc import Callable

from rich.console import Console
from rich.table import Table

from taygedo.cli._render._helpers import truncate
from taygedo.models import HotWord, SearchTopicResult, SearchUsersPage, Topic


def _render_hot_words(words: list[HotWord], console: Console) -> None:
    t = Table(title="Hot keywords")
    t.add_column("keyword")
    t.add_column("count")
    for w in words:
        t.add_row(w.keyword, str(w.count))
    console.print(t)


def _render_topics(topics: list[Topic], console: Console) -> None:
    t = Table(title="Topics")
    t.add_column("id", style="cyan")
    t.add_column("topic")
    t.add_column("related")
    t.add_column("introduce")
    for tp in topics:
        t.add_row(
            str(tp.id),
            tp.topic,
            str(tp.related_num),
            truncate(tp.introduce, 50),
        )
    console.print(t)


def _render_search_topic_result(result: SearchTopicResult, console: Console) -> None:
    _render_topics(result.items, console)


def _render_search_users_page(page: SearchUsersPage, console: Console) -> None:
    # Reuse User-list renderer registered by _user.py.
    from taygedo.cli._render._user import _render_user_list as _ulist
    _ulist(page.items, console)


def register(
    single: dict[type, Callable[..., None]],
    listed: dict[type, Callable[..., None]],
) -> None:
    single[SearchTopicResult] = _render_search_topic_result
    single[SearchUsersPage] = _render_search_users_page
    listed[HotWord] = _render_hot_words
    listed[Topic] = _render_topics
