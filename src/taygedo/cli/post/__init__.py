"""``taygedo post`` — view, comment, like, collect, create."""

from __future__ import annotations

import click

from taygedo.cli.post import _actions, _create, _read

__all__ = ["post_group"]


@click.group(name="post")
def post_group() -> None:
    """Post detail / comments / like / collect / create."""


post_group.add_command(_read.show)
post_group.add_command(_read.comments)
post_group.add_command(_read.perm)
post_group.add_command(_actions.like)
post_group.add_command(_actions.collect)
post_group.add_command(_actions.comment)
post_group.add_command(_create.create)
