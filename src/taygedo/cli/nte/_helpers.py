"""Internal helpers shared across nte/ subcommands."""

from __future__ import annotations

import click

from taygedo.client import TaygedoClient


async def resolve_role_id(client: TaygedoClient, role_id: int | None) -> int:
    """If role_id is None, hit /yh/roleHome to discover it."""
    if role_id is not None:
        return role_id
    home = await client.nte.get_role_home()
    if home.data is None:
        raise click.ClickException("could not resolve role id from /yh/roleHome")
    return int(home.data.roleid)
