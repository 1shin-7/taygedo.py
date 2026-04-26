"""``taygedo community`` — BBS listings, signin, tasks, shop.

Commands are split per business domain into ``_*`` modules; this ``__init__``
just registers them onto the click group.
"""

from __future__ import annotations

import click

from taygedo.cli.community import _bootstrap, _feeds, _shop, _signin, _tasks

__all__ = ["community_group"]


@click.group(name="community")
def community_group() -> None:
    """BBS community: listings, signin, tasks, shop."""


# Listings + bootstrap
community_group.add_command(_bootstrap.list_all)
community_group.add_command(_bootstrap.home)
community_group.add_command(_bootstrap.column)
community_group.add_command(_bootstrap.all_columns)
community_group.add_command(_bootstrap.startup)

# Discovery feeds
community_group.add_command(_feeds.recommend)
community_group.add_command(_feeds.official)
community_group.add_command(_feeds.topics)

# Signin
community_group.add_command(_signin.signin)
community_group.add_command(_signin.sign_state)

# Tasks / exp / coins
community_group.add_command(_tasks.tasks)
community_group.add_command(_tasks.exp)
community_group.add_command(_tasks.coins)

# Shop
community_group.add_command(_shop.shop)
