"""``taygedo user`` — profile, feeds, follow/unfollow."""

from __future__ import annotations

import click

from taygedo.cli.user import _feeds, _profile, _social

__all__ = ["user_group"]


@click.group(name="user")
def user_group() -> None:
    """User profile, feeds, follow."""


# Profile
user_group.add_command(_profile.me)
user_group.add_command(_profile.nickname)
user_group.add_command(_profile.avatar)
user_group.add_command(_profile.avatars)

# Feeds
user_group.add_command(_feeds.posts)
user_group.add_command(_feeds.browse)
user_group.add_command(_feeds.collects)
user_group.add_command(_feeds.replies)
user_group.add_command(_feeds.exp)

# Social
user_group.add_command(_social.follow)
user_group.add_command(_social.unfollow)
user_group.add_command(_social.follows)
