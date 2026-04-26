"""``taygedo nte`` (alias ``taygedo yh``) — 异环 game queries + sign-in + recommend."""

from __future__ import annotations

import click

from taygedo.cli.nte import _assets, _recommend, _role, _signin

__all__ = ["nte_group"]


@click.group(name="nte")
def nte_group() -> None:
    """异环 (gameId=1289) data + monthly sign-in."""


# Role
nte_group.add_command(_role.info)
nte_group.add_command(_role.character)

# Collectibles + meta
nte_group.add_command(_assets.realestate)
nte_group.add_command(_assets.vehicle)
nte_group.add_command(_assets.area)
nte_group.add_command(_assets.team)
nte_group.add_command(_assets.cards)

# Signin
nte_group.add_command(_signin.sign)

# Recommend (moved from `community game-recommend`)
nte_group.add_command(_recommend.recommend)
