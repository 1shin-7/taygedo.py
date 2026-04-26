"""Tower of Fantasy role record sub-views."""

from __future__ import annotations

import click

from taygedo.cli._options import json_option, role_id_option, uid_option
from taygedo.cli._render import render
from taygedo.cli._shared import async_command
from taygedo.cli.ht._helpers import fetch_record


@click.command()
@uid_option
@role_id_option
@json_option
@async_command
async def info(uid: int | None, role_id: int | None, json_out: bool) -> None:
    """Headline numbers (level / power / achievements)."""
    rec = await fetch_record(uid, role_id)
    if json_out:
        render(
            {
                "roleid": rec.roleid,
                "rolename": rec.rolename,
                "lev": rec.lev,
                "shengelev": rec.shengelev,
                "maxgs": rec.maxgs,
                "achievementpointall": rec.achievementpointall,
                "imitationCount": rec.imitation_count,
                "artifactcount": rec.artifactcount,
                "bigsecretround": rec.bigsecretround,
                "endlessidolumtotalscore": rec.endlessidolumtotalscore,
            },
            json_out=True,
        )
        return
    rec_slim = rec.model_copy(
        update={
            "weaponinfo": [],
            "imitationlist": [],
            "mountlist": [],
            "dressfashionlist": [],
        },
    )
    render(rec_slim, json_out=False)


@click.command()
@uid_option
@role_id_option
@json_option
@async_command
async def record(uid: int | None, role_id: int | None, json_out: bool) -> None:
    """Full role record."""
    rec = await fetch_record(uid, role_id)
    render(rec, json_out=json_out)


@click.command()
@uid_option
@role_id_option
@json_option
@async_command
async def weapon(uid: int | None, role_id: int | None, json_out: bool) -> None:
    """Equipped weapons + matrix levels."""
    rec = await fetch_record(uid, role_id)
    render(rec.weaponinfo, json_out=json_out)


@click.command()
@uid_option
@role_id_option
@json_option
@async_command
async def imitation(uid: int | None, role_id: int | None, json_out: bool) -> None:
    """Imitations (拟态)."""
    rec = await fetch_record(uid, role_id)
    render(rec.imitationlist, json_out=json_out)


@click.command()
@uid_option
@role_id_option
@json_option
@async_command
async def mount(uid: int | None, role_id: int | None, json_out: bool) -> None:
    """Mounts (坐骑)."""
    rec = await fetch_record(uid, role_id)
    render(rec.mountlist, json_out=json_out)


@click.command()
@uid_option
@role_id_option
@json_option
@async_command
async def fashion(uid: int | None, role_id: int | None, json_out: bool) -> None:
    """Dress fashion (时装)."""
    rec = await fetch_record(uid, role_id)
    render(rec.dressfashionlist, json_out=json_out)
