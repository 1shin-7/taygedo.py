"""taygedo command-line entry point.

``ht``/``tof`` and ``nte``/``yh`` are aliased — the English acronym and the
Pinyin both work. Pass ``--debug`` (or set ``TAGEDO_DEBUG=1``) to dump every
HTTP request/response to stderr.
"""

from __future__ import annotations

import os

import click

from .auth import auth_group
from .community import community_group
from .conf import conf_group
from .ht import ht_group
from .nte import nte_group
from .post import post_group
from .search import search_group
from .user import user_group

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
app.add_command(community_group, name="community")
app.add_command(conf_group, name="conf")
app.add_command(ht_group, name="ht")
app.add_command(ht_group, name="tof")
app.add_command(nte_group, name="nte")
app.add_command(nte_group, name="yh")
app.add_command(post_group, name="post")
app.add_command(search_group, name="search")
app.add_command(user_group, name="user")
