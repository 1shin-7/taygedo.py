"""tagedo command-line entry point.

Concrete subcommands will live alongside the matching ``services/<name>.py``
modules and be wired into ``app`` here as they are added.
"""

from __future__ import annotations

import click

__all__ = ["app"]


@click.group()
@click.version_option(package_name="tagedo")
def app() -> None:
    """tagedo — bbs-api.tajiduo.com client."""
