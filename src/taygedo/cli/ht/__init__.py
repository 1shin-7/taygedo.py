"""``taygedo ht`` (alias ``taygedo tof``) — 幻塔 game record + sign + recommend."""

from __future__ import annotations

import click

from taygedo.cli.ht import _recommend, _record, _signin

__all__ = ["ht_group"]


@click.group(name="ht")
def ht_group() -> None:
    """Tower of Fantasy (gameId=1256) data."""


# Record sub-views
ht_group.add_command(_record.info)
ht_group.add_command(_record.record)
ht_group.add_command(_record.weapon)
ht_group.add_command(_record.imitation)
ht_group.add_command(_record.mount)
ht_group.add_command(_record.fashion)

# Signin
ht_group.add_command(_signin.sign)

# Recommend (moved from `community game-recommend`)
ht_group.add_command(_recommend.recommend)
