"""taygedo command-line entry point.

The top-level ``app`` group bundles five sub-groups, two of which are
double-named for ergonomics:

* ``auth``                — login / logout / info / switch / list
* ``ht`` and ``tof``      — Tower of Fantasy queries (same handler)
* ``nte`` and ``yh``      — 异环 queries (same handler)
* ``conf``                — config.toml view + edit

Pass ``--debug`` (or set ``TAGEDO_DEBUG=1``) to dump every HTTP
request/response to stderr — useful when a server returns a non-zero
business code and you need to see the raw payload.
"""

from __future__ import annotations

import os

import click

from .auth import auth_group
from .conf import conf_group
from .ht import ht_group
from .nte import nte_group

__all__ = ["app"]


@click.group()
@click.version_option(package_name="taygedo")
@click.option(
    "--debug",
    is_flag=True,
    help="Print every HTTP request/response to stderr.",
)
def app(debug: bool) -> None:
    """taygedo — bbs-api.tajiduo.com client."""
    if debug:
        os.environ["TAGEDO_DEBUG"] = "1"


app.add_command(auth_group, name="auth")
app.add_command(conf_group, name="conf")
app.add_command(nte_group, name="nte")
app.add_command(nte_group, name="yh")
app.add_command(ht_group, name="ht")
app.add_command(ht_group, name="tof")
