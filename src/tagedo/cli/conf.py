"""``tagedo conf`` — view + edit ``~/.config/taygedo/config.toml``."""

from __future__ import annotations

import os
import subprocess

import click
from rich.console import Console

from . import _storage
from ._render import render
from ._shared import storage

__all__ = ["conf_group"]


@click.group(name="conf")
def conf_group() -> None:
    """CLI configuration (config.toml)."""


@conf_group.command()
def show() -> None:
    """Print the current config.toml."""
    path = _storage.CONFIG_FILE
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    Console().print(text, markup=False, highlight=False)


@conf_group.command(name="set")
@click.argument("key")
@click.argument("value")
def set_(key: str, value: str) -> None:
    """Set a config key (dotted path).

    Values are coerced: ``true`` / ``false`` → bool, integers → int,
    everything else stays string.
    """
    coerced: object
    if value.lower() == "true":
        coerced = True
    elif value.lower() == "false":
        coerced = False
    else:
        try:
            coerced = int(value)
        except ValueError:
            coerced = value
    storage().set_config(key, coerced)
    Console().print(f"OK {key} = {coerced!r}")


@conf_group.command()
def path() -> None:
    """Print the on-disk paths used by tagedo."""
    render(
        {
            "config": str(_storage.CONFIG_FILE),
            "data": str(_storage.DATA_FILE),
        },
        json_out=False,
    )


@conf_group.command()
def edit() -> None:
    """Open config.toml in $EDITOR (or $VISUAL)."""
    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR") or "nano"
    storage().load_config()
    subprocess.call([editor, str(_storage.CONFIG_FILE)])
